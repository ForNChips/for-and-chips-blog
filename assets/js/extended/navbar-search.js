(() => {
    // ── Desktop navbar: live dropdown + Enter → /articles/?q= ────────
    //
    // Search engine: Pagefind (full-text over article bodies, built by
    // `pagefind --site public` after `hugo`). When the /pagefind/ bundle is
    // absent — typically under `hugo server` — it falls back to Fuse over
    // /index.json (titles + summaries), so dev keeps a working search.
    const navSearch = document.querySelector('.nav-search');
    if (navSearch) {
        initDesktopSearch(navSearch);

        // Swap placeholder text at the tablet breakpoint (input shrinks to 60px).
        const navInput = navSearch.querySelector('input');
        const mq = window.matchMedia('(max-width: 800px)');
        const syncPlaceholder = (e) => {
            navInput.placeholder = e.matches ? 'Search' : 'Search articles';
        };
        mq.addEventListener('change', syncPlaceholder);
        syncPlaceholder(mq);
    }

    // ── Mobile dropdown: redirect only ────────────────────────────
    const mobileSearch = document.querySelector('.nav-dropdown__search');
    if (mobileSearch) {
        const mInput = mobileSearch.querySelector('input');
        const mBtn   = mobileSearch.querySelector('button');
        if (mInput) {
            mInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') redirectToPosts(mInput.value);
            });
            if (mBtn) mBtn.addEventListener('click', () => redirectToPosts(mInput.value));
        }
    }

    function redirectToPosts(q) {
        q = q.trim();
        if (q) window.location.href = '/articles/?q=' + encodeURIComponent(q);
    }

    function initDesktopSearch(container) {
        const input = container.querySelector('input');
        const btn   = container.querySelector('button');
        let engine        = null;   // { search(q) → [{title, permalink, summary, excerptHtml?}] }
        let engineLoading = null;
        let dropdown      = null;
        let queryToken    = 0;      // discards stale async results

        const ensureEngine = () => {
            if (engine || engineLoading) return engineLoading;
            engineLoading = import('/pagefind/pagefind.js')
                .then(async (pagefind) => {
                    await pagefind.init();
                    engine = {
                        search: async (q) => {
                            const res  = await pagefind.search(q);
                            const data = await Promise.all(res.results.slice(0, 6).map(r => r.data()));
                            return data.map(d => ({
                                title:       d.meta.title || d.url,
                                permalink:   d.url,
                                excerptHtml: d.excerpt
                            }));
                        }
                    };
                })
                .catch(() => fetch('/index.json')
                    .then(r => r.json())
                    .then(data => {
                        const fuse = new Fuse(data, {
                            keys: [{ name: 'title', weight: 2 }, { name: 'summary', weight: 1 }],
                            threshold: 0.4,
                            ignoreLocation: true,
                            minMatchCharLength: 2
                        });
                        engine = {
                            search: async (q) => fuse.search(q, { limit: 6 }).map(r => r.item)
                        };
                    })
                    .catch(() => { engineLoading = null; }));
            return engineLoading;
        };

        input.addEventListener('focus', ensureEngine);

        input.addEventListener('input', async function () {
            const q = this.value.trim();
            if (!q || q.length < 2 || !engine) { closeDropdown(); return; }
            const token = ++queryToken;
            const results = await engine.search(q);
            if (token !== queryToken) return;   // a newer query superseded this one
            renderDropdown(results);
        });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                redirectToPosts(this.value);
                closeDropdown();
            } else if (e.key === 'Escape') {
                closeDropdown();
                this.value = '';
                this.blur();
            }
        });

        if (btn) btn.addEventListener('click', () => redirectToPosts(input.value));

        document.addEventListener('click', (e) => {
            if (!container.contains(e.target) && dropdown && !dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        function renderDropdown(results) {
            closeDropdown();
            if (!results.length) return;

            dropdown = document.createElement('ul');
            dropdown.className = 'nav-search-dropdown';

            results.forEach(post => {
                const li = document.createElement('li');
                const a  = document.createElement('a');
                a.href      = post.permalink;
                a.className = 'nav-search-result';

                const title = document.createElement('span');
                title.className   = 'nav-search-result__title';
                title.textContent = post.title;
                a.appendChild(title);

                if (post.excerptHtml) {
                    // Pagefind excerpt: our own article text with <mark>
                    // highlights around the matched terms.
                    const excerpt = document.createElement('span');
                    excerpt.className = 'nav-search-result__summary';
                    excerpt.innerHTML = post.excerptHtml;
                    a.appendChild(excerpt);
                } else if (post.summary) {
                    const summary = document.createElement('span');
                    summary.className   = 'nav-search-result__summary';
                    summary.textContent = post.summary.length > 90
                        ? post.summary.slice(0, 90) + '…'
                        : post.summary;
                    a.appendChild(summary);
                }

                li.appendChild(a);
                dropdown.appendChild(li);
            });

            const rect = container.getBoundingClientRect();
            dropdown.style.top   = (rect.bottom + window.scrollY + 4) + 'px';
            dropdown.style.left  = (rect.left + window.scrollX) + 'px';
            dropdown.style.width = Math.max(rect.width, 280) + 'px';
            document.body.appendChild(dropdown);
        }

        function closeDropdown() {
            if (dropdown) { dropdown.remove(); dropdown = null; }
        }
    }
})();
