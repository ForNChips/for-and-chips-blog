class Paginator {
  constructor({ articles, topEl, bottomEl, perPage = 10, label = 'article' }) {
    this.all      = articles;
    this.visible  = articles;
    this.topEl    = topEl;
    this.bottomEl = bottomEl;
    this.perPage  = perPage;
    this.label    = label;
    this.page     = 1;
    this._render();
  }

  setVisible(articles) {
    this.visible = articles;
    this.page    = 1;
    this._render();
  }

  _totalPages() {
    return Math.max(1, Math.ceil(this.visible.length / this.perPage));
  }

  _render() {
    const total = this._totalPages();
    const start = (this.page - 1) * this.perPage;
    const end   = start + this.perPage;

    this.all.forEach(a => (a.style.display = 'none'));
    this.visible.slice(start, end).forEach(a => (a.style.display = ''));

    const html = this._html(total);
    [this.topEl, this.bottomEl].forEach((el, i) => {
      if (!el) return;
      if (this.visible.length === 0) {
        // show "no results" only once, in the bottom slot
        el.innerHTML = i > 0 ? `<p class="pagination-empty">No ${this.label}s found.</p>` : '';
        return;
      }
      el.innerHTML = html;
      el.querySelectorAll('[data-page]').forEach(btn => {
        btn.addEventListener('click', () => {
          const v = btn.dataset.page;
          if      (v === 'prev') this.page = Math.max(1, this.page - 1);
          else if (v === 'next') this.page = Math.min(this._totalPages(), this.page + 1);
          else                   this.page = +v;
          this._render();
          this.all[0]?.parentElement?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
      });
      const sel = el.querySelector('.perpage-select');
      if (sel) sel.addEventListener('change', () => {
        this.perPage = +sel.value;
        this.page    = 1;
        this._render();
      });
    });
  }

  _html(totalPages) {
    if (this.visible.length === 0) return '';

    const opts = [5, 10, 20].map(n =>
      `<option value="${n}"${n === this.perPage ? ' selected' : ''}>${n}</option>`
    ).join('');
    const perPage = `<label class="pagination-perpage">Per page&nbsp;<select class="perpage-select">${opts}</select></label>`;

    let btns = '';
    if (totalPages > 1) {
      btns += `<button class="page-btn" data-page="prev"${this.page === 1 ? ' disabled' : ''}>«</button>`;
      let prev = null;
      for (const p of this._pageRange(totalPages)) {
        if (prev !== null && p > prev + 1) btns += `<span class="page-ellipsis">…</span>`;
        btns += `<button class="page-btn${p === this.page ? ' page-btn--active' : ''}" data-page="${p}">${p}</button>`;
        prev = p;
      }
      btns += `<button class="page-btn" data-page="next"${this.page === totalPages ? ' disabled' : ''}>»</button>`;
    }

    const count = `<span class="pagination-count">${this.visible.length} ${this.label}${this.visible.length !== 1 ? 's' : ''}</span>`;
    return `<div class="pagination-bar">${count}<nav class="pagination-nav">${btns}</nav>${perPage}</div>`;
  }

  _pageRange(total) {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const p   = this.page;
    const set = new Set([1, total, p - 1, p, p + 1].filter(n => n >= 1 && n <= total));
    return [...set].sort((a, b) => a - b);
  }
}
