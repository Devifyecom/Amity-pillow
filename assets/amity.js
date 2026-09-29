/* Amity product page — behaviour for `amity-*` sections. */
(function () {
  if (window.__amityLoaded) return;
  window.__amityLoaded = true;

  const define = (name, ctor) => {
    if (!customElements.get(name)) customElements.define(name, ctor);
  };

  const formatMoney = (cents, format) => {
    const fmt = format || window.amityMoneyFormat || '${{amount}}';
    const value = (Number(cents) || 0) / 100;
    const withDelimiters = (num, decimals, thousands, decimal) => {
      const parts = num.toFixed(decimals).split('.');
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousands);
      return parts.join(decimals ? decimal : '');
    };
    return fmt.replace(/\{\{\s*(\w+)\s*\}\}/, (_, key) => {
      switch (key) {
        case 'amount_no_decimals':
          return withDelimiters(value, 0, ',', '.');
        case 'amount_with_comma_separator':
          return withDelimiters(value, 2, '.', ',');
        case 'amount_no_decimals_with_comma_separator':
          return withDelimiters(value, 0, '.', ',');
        case 'amount_with_apostrophe_separator':
          return withDelimiters(value, 2, "'", '.');
        default:
          return withDelimiters(value, 2, ',', '.');
      }
    });
  };

  /* ---------------- Gallery ---------------- */
  define(
    'am-gallery',
    class extends HTMLElement {
      connectedCallback() {
        this.viewport = this.querySelector('[data-viewport]');
        this.slides = [...this.querySelectorAll('[data-slide]')];
        this.thumbs = [...this.querySelectorAll('[data-thumb]')];
        this.dots = [...this.querySelectorAll('[data-dot]')];
        this.track = this.querySelector('[data-thumbs-track]');
        this.prev = this.querySelector('[data-thumbs-prev]');
        this.next = this.querySelector('[data-thumbs-next]');
        if (!this.viewport || !this.slides.length) return;

        this.thumbs.forEach((btn, i) => btn.addEventListener('click', () => this.go(i)));
        this.dots.forEach((btn, i) => btn.addEventListener('click', () => this.go(i)));
        this.prev && this.prev.addEventListener('click', () => this.go(this.index - 1));
        this.next && this.next.addEventListener('click', () => this.go(this.index + 1));

        this.index = 0;
        let raf;
        this.viewport.addEventListener(
          'scroll',
          () => {
            cancelAnimationFrame(raf);
            raf = requestAnimationFrame(() => {
              const i = Math.round(this.viewport.scrollLeft / this.viewport.clientWidth);
              if (i !== this.index) this.setActive(i);
            });
          },
          { passive: true }
        );
        this.setActive(0);

        document.addEventListener('amity:variant-change', (e) => {
          const mediaId = e.detail && e.detail.mediaId;
          if (!mediaId) return;
          const i = this.slides.findIndex((s) => s.dataset.mediaId === String(mediaId));
          if (i > -1) this.go(i);
        });
      }

      go(i) {
        const max = this.slides.length - 1;
        const target = Math.max(0, Math.min(max, i));
        this.viewport.scrollTo({ left: target * this.viewport.clientWidth, behavior: 'smooth' });
        this.setActive(target);
      }

      setActive(i) {
        this.index = i;
        this.thumbs.forEach((t, n) => t.setAttribute('aria-current', n === i ? 'true' : 'false'));
        this.dots.forEach((d, n) => d.setAttribute('aria-current', n === i ? 'true' : 'false'));
        this.slides.forEach((s, n) => {
          const v = s.querySelector('video');
          if (v && n !== i) v.pause();
        });
        if (this.prev) this.prev.disabled = i === 0;
        if (this.next) this.next.disabled = i === this.slides.length - 1;
        const thumb = this.thumbs[i];
        if (thumb && this.track) {
          const left = thumb.offsetLeft - (this.track.clientWidth - thumb.clientWidth) / 2;
          this.track.scrollTo({ left, behavior: 'smooth' });
        }
      }
    }
  );

  /* ---------------- Bundle picker + add to cart ---------------- */
  define(
    'am-bundle',
    class extends HTMLElement {
      connectedCallback() {
        this.form = this.querySelector('form');
        this.tiers = [...this.querySelectorAll('[data-tier]')];
        this.variantSelect = this.querySelector('[data-variant-select]');
        this.button = this.querySelector('[data-atc]');
        this.buttonText = this.querySelector('[data-atc-text]');
        this.error = this.querySelector('[data-atc-error]');
        this.variants = JSON.parse(this.querySelector('[data-variants]')?.textContent || '[]');
        this.moneyFormat = this.dataset.moneyFormat;
        this.labels = {
          add: this.dataset.labelAdd,
          soldOut: this.dataset.labelSoldOut,
          error: this.dataset.labelError,
        };

        this.tiers.forEach((tier) => {
          tier.querySelector('input').addEventListener('change', () => this.select(tier));
        });

        this.variantSelect &&
          this.variantSelect.addEventListener('change', () => {
            this.refreshPrices();
            const v = this.currentVariant();
            document.dispatchEvent(
              new CustomEvent('amity:variant-change', { detail: { mediaId: v && v.featured_media_id } })
            );
          });

        this.form.addEventListener('submit', (e) => this.onSubmit(e));

        const preset = this.tiers.find((t) => t.querySelector('input').checked) || this.tiers[0];
        preset && this.select(preset);
        this.refreshPrices();
      }

      currentVariant() {
        const id = this.variantSelect ? Number(this.variantSelect.value) : Number(this.dataset.variantId);
        return this.variants.find((v) => v.id === id) || this.variants[0];
      }

      selectedTier() {
        return this.tiers.find((t) => t.classList.contains('is-selected')) || this.tiers[0];
      }

      select(tier) {
        this.tiers.forEach((t) => {
          const on = t === tier;
          t.classList.toggle('is-selected', on);
          t.querySelector('input').checked = on;
        });
      }

      refreshPrices() {
        const v = this.currentVariant();
        if (!v) return;
        const unit = v.price;
        const unitCompare = Math.max(v.compare_at_price || 0, unit);

        this.tiers.forEach((tier) => {
          const qty = Number(tier.dataset.qty) || 1;
          const free = Number(tier.dataset.free) || 0;
          const pct = Number(tier.dataset.discount) || 0;
          const paid = Math.max(qty - free, 0);
          const price = Math.round(unit * paid * (1 - pct / 100));
          const compare = unitCompare * qty;
          const save = Math.max(compare - price, 0);

          const set = (sel, text) => {
            const el = tier.querySelector(sel);
            if (el) el.textContent = text;
          };
          set('[data-tier-price]', formatMoney(price, this.moneyFormat));
          set('[data-tier-compare]', compare > price ? formatMoney(compare, this.moneyFormat) : '');
          const saveEl = tier.querySelector('[data-tier-save]');
          if (saveEl) {
            saveEl.textContent = (saveEl.dataset.template || '').replace('[amount]', formatMoney(save, this.moneyFormat));
            saveEl.hidden = save <= 0;
          }
          tier.querySelectorAll('[data-free-unit]').forEach((el) => {
            el.textContent = formatMoney(unit, this.moneyFormat);
          });
        });

        const available = v.available;
        this.button.disabled = !available;
        this.buttonText.textContent = available ? this.labels.add : this.labels.soldOut;
      }

      async onSubmit(e) {
        e.preventDefault();
        if (this.button.disabled) return;
        const v = this.currentVariant();
        const tier = this.selectedTier();
        if (!v || !tier) return;

        const items = [{ id: v.id, quantity: Number(tier.dataset.qty) || 1 }];
        const bundleLabel = tier.dataset.label;
        if (bundleLabel) items[0].properties = { _bundle: bundleLabel };
        tier.querySelectorAll('[data-gift-variant]').forEach((g) => {
          const id = Number(g.dataset.giftVariant);
          if (id) items.push({ id, quantity: 1, properties: { _gift: 'true', _bundle: bundleLabel } });
        });

        const drawer = document.querySelector('cart-drawer');
        const body = { items };
        let sections = [];
        if (drawer && typeof drawer.getSectionsToRender === 'function') {
          try {
            sections = drawer.getSectionsToRender().map((s) => s.id);
            body.sections = sections;
            body.sections_url = window.location.pathname;
          } catch (err) {
            sections = [];
          }
        }

        this.setLoading(true);
        this.error.textContent = '';
        try {
          const res = await fetch(`${(window.routes && window.routes.cart_add_url) || '/cart/add'}.js`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify(body),
          });
          const data = await res.json();
          if (!res.ok || data.status) {
            this.error.textContent = data.description || data.message || this.labels.error;
            return;
          }
          document.dispatchEvent(new CustomEvent('amity:cart-added', { detail: data }));

          if (drawer && typeof drawer.renderContents === 'function' && data.sections) {
            try {
              const first = (data.items && data.items[0]) || {};
              drawer.classList.remove('is-empty');
              drawer.renderContents({ ...data, id: first.variant_id, key: first.key });
              return;
            } catch (err) {
              /* fall through to cart page */
            }
          }
          window.location.href = (window.routes && window.routes.cart_url) || '/cart';
        } catch (err) {
          this.error.textContent = this.labels.error;
        } finally {
          this.setLoading(false);
        }
      }

      setLoading(on) {
        this.button.classList.toggle('is-loading', on);
        this.button.setAttribute('aria-busy', on ? 'true' : 'false');
      }
    }
  );

  /* ---------------- Ship-by date ---------------- */
  define(
    'am-shipdate',
    class extends HTMLElement {
      connectedCallback() {
        const days = Number(this.dataset.days) || 0;
        const skipWeekends = this.dataset.skipWeekends === 'true';
        const d = new Date();
        let added = 0;
        while (added < days) {
          d.setDate(d.getDate() + 1);
          if (skipWeekends && (d.getDay() === 0 || d.getDay() === 6)) continue;
          added++;
        }
        try {
          this.textContent = new Intl.DateTimeFormat(document.documentElement.lang || undefined, {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
          }).format(d);
        } catch (e) {
          this.textContent = d.toDateString().slice(0, 10);
        }
      }
    }
  );

  /* ---------------- Accordion (animated <details>) ---------------- */
  define(
    'am-accordion',
    class extends HTMLElement {
      connectedCallback() {
        this.details = this.querySelector('details');
        this.summary = this.querySelector('summary');
        this.body = this.querySelector('.am-acc__body');
        if (!this.details || !this.summary || !this.body) return;
        this.group = this.dataset.group;
        this.summary.addEventListener('click', (e) => {
          e.preventDefault();
          this.details.open ? this.close() : this.open();
        });
      }

      open() {
        if (this.group) {
          document
            .querySelectorAll(`am-accordion[data-group="${this.group}"]`)
            .forEach((a) => a !== this && a.details && a.details.open && a.close());
        }
        this.details.open = true;
        const h = this.body.scrollHeight;
        this.body.animate([{ height: '0px' }, { height: `${h}px` }], { duration: 280, easing: 'ease-out' });
      }

      close() {
        const h = this.body.scrollHeight;
        const anim = this.body.animate([{ height: `${h}px` }, { height: '0px' }], {
          duration: 240,
          easing: 'ease-in',
        });
        anim.onfinish = () => (this.details.open = false);
      }
    }
  );

  /* ---------------- Tabs (sleep toggle) ---------------- */
  define(
    'am-tabs',
    class extends HTMLElement {
      connectedCallback() {
        this.tabs = [...this.querySelectorAll('[role="tab"]')];
        this.panels = [...this.querySelectorAll('[role="tabpanel"]')];
        this.tabs.forEach((tab, i) => {
          tab.addEventListener('click', () => this.activate(i));
          tab.addEventListener('keydown', (e) => {
            if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
            const n = (i + (e.key === 'ArrowRight' ? 1 : -1) + this.tabs.length) % this.tabs.length;
            this.activate(n);
            this.tabs[n].focus();
          });
        });
      }

      activate(i) {
        this.dataset.active = String(i);
        this.tabs.forEach((t, n) => {
          t.setAttribute('aria-selected', n === i ? 'true' : 'false');
          t.tabIndex = n === i ? 0 : -1;
        });
        this.panels.forEach((p, n) => (p.hidden = n !== i));
      }
    }
  );

  /* ---------------- Video reel ---------------- */
  define(
    'am-reel',
    class extends HTMLElement {
      connectedCallback() {
        this.video = this.querySelector('video');
        this.play = this.querySelector('[data-play]');
        this.sound = this.querySelector('[data-sound]');
        if (!this.video) return;
        this.video.muted = true;
        this.classList.add('is-muted');

        this.play && this.play.addEventListener('click', () => this.start(true));
        this.video.addEventListener('click', () => (this.video.paused ? this.start(false) : this.stop()));
        this.sound &&
          this.sound.addEventListener('click', () => {
            this.video.muted = !this.video.muted;
            this.classList.toggle('is-muted', this.video.muted);
            if (!this.video.muted && this.video.paused) this.start(false);
          });
        this.video.addEventListener('ended', () => this.classList.remove('is-playing'));
      }

      start(withSound) {
        document.querySelectorAll('am-reel.is-playing').forEach((r) => r !== this && r.stop());
        if (withSound) {
          this.video.muted = false;
          this.classList.remove('is-muted');
        }
        this.video.play().catch(() => {
          this.video.muted = true;
          this.classList.add('is-muted');
          this.video.play().catch(() => {});
        });
        this.classList.add('is-playing');
      }

      stop() {
        this.video.pause();
        this.classList.remove('is-playing');
      }
    }
  );

  /* ---------------- Review pagination ---------------- */
  define(
    'am-reviews',
    class extends HTMLElement {
      connectedCallback() {
        this.items = [...this.querySelectorAll('[data-review]')];
        this.perPage = Number(this.dataset.perPage) || 5;
        this.pager = this.querySelector('[data-pager]');
        this.pages = Math.max(1, Math.ceil(this.items.length / this.perPage));
        if (!this.pager) return;
        if (this.pages < 2) {
          this.pager.hidden = true;
          return;
        }
        this.render(1);
      }

      render(page) {
        this.page = page;
        this.items.forEach((el, i) => {
          el.hidden = Math.floor(i / this.perPage) + 1 !== page;
        });
        const chev = (dir) =>
          `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="${
            dir === 'prev' ? 'M10 3 5 8l5 5' : 'M6 3l5 5-5 5'
          }"/></svg>`;
        let html = `<button type="button" class="am-pager__btn" data-go="${page - 1}" aria-label="Previous page" ${
          page === 1 ? 'disabled' : ''
        }>${chev('prev')}</button>`;
        for (let p = 1; p <= this.pages; p++) {
          html += `<button type="button" class="am-pager__btn" data-go="${p}" ${
            p === page ? 'aria-current="page"' : ''
          }>${p}</button>`;
        }
        html += `<button type="button" class="am-pager__btn" data-go="${page + 1}" aria-label="Next page" ${
          page === this.pages ? 'disabled' : ''
        }>${chev('next')}</button>`;
        this.pager.innerHTML = html;
        this.pager.querySelectorAll('[data-go]').forEach((b) =>
          b.addEventListener('click', () => {
            this.render(Number(b.dataset.go));
            const top = this.getBoundingClientRect().top + window.scrollY - 80;
            window.scrollTo({ top, behavior: 'smooth' });
          })
        );
      }
    }
  );

  /* ---------------- Product recommendations ---------------- */
  define(
    'am-recommendations',
    class extends HTMLElement {
      connectedCallback() {
        if (!this.dataset.url || this.dataset.loaded) return;
        const load = () => {
          this.dataset.loaded = 'true';
          fetch(this.dataset.url)
            .then((r) => r.text())
            .then((text) => {
              const html = new DOMParser().parseFromString(text, 'text/html');
              const fresh = html.querySelector('am-recommendations');
              if (fresh && fresh.innerHTML.trim().length) this.innerHTML = fresh.innerHTML;
              else this.closest('.shopify-section')?.classList.add('hidden');
            })
            .catch(() => {});
        };
        if ('IntersectionObserver' in window) {
          const io = new IntersectionObserver(
            (entries) => {
              if (entries[0].isIntersecting) {
                io.disconnect();
                load();
              }
            },
            { rootMargin: '0px 0px 400px 0px' }
          );
          io.observe(this);
        } else load();
      }
    }
  );
})();
