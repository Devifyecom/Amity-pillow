/* IND storefront: behaviour for `ind-*` sections. Vanilla JS, no dependencies. */
(function () {
  if (window.__indLoaded) return;
  window.__indLoaded = true;

  const IND = window.IND || {};
  const define = (name, ctor) => { if (!customElements.get(name)) customElements.define(name, ctor); };
  const qs = (el, s) => el.querySelector(s);
  const qsa = (el, s) => Array.from(el.querySelectorAll(s));

  /* ---------- Money ---------- */
  const formatMoney = (cents, format) => {
    const fmt = format || IND.moneyFormat || '€{{amount}}';
    const value = (Number(cents) || 0) / 100;
    const delim = (num, dec, thou, decSep) => {
      const parts = num.toFixed(dec).split('.');
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thou);
      return parts.join(dec ? decSep : '');
    };
    return fmt.replace(/\{\{\s*(\w+)\s*\}\}/, (_, key) => {
      switch (key) {
        case 'amount_no_decimals': return delim(value, 0, ',', '.');
        case 'amount_with_comma_separator': return delim(value, 2, '.', ',');
        case 'amount_no_decimals_with_comma_separator': return delim(value, 0, '.', ',');
        case 'amount_with_apostrophe_separator': return delim(value, 2, "'", '.');
        case 'amount_with_space_separator': return delim(value, 2, ' ', ',');
        default: return delim(value, 2, ',', '.');
      }
    });
  };
  IND.formatMoney = formatMoney;

  /* ---------- Black Friday campaign state (re-checked client-side; pages may be cached) ---------- */
  const parseTime = (iso) => {
    const t = Date.parse(iso);
    return Number.isNaN(t) ? null : t;
  };
  const bfWindow = () => {
    const bf = IND.bf || {};
    return { start: parseTime(bf.start), end: parseTime(bf.end) };
  };
  const bfState = () => {
    const bf = IND.bf || {};
    if (!bf.enabled) return 'off';
    if (bf.preview && bf.designMode) return 'active';
    const { start, end } = bfWindow();
    if (start === null || end === null) return 'off';
    const now = Date.now();
    if (now < start) return 'upcoming';
    if (now > end) return 'ended';
    return 'active';
  };
  IND.bfState = bfState;

  const applyBfVisibility = () => {
    const state = bfState();
    document.documentElement.dataset.indBf = state;
    qsa(document, '[data-bf-show]').forEach((el) => {
      const wanted = el.dataset.bfShow.split(/\s+/);
      el.hidden = !wanted.includes(state);
    });
    document.dispatchEvent(new CustomEvent('ind:bf-state', { detail: { state } }));
  };
  IND.applyBfVisibility = applyBfVisibility;

  /* ---------- Countdown ---------- */
  define('ind-countdown', class extends HTMLElement {
    connectedCallback() {
      this.parts = {};
      qsa(this, '[data-cd]').forEach((el) => { this.parts[el.dataset.cd] = el; });
      this.tick = this.tick.bind(this);
      this.tick();
      this.timer = setInterval(this.tick, 1000);
    }
    disconnectedCallback() { clearInterval(this.timer); }
    tick() {
      const state = bfState();
      const { start, end } = bfWindow();
      const bf = IND.bf || {};
      let target = this.dataset.target === 'start' ? start : end;
      // Editor preview with dates in the future/past: count to end if still ahead, else hide.
      if (bf.preview && bf.designMode && this.dataset.target !== 'start') target = end;
      const wantState = this.dataset.target === 'start' ? 'upcoming' : 'active';
      const diff = target === null ? -1 : target - Date.now();
      if (state !== wantState || diff <= 0) {
        this.hidden = true;
        if (diff <= 0 && this._wasRunning) { this._wasRunning = false; applyBfVisibility(); }
        return;
      }
      this._wasRunning = true;
      this.hidden = false;
      const s = Math.floor(diff / 1000);
      const vals = {
        days: Math.floor(s / 86400),
        hours: Math.floor((s % 86400) / 3600),
        minutes: Math.floor((s % 3600) / 60),
        seconds: s % 60,
      };
      Object.keys(vals).forEach((k) => {
        if (this.parts[k]) this.parts[k].textContent = String(vals[k]).padStart(2, '0');
      });
      this.setAttribute('aria-label', `${vals.days} ${IND.strings.days}, ${vals.hours} ${IND.strings.hours}, ${vals.minutes} ${IND.strings.minutes}`);
    }
  });

  /* ---------- Announcement rotator ---------- */
  define('ind-announce', class extends HTMLElement {
    connectedCallback() {
      this.items = qsa(this, '.ind-announce__msg');
      if (this.items.length < 2) { this.items.forEach((i) => i.classList.add('is-active')); return; }
      this.i = 0;
      this.items[0].classList.add('is-active');
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      this.timer = setInterval(() => this.next(), (Number(this.dataset.speed) || 5) * 1000);
      this.addEventListener('mouseenter', () => clearInterval(this.timer));
    }
    disconnectedCallback() { clearInterval(this.timer); }
    next() {
      const visible = this.items.filter((el) => !el.hidden);
      if (visible.length < 2) return;
      const cur = visible.findIndex((el) => el.classList.contains('is-active'));
      visible.forEach((el) => el.classList.remove('is-active'));
      visible[(cur + 1) % visible.length].classList.add('is-active');
    }
  });

  /* ---------- Header: sticky state, drawer, search ---------- */
  define('ind-header', class extends HTMLElement {
    connectedCallback() {
      this.wrap = this.closest('.ind-header-wrap') || this;
      const onScroll = () => this.wrap.classList.toggle('is-scrolled', window.scrollY > 8);
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();

      qsa(this, '[data-open-dialog]').forEach((btn) => {
        btn.addEventListener('click', () => {
          const dlg = document.getElementById(btn.dataset.openDialog);
          if (!dlg) return;
          dlg.showModal();
          btn.setAttribute('aria-expanded', 'true');
          const focusEl = qs(dlg, '[autofocus], input');
          if (focusEl) setTimeout(() => focusEl.focus(), 30);
          dlg.addEventListener('close', () => btn.setAttribute('aria-expanded', 'false'), { once: true });
        });
      });
      qsa(this, 'dialog').forEach((dlg) => {
        dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
        qsa(dlg, '[data-close-dialog]').forEach((b) => b.addEventListener('click', () => dlg.close()));
      });

      const search = qs(this, '[data-search-input]');
      const results = qs(this, '[data-search-results]');
      if (search && results) {
        let t;
        search.addEventListener('input', () => {
          clearTimeout(t);
          const q = search.value.trim();
          if (q.length < 2) { results.innerHTML = ''; return; }
          t = setTimeout(() => this.suggest(q, results), 220);
        });
      }
    }
    async suggest(q, results) {
      try {
        const url = `${IND.root.replace(/\/$/, '')}/search/suggest.json?q=${encodeURIComponent(q)}&resources[type]=product&resources[limit]=6`;
        const res = await fetch(url);
        const data = await res.json();
        const products = (data.resources && data.resources.results && data.resources.results.products) || [];
        results.innerHTML = products.map((p) => {
          const img = p.image ? `<img src="${p.image}&width=120" alt="" loading="lazy" width="56" height="56">` : '<span style="width:56px;height:56px"></span>';
          return `<a class="ind-search__item" href="${p.url}">${img}<span><strong>${p.title}</strong><span class="ind-small">${formatMoney(Math.round(parseFloat(p.price) * 100))}</span></span></a>`;
        }).join('');
      } catch (e) { results.innerHTML = ''; }
    }
  });

  /* ---------- Accordion ---------- */
  define('ind-accordion', class extends HTMLElement {
    connectedCallback() {
      this.single = this.hasAttribute('data-single');
      qsa(this, '.ind-acc__q').forEach((btn) => {
        btn.addEventListener('click', () => {
          const open = btn.getAttribute('aria-expanded') !== 'true';
          if (this.single && open) {
            qsa(this, '.ind-acc__q[aria-expanded="true"]').forEach((b) => this.set(b, false));
          }
          this.set(btn, open);
        });
      });
    }
    set(btn, open) {
      btn.setAttribute('aria-expanded', String(open));
      const panel = document.getElementById(btn.getAttribute('aria-controls'));
      if (panel) { panel.classList.toggle('is-open', open); panel.setAttribute('aria-hidden', String(!open)); }
    }
  });

  /* ---------- Gallery + lightbox ---------- */
  define('ind-gallery', class extends HTMLElement {
    connectedCallback() {
      this.viewport = qs(this, '[data-viewport]');
      this.slides = qsa(this, '[data-slide]');
      this.thumbs = qsa(this, '[data-thumb]');
      this.dots = qsa(this, '[data-dot]');
      this.counter = qs(this, '[data-counter]');
      this.prevBtn = qs(this, '[data-prev]');
      this.nextBtn = qs(this, '[data-next]');
      if (!this.viewport || !this.slides.length) return;
      this.index = 0;

      this.thumbs.forEach((b, i) => b.addEventListener('click', () => this.go(i)));
      this.dots.forEach((b, i) => b.addEventListener('click', () => this.go(i)));
      if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.go(this.index - 1));
      if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.go(this.index + 1));
      this.viewport.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') { e.preventDefault(); this.go(this.index + 1); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); this.go(this.index - 1); }
      });
      let raf;
      this.viewport.addEventListener('scroll', () => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          const i = Math.round(this.viewport.scrollLeft / this.viewport.clientWidth);
          if (i !== this.index) this.mark(i);
        });
      }, { passive: true });

      // hover zoom follows the pointer
      qsa(this, '.ind-gallery__zoom').forEach((z) => {
        z.addEventListener('mousemove', (e) => {
          const r = z.getBoundingClientRect();
          z.style.setProperty('--zx', `${((e.clientX - r.left) / r.width) * 100}%`);
          z.style.setProperty('--zy', `${((e.clientY - r.top) / r.height) * 100}%`);
        });
        z.addEventListener('click', () => this.openLightbox(Number(z.dataset.index)));
      });

      this.lightbox = qs(this, '[data-lightbox]');
      if (this.lightbox) this.initLightbox();

      // variant image sync
      const section = this.closest('[data-section-id]');
      if (section) {
        section.addEventListener('ind:variant-change', (e) => {
          const mediaId = e.detail && e.detail.variant && e.detail.variant.featured_media && e.detail.variant.featured_media.id;
          if (!mediaId) return;
          const idx = this.slides.findIndex((s) => Number(s.dataset.mediaId) === mediaId);
          if (idx > -1) this.go(idx);
        });
      }
      this.mark(0);
    }
    go(i) {
      const n = this.slides.length;
      const idx = Math.max(0, Math.min(n - 1, i));
      this.viewport.scrollTo({ left: this.viewport.clientWidth * idx, behavior: 'smooth' });
      this.mark(idx);
    }
    mark(i) {
      this.index = i;
      this.thumbs.forEach((t, k) => t.setAttribute('aria-current', String(k === i)));
      this.dots.forEach((t, k) => t.setAttribute('aria-current', String(k === i)));
      this.slides.forEach((s, k) => s.setAttribute('aria-hidden', String(k !== i)));
      if (this.counter) this.counter.textContent = `${i + 1} / ${this.slides.length}`;
      if (this.prevBtn) this.prevBtn.disabled = i === 0;
      if (this.nextBtn) this.nextBtn.disabled = i === this.slides.length - 1;
      const active = this.thumbs[i];
      if (active && active.parentElement) {
        const p = active.parentElement;
        const vertical = p.scrollHeight > p.clientHeight;
        if (vertical) p.scrollTo({ top: active.offsetTop - p.clientHeight / 2 + active.clientHeight / 2, behavior: 'smooth' });
        else p.scrollTo({ left: active.offsetLeft - p.clientWidth / 2 + active.clientWidth / 2, behavior: 'smooth' });
      }
    }
    initLightbox() {
      const lb = this.lightbox;
      this.lbImg = qs(lb, 'img');
      this.lbStage = qs(lb, '[data-lb-stage]');
      this.lbSources = qsa(this, '.ind-gallery__zoom').map((z) => ({ src: z.dataset.full, alt: z.dataset.alt || '' }));
      qs(lb, '[data-lb-close]').addEventListener('click', () => lb.close());
      qs(lb, '[data-lb-prev]').addEventListener('click', () => this.lbShow(this.lbIndex - 1));
      qs(lb, '[data-lb-next]').addEventListener('click', () => this.lbShow(this.lbIndex + 1));
      lb.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') this.lbShow(this.lbIndex + 1);
        if (e.key === 'ArrowLeft') this.lbShow(this.lbIndex - 1);
      });
      lb.addEventListener('close', () => { this.resetZoom(); this.go(this.lbIndex); });

      // zoom: click / double-tap toggles 2.5×, drag pans
      let startX = 0, startY = 0, baseX = 0, baseY = 0, dragging = false, moved = false, swipeX = null;
      this.zoom = { s: 1, x: 0, y: 0 };
      const apply = () => { this.lbImg.style.transform = `translate(${this.zoom.x}px, ${this.zoom.y}px) scale(${this.zoom.s})`; };
      this.lbApply = apply;
      this.lbStage.addEventListener('pointerdown', (e) => {
        dragging = true; moved = false; startX = e.clientX; startY = e.clientY; baseX = this.zoom.x; baseY = this.zoom.y; swipeX = e.clientX;
        this.lbStage.setPointerCapture(e.pointerId);
      });
      this.lbStage.addEventListener('pointermove', (e) => {
        if (!dragging) return;
        const dx = e.clientX - startX, dy = e.clientY - startY;
        if (Math.abs(dx) + Math.abs(dy) > 6) moved = true;
        if (this.zoom.s > 1) { this.zoom.x = baseX + dx; this.zoom.y = baseY + dy; apply(); }
      });
      this.lbStage.addEventListener('pointerup', (e) => {
        dragging = false;
        if (!moved) {
          if (this.zoom.s > 1) { this.resetZoom(); }
          else {
            const r = this.lbImg.getBoundingClientRect();
            const ox = e.clientX - (r.left + r.width / 2), oy = e.clientY - (r.top + r.height / 2);
            this.zoom = { s: 2.5, x: -ox * 1.5, y: -oy * 1.5 };
            this.lbStage.classList.add('is-zoomed');
            apply();
          }
        } else if (this.zoom.s === 1 && swipeX !== null) {
          const dx = e.clientX - swipeX;
          if (Math.abs(dx) > 50) this.lbShow(this.lbIndex + (dx < 0 ? 1 : -1));
        }
      });
    }
    resetZoom() {
      this.zoom = { s: 1, x: 0, y: 0 };
      if (this.lbStage) this.lbStage.classList.remove('is-zoomed');
      if (this.lbApply) this.lbApply();
    }
    openLightbox(i) {
      if (!this.lightbox) return;
      this.lightbox.showModal();
      this.lbShow(i);
    }
    lbShow(i) {
      const n = this.lbSources.length;
      if (!n) return;
      this.lbIndex = (i + n) % n;
      this.resetZoom();
      this.lbImg.src = this.lbSources[this.lbIndex].src;
      this.lbImg.alt = this.lbSources[this.lbIndex].alt;
    }
  });

  /* ---------- Cart helpers ---------- */
  const addToCart = async (items) => {
    const drawer = document.querySelector('cart-drawer');
    const body = { items };
    if (drawer && typeof drawer.getSectionsToRender === 'function') {
      try {
        body.sections = drawer.getSectionsToRender().map((s) => s.id);
        body.sections_url = window.location.pathname;
      } catch (e) { /* ignore */ }
    } else {
      body.sections = ['cart-icon-bubble'];
    }
    const res = await fetch(`${IND.cartAddUrl || '/cart/add'}.js`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok || data.status) throw new Error(data.description || data.message || IND.strings.error);
    document.dispatchEvent(new CustomEvent('ind:cart-added', { detail: data }));

    if (drawer && typeof drawer.renderContents === 'function' && data.sections) {
      const first = (data.items && data.items[0]) || {};
      drawer.classList.remove('is-empty');
      drawer.renderContents({ ...data, id: first.variant_id, key: first.key });
      return 'drawer';
    }
    // No drawer: refresh the bubble ourselves, then go to the cart page.
    const bubble = document.getElementById('cart-icon-bubble');
    if (bubble && data.sections && data.sections['cart-icon-bubble']) {
      const doc = new DOMParser().parseFromString(data.sections['cart-icon-bubble'], 'text/html');
      const inner = doc.querySelector('.shopify-section');
      if (inner) bubble.innerHTML = inner.innerHTML;
    }
    window.location.href = IND.cartUrl || '/cart';
    return 'page';
  };
  IND.addToCart = addToCart;

  /* ---------- Product form: variants, quantity tiers, totals, ATC, Buy now, sticky bar ---------- */
  define('ind-product', class extends HTMLElement {
    connectedCallback() {
      this.section = this.closest('[data-section-id]') || this;
      const json = qs(this, 'script[data-product-json]');
      this.product = json ? JSON.parse(json.textContent) : null;
      if (!this.product) return;
      this.form = qs(this, 'form[data-product-form]');
      this.idInput = qs(this, 'input[name="id"]');
      this.qtyInput = qs(this, '[data-qty-input]');
      this.tiers = qsa(this, '[data-tier]');
      this.atc = qs(this, '[data-atc]');
      this.atcLabel = qs(this, '[data-atc-label]');
      this.buyNow = qs(this, '[data-buy-now]');
      this.error = qs(this, '[data-error]');
      this.optionInputs = qsa(this, '[data-option-input]');
      this.variant = this.product.variants.find((v) => v.id === Number(this.idInput.value)) || this.product.variants[0];

      this.optionInputs.forEach((i) => i.addEventListener('change', () => this.onOptionChange()));
      this.tiers.forEach((t) => {
        const input = qs(t, 'input');
        input.addEventListener('change', () => { if (input.checked) this.setQty(Number(t.dataset.qty), true); });
      });
      qsa(this, '[data-qty-step]').forEach((b) => b.addEventListener('click', () => {
        this.setQty(this.qty() + Number(b.dataset.qtyStep));
      }));
      if (this.qtyInput) {
        this.qtyInput.addEventListener('change', () => this.setQty(this.qty()));
      }
      this.form.addEventListener('submit', (e) => this.onSubmit(e));
      if (this.buyNow) this.buyNow.addEventListener('click', () => this.onBuyNow());
      document.addEventListener('ind:bf-state', () => this.refresh());

      // external triggers (sticky bar, final CTA)
      document.addEventListener('ind:request-atc', (e) => {
        if (e.detail && e.detail.productId === this.product.id) this.form.requestSubmit ? this.form.requestSubmit() : this.onSubmit(new Event('submit'));
      });

      this.initSticky();
      this.trackRecentlyViewed();
      const pre = this.tiers.find((t) => qs(t, 'input').checked);
      this.setQty(pre ? Number(pre.dataset.qty) : this.qty(), true);
    }

    qty() { return Math.max(1, parseInt(this.qtyInput && this.qtyInput.value, 10) || 1); }

    setQty(n, fromTier) {
      const q = Math.max(1, Math.min(99, n || 1));
      if (this.qtyInput) this.qtyInput.value = q;
      if (!fromTier && this.tiers.length) {
        // pick the largest tier whose quantity is <= q
        let match = null;
        this.tiers.forEach((t) => { if (Number(t.dataset.qty) <= q) match = t; });
        this.tiers.forEach((t) => { qs(t, 'input').checked = t === match && Number(t.dataset.qty) === q; });
      }
      this.refresh();
    }

    pctFor(q) {
      const bfActive = bfState() === 'active' && this.dataset.bfEligible === 'true';
      let pct = 0;
      this.tiers.forEach((t) => {
        if (Number(t.dataset.qty) <= q) pct = Number(bfActive ? t.dataset.bfPct : t.dataset.pct) || 0;
      });
      return pct;
    }

    onOptionChange() {
      const selected = [];
      qsa(this, '[data-option-group]').forEach((g) => {
        const checked = qs(g, 'input:checked');
        selected.push(checked ? checked.value : null);
      });
      const v = this.product.variants.find((x) => x.options.every((o, i) => o === selected[i]));
      if (!v) { this.variant = null; this.refresh(); return; }
      this.variant = v;
      this.idInput.value = v.id;
      const url = new URL(window.location.href);
      url.searchParams.set('variant', v.id);
      window.history.replaceState({}, '', url.toString());
      this.section.dispatchEvent(new CustomEvent('ind:variant-change', { detail: { variant: v } }));
      this.refresh();
    }

    refresh() {
      const v = this.variant;
      const q = this.qty();
      const fmt = IND.moneyFormat;
      const unavailable = !v || !v.available;

      // tier cards
      const bfActive = bfState() === 'active' && this.dataset.bfEligible === 'true';
      this.tiers.forEach((t) => {
        if (!v) return;
        const tq = Number(t.dataset.qty) || 1;
        const pct = Number(bfActive ? t.dataset.bfPct : t.dataset.pct) || 0;
        const original = v.price * tq;
        const total = Math.round(original * (1 - pct / 100));
        const set = (sel, txt) => { const el = qs(t, sel); if (el) el.textContent = txt; };
        set('[data-tier-total]', formatMoney(total, fmt));
        set('[data-tier-was]', pct > 0 ? formatMoney(original, fmt) : '');
        set('[data-tier-each]', `${formatMoney(Math.round(total / tq), fmt)} ${IND.strings.each}`);
        const saveEl = qs(t, '[data-tier-save]');
        if (saveEl) {
          saveEl.hidden = pct <= 0;
          saveEl.innerHTML = pct > 0 ? `· <strong>${IND.strings.save} ${formatMoney(original - total, fmt)} (−${pct}%)</strong>` : '';
        }
        const flag = qs(t, '[data-tier-pct-flag]');
        if (flag) { flag.hidden = pct <= 0; flag.textContent = `−${pct}%`; }
      });

      // summary + main price
      if (v) {
        const pct = this.pctFor(q);
        const original = v.price * q;
        const total = Math.round(original * (1 - pct / 100));
        qsa(this.section, '[data-summary-qty]').forEach((el) => { el.textContent = q; });
        qsa(this.section, '[data-summary-total]').forEach((el) => { el.textContent = formatMoney(total, fmt); });
        qsa(this.section, '[data-summary-was]').forEach((el) => { el.textContent = pct > 0 ? formatMoney(original, fmt) : ''; el.hidden = pct <= 0; });
        qsa(this.section, '[data-summary-save]').forEach((el) => { el.textContent = pct > 0 ? `${IND.strings.save} ${formatMoney(original - total, fmt)} (−${pct}%)` : ''; });
        qsa(this.section, '[data-price]').forEach((el) => { el.textContent = formatMoney(v.price, fmt); });
        qsa(this.section, '[data-compare]').forEach((el) => {
          const on = v.compare_at_price && v.compare_at_price > v.price;
          el.hidden = !on;
          el.textContent = on ? formatMoney(v.compare_at_price, fmt) : '';
        });
        qsa(this.section, '[data-sku]').forEach((el) => { el.textContent = v.sku || ''; });
      }

      // buttons
      const label = unavailable ? (IND.strings.soldOut) : (this.atcLabel ? this.atcLabel.dataset.default : IND.strings.addToCart);
      if (this.atc) { this.atc.disabled = unavailable; }
      if (this.atcLabel) this.atcLabel.textContent = label;
      if (this.buyNow) this.buyNow.disabled = unavailable;
      qsa(document, `[data-sticky-for="${this.product.id}"] [data-sticky-atc]`).forEach((b) => {
        b.disabled = unavailable;
        b.textContent = label;
      });
      qsa(this.section, '[data-stock]').forEach((el) => {
        el.classList.toggle('ind-buy__stock--out', unavailable);
        const msg = unavailable ? el.dataset.out : el.dataset.in;
        if (msg) el.firstChild.textContent = msg;
      });
    }

    async onSubmit(e) {
      e.preventDefault();
      if (!this.variant || !this.variant.available) return;
      this.setError('');
      this.loading(true);
      try {
        await addToCart([{ id: this.variant.id, quantity: this.qty() }]);
      } catch (err) {
        this.setError(err.message || IND.strings.error);
      } finally {
        this.loading(false);
      }
    }

    onBuyNow() {
      if (!this.variant || !this.variant.available) return;
      this.buyNow.classList.add('is-loading');
      // Cart permalink → straight to checkout with exactly this line. Shopify applies automatic discounts there.
      window.location.href = `${IND.root.replace(/\/$/, '')}/cart/${this.variant.id}:${this.qty()}`;
    }

    loading(on) {
      [this.atc, ...qsa(document, `[data-sticky-for="${this.product.id}"] [data-sticky-atc]`)].forEach((b) => {
        if (!b) return;
        b.classList.toggle('is-loading', on);
        b.setAttribute('aria-busy', String(on));
      });
    }

    setError(msg) {
      if (this.error) this.error.textContent = msg;
    }

    initSticky() {
      const bar = document.querySelector(`[data-sticky-for="${this.product.id}"]`);
      if (!bar || !this.atc) return;
      const btn = qs(bar, '[data-sticky-atc]');
      if (btn) btn.addEventListener('click', () => {
        if (window.matchMedia('(max-width: 749px)').matches && this.tiers.length && bar.dataset.mobileScroll === 'true') {
          this.scrollIntoView({ behavior: 'smooth', block: 'start' });
          return;
        }
        this.form.requestSubmit ? this.form.requestSubmit() : this.onSubmit(new Event('submit'));
      });
      const footer = document.querySelector('.ind-footer, footer');
      let atcVisible = true, footerVisible = false;
      const update = () => {
        const show = !atcVisible && !footerVisible && window.scrollY > 200;
        bar.classList.toggle('is-visible', show);
        bar.setAttribute('aria-hidden', String(!show));
        qsa(bar, 'button, a').forEach((el) => { el.tabIndex = show ? 0 : -1; });
      };
      new IntersectionObserver(([e]) => { atcVisible = e.isIntersecting || e.boundingClientRect.top > 0; update(); }).observe(this.atc);
      if (footer) new IntersectionObserver(([e]) => { footerVisible = e.isIntersecting; update(); }).observe(footer);
      update();
    }

    trackRecentlyViewed() {
      try {
        const key = 'ind:recent';
        const list = JSON.parse(localStorage.getItem(key) || '[]').filter((h) => h !== this.product.handle);
        list.unshift(this.product.handle);
        localStorage.setItem(key, JSON.stringify(list.slice(0, 8)));
      } catch (e) { /* storage blocked */ }
    }
  });

  /* ---------- Buttons elsewhere on the page that add the main product ---------- */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-ind-add]');
    if (!btn) return;
    e.preventDefault();
    const id = Number(btn.dataset.indAdd);
    const qty = Number(btn.dataset.qty) || 1;
    if (!id) return;
    btn.classList.add('is-loading');
    addToCart([{ id, quantity: qty }])
      .catch((err) => {
        const out = btn.parentElement && btn.parentElement.querySelector('[data-error]');
        if (out) out.textContent = err.message;
      })
      .finally(() => btn.classList.remove('is-loading'));
  });

  /* ---------- Recommendations + recently viewed ---------- */
  define('ind-recommendations', class extends HTMLElement {
    connectedCallback() {
      if (this.dataset.url) this.loadRelated();
      if (this.dataset.recent === 'true') this.loadRecent();
    }
    async loadRelated() {
      try {
        const res = await fetch(this.dataset.url);
        const html = await res.text();
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const fresh = doc.querySelector('[data-related-target]');
        const target = qs(this, '[data-related-target]');
        if (fresh && target && fresh.children.length) {
          target.innerHTML = fresh.innerHTML;
          qs(this, '[data-related]').hidden = false;
        }
      } catch (e) { /* leave hidden */ }
    }
    async loadRecent() {
      let handles = [];
      try { handles = JSON.parse(localStorage.getItem('ind:recent') || '[]'); } catch (e) { return; }
      handles = handles.filter((h) => h !== this.dataset.current).slice(0, 4);
      if (!handles.length) return;
      const target = qs(this, '[data-recent-target]');
      const products = await Promise.all(handles.map((h) =>
        fetch(`${IND.root.replace(/\/$/, '')}/products/${h}.js`).then((r) => (r.ok ? r.json() : null)).catch(() => null)));
      const cards = products.filter(Boolean).map((p) => {
        const img = p.featured_image ? `<img src="${p.featured_image}${p.featured_image.includes('?') ? '&' : '?'}width=600" alt="${p.title.replace(/"/g, '&quot;')}" loading="lazy" width="600" height="600">` : '';
        const was = p.compare_at_price > p.price ? `<s class="ind-price__was">${formatMoney(p.compare_at_price)}</s>` : '';
        return `<div class="ind-card"><div class="ind-card__media">${img}</div><div><h3 class="ind-card__title"><a href="${p.url}">${p.title}</a></h3></div><div class="ind-price"><span class="ind-price__now">${formatMoney(p.price)}</span>${was}</div></div>`;
      });
      if (cards.length && target) {
        target.innerHTML = cards.join('');
        qs(this, '[data-recent]').hidden = false;
      }
    }
  });

  /* ---------- Reveal on scroll ---------- */
  const reveal = () => {
    const els = qsa(document, '.ind-reveal:not(.is-in)');
    if (!('IntersectionObserver' in window)) { els.forEach((el) => el.classList.add('is-in')); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach((el) => io.observe(el));
  };

  const init = () => { applyBfVisibility(); reveal(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  document.addEventListener('shopify:section:load', init);
  // flip campaign visibility exactly at start / end without a reload
  setInterval(() => { if (document.documentElement.dataset.indBf !== bfState()) applyBfVisibility(); }, 15000);
})();
