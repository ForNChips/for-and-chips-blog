/* Shared tag-pill + text-search filter engine.
 *
 * One brick for every "filter a list of items" surface:
 *   /articles (articles-filter.js), /bags (bags-filter.js),
 *   /authors (authors-filter.js, search-only — no pills) and the
 *   cards.html partial (author page).
 *
 * Items are any elements carrying a comma-separated `data-tags` attribute.
 * Options:
 *   items        {Element[]}  elements to show/hide (required)
 *   cloud        {Element}    container holding .tag-pill buttons
 *   pills        {NodeList}   explicit pill list (overrides `cloud`)
 *   activeClass  {string}     class toggled on an active pill (default 'tag-pill--active')
 *   multi        {boolean}    multi-select AND logic (default) vs single-select
 *   searchInput  {Element}    optional free-text input
 *   searchFields {string[]}   dataset keys the text query matches (e.g. ['title','abstract'])
 *   paginator    {Paginator}  optional; when set, filtering drives it instead of inline display
 *   syncURL      {boolean}    mirror the current query/tags into ?q= &tag=
 */
class TagFilter {
  constructor(opts) {
    this.items        = opts.items || [];
    this.activeClass  = opts.activeClass || 'tag-pill--active';
    this.multi        = opts.multi !== false;
    this.searchInput  = opts.searchInput || null;
    this.searchFields = opts.searchFields || [];
    this.paginator    = opts.paginator || null;
    this.syncURL      = !!opts.syncURL;

    this.pills = opts.pills
      ? Array.from(opts.pills)
      : (opts.cloud ? Array.from(opts.cloud.querySelectorAll('.tag-pill')) : []);

    this.activeTags = new Set();
    this.query = '';

    this._wirePills();
    this._wireSearch();
    this._initFromURL();
    this.apply();
  }

  _wirePills() {
    this.pills.forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        this._toggle(btn.dataset.tag, btn);
      });
    });
  }

  _toggle(tag, btn) {
    if (!tag) return;
    if (this.multi) {
      if (this.activeTags.has(tag)) {
        this.activeTags.delete(tag);
        if (btn) btn.classList.remove(this.activeClass);
      } else {
        this.activeTags.add(tag);
        if (btn) btn.classList.add(this.activeClass);
      }
    } else {
      const wasActive = this.activeTags.has(tag);
      this.activeTags.clear();
      this.pills.forEach(p => p.classList.remove(this.activeClass));
      if (!wasActive) {
        this.activeTags.add(tag);
        if (btn) btn.classList.add(this.activeClass);
      }
    }
    this.apply();
  }

  _wireSearch() {
    if (!this.searchInput) return;
    this.searchInput.addEventListener('input', () => {
      this.query = this.searchInput.value.toLowerCase().trim();
      this.apply();
    });
  }

  _initFromURL() {
    const params = new URLSearchParams(window.location.search);
    if (this.searchInput) {
      const q = params.get('q');
      if (q) {
        this.searchInput.value = q;
        this.query = q.toLowerCase().trim();
      }
    }
    const tagParam = params.get('tag');
    if (tagParam) {
      const tags = this.multi ? tagParam.split(',') : [tagParam.split(',')[0]];
      tags.forEach(tag => {
        this.activeTags.add(tag);
        const pill = this.pills.find(p => p.dataset.tag === tag);
        if (pill) pill.classList.add(this.activeClass);
      });
    }
  }

  _matches(item) {
    const tags = (item.dataset.tags || '').split(',').filter(Boolean);
    const matchTag = this.activeTags.size === 0
      || Array.from(this.activeTags).every(t => tags.includes(t));
    const matchText = !this.query || !this.searchFields.length
      || this.searchFields.some(f => (item.dataset[f] || '').includes(this.query));
    return matchTag && matchText;
  }

  apply() {
    const filtered = this.items.filter(i => this._matches(i));

    if (this.paginator) {
      this.paginator.setVisible(filtered);
    } else {
      this.items.forEach(i => { i.style.display = 'none'; });
      filtered.forEach(i => { i.style.display = ''; });
    }

    if (this.syncURL) this._syncURL();
  }

  _syncURL() {
    const url = new URL(window.location);
    if (this.query) url.searchParams.set('q', this.query);
    else            url.searchParams.delete('q');
    if (this.activeTags.size > 0) url.searchParams.set('tag', Array.from(this.activeTags).join(','));
    else                          url.searchParams.delete('tag');
    history.replaceState(null, '', url);
  }
}
