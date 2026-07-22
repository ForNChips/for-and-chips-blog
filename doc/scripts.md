# Scripts

Frontend JavaScript, Python helpers, git hooks, CI workflows. Three layers: things that run in the browser, things that run on the contributor's machine before/around commits, and things that run on GitHub.

## Frontend JS — `assets/js/extended/`

All vanilla ES, no bundler. Loaded from `partials/extend_head.html` or `partials/extend_footer.html`.

| File                    | Loaded on              | Hooks into                                        | What it does                                                           |
| ----------------------- | ---------------------- | ------------------------------------------------- | ---------------------------------------------------------------------- |
| `nav-scroll.js`         | Every page             | `#menu`, `a[href^="#"]`                            | Persists menu scroll position; smooth-scrolls in-page anchors.        |
| `nav-hamburger-menu.js` | Every page             | `.nav-hamburger`, `.nav-dropdown`                 | Mobile menu open/close + focus trap.                                  |
| `navbar-search.js`      | Every page             | `.nav-search input`, fetches `/index.json`        | Fuse.js fuzzy search across articles.                                 |
| `theme-toggle.js`       | Every page¹            | `#theme-toggle`                                   | Light/dark theme switch.                                              |
| `top-link.js`           | Every page¹            | scroll position                                   | Scroll-to-top button.                                                 |
| `copy-code.js`          | Article pages          | code blocks                                       | Copy button on fenced code.                                          |
| `progress-bar.js`       | Article pages          | `#reading-progress`, scroll position              | Reading-progress bar at top of articles.                              |
| `paginator.js`          | Article/author lists   | `.pagination-bar`, per-page `data-*`              | Generic client-side pagination (`Paginator` class).                  |
| `tag-filter.js`         | Wherever a list is filtered | `.tag-pill[data-tag]`, `[data-tags]` items    | Shared `TagFilter` engine: pill toggle, text search, URL sync, paginator glue. |
| `articles-filter.js`    | `/articles`            | `#articles-tag-cloud`, `article[data-title]`      | Wires `TagFilter` for the articles list (multi-select + search).     |
| `bags-filter.js`        | `/bags`                | `#bags-tag-cloud`, `.bag-card`                     | Wires `TagFilter` for bag cards.                                     |
| `authors-filter.js`     | `/authors`             | `#authorSearch`, `#authors-grid .card`             | Wires `Paginator` + `TagFilter` (search-only, no pills) for author cards. |
| `force-graph.js`        | Graph pages            | —                                                 | Shared D3 helpers (`ForceGraph`): SVG/zoom, drag, tooltip, link dedup. |
| `collab-graph.js`       | `/collab`              | `#collab-graph`, `#collab-graph-data`              | Co-authorship network (uses `ForceGraph`).                          |
| `article-graph.js`      | `/article-graph`       | `#article-graph`, `#article-graph-data`            | Article relationship graph, refs/tags toggle (uses `ForceGraph`).   |

¹ Unless disabled via `disableThemeToggle` / `disableScrollToTop`.

### How pages wire the shared classes

There are exactly two wiring mechanisms:

1. **Standalone wiring files** (`articles-filter.js`, `bags-filter.js`, `authors-filter.js`) — one per page-level surface, loaded conditionally from `extend_head.html`. Each just constructs a `Paginator` and/or `TagFilter` with the page's DOM ids.
2. **The inline script in `cards.html`** — the one exception. The partial is parametric (DOM id prefix, pill selector, active class are template arguments), so the wiring is generated inline by Hugo. It depends on `paginator.js` / `tag-filter.js` being loaded on the page, which `extend_head.html` guarantees for the pages that use it.

If you add a new filtered page, prefer mechanism 1.

All modules use `data-*` attributes on the rendered HTML to find their targets — no hard-coded selectors that would couple them to a single template. If you rename a class in SCSS, check the JS for `querySelector` calls before assuming nothing else cares.

External libraries:

- **Pagefind** — full-text search index built post-build (`pagefind --site public`,
  see `doc/deployment.md`); `navbar-search.js` imports `/pagefind/pagefind.js` at
  runtime and falls back to Fuse when the index is absent (`hugo server`).
- **Fuse.js** — bundled locally (`assets/js/fuse.basic.min.js`), loaded in `extend_head.html`, dev fallback for `navbar-search.js`.
- **D3.js** — vendored (`assets/js/d3.v7.9.0.min.js`), loaded by `layouts/collab/single.html` and `layouts/article-graph/single.html`, which then load `force-graph.js` + their page module.
- Social icons are inlined SVGs (`assets/images/icons/social/`, Font Awesome
  Free, CC BY 4.0) via `partials/helpers/social_icon.html` — no icon CDN.

## Python — `scripts/`

Run from the repo root. Dependencies in `scripts/requirements.txt` and `pyproject.toml` (pyyaml + bibtexparser).

**Setup** — use `uv` for fast, reproducible environment management:

```bash
uv sync                 # Install dependencies defined in pyproject.toml
```

Alternatively, without `uv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

| File                  | Run by                          | Purpose                                                                 |
| --------------------- | ------------------------------- | ----------------------------------------------------------------------- |
| `bib_to_yaml.py`      | `pre-commit` hook + CI          | Parse every `.bib` in `bibliography/` → write `data/references.yml`.    |
| `sync_citations.py`   | `check_commit.py`               | Walk an article body for `{{< cite "key" >}}` and reconcile its `references:` frontmatter array. Returns whether anything changed. |
| `validate.py`         | CI (full repo) + library code   | The single source of truth for article validation. Other scripts import its `check_article()`. Checks: required fields, slug format, dates (future = warning), authors exist, references exist, tags exist, image references resolve, citations are listed, optional orphan warnings. |
| `check_commit.py`     | `pre-commit` hook               | For each staged article with `draft: false`: sync citations, re-stage if changed, run strict validation. Drafts are skipped. Auto-installs missing dependencies via `uv` on first run. Exit 1 blocks the commit. |

### The single publication flag

Articles carry one boolean: `draft`.

| `draft`    | Meaning                                                                                       |
| :--------: | --------------------------------------------------------------------------------------------- |
| `true`     | Work in progress. Won't render via Hugo (without `-D`). The pre-commit hook skips it entirely. |
| `false`    | Ready for the world. Every commit that touches it triggers full validation through the hook.   |

There is no separate "publish" command. Flipping `draft: false` *is* publishing — the hook makes sure the article passed all checks before the commit lands.

### Module dependency graph

```
check_commit.py ──► validate.py     (check_article, parse_frontmatter, load_yaml, ...)
                └► sync_citations.py (sync_file)

bib_to_yaml.py — standalone
```

`validate.py` keeps module-level lists `ERRORS`, `WARNINGS`, `INFO` plus `reset_findings()`. Importers must call `reset_findings()` between articles, which `check_commit.py` does inside its loop.

## Git hooks — `.githooks/`

Activate locally:

```bash
git config core.hooksPath .githooks
```

| Hook         | Triggers                            | Action                                                                                    |
| ------------ | ----------------------------------- | ----------------------------------------------------------------------------------------- |
| `pre-commit` | Every `git commit`                  | (a) If a `.bib` is staged, run `bib_to_yaml.py` and auto-stage `data/references.yml`. (b) Run `check_commit.py` over staged articles — drafts are skipped, non-drafts are synced + validated strictly. |
| `pre-push`   | Every `git push`                    | Run `hugo --gc --minify -D=false --quiet` as a final build sanity check.                   |

### Why validate at commit time

The contributor flow is: edit, commit, push. Drafts skip validation entirely, so commits stay fast while you're iterating. The moment you flip `draft: false`, the commit becomes the implicit "publish" gesture — and validation runs exactly once, on exactly that change. No second command to remember.

The build check stays in `pre-push` because it's the only step that proves the *whole site* still compiles, including changes to data files, layouts, or SCSS that no individual article commit could catch.

If a commit fails:

```
✖ content/articles/foo/index.md
  ERROR: …
…
Fix the errors above before committing (or set draft: true to defer).
```

The article on disk is untouched (apart from the citation sync, which is idempotent). Fix and `git commit` again.

### Bypassing

`git commit --no-verify` and `git push --no-verify` bypass the hooks. Don't, except in emergencies — CI will then catch it (slower, more public).

## CI — `.github/workflows/`

| Workflow                  | Trigger                                                  | What it does                                                                |
| ------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------- |
| `parse-bibliography.yml`  | Push to `main` touching any `.bib` (shared `bibliography/` or per-article `content/articles/**`) | Run `bib_to_yaml.py`, commit `data/references.yml` if changed. |
| `validate.yml`            | Pushes and PRs                                           | Install deps via `uv` (from `scripts/requirements.txt`), run `scripts/validate.py` on the entire content tree. Fails the PR on errors. |

CI uses `uv` for fast, reproducible builds. It re-validates the whole repo (not just the diff) — it's slower but catches drift in already-verified articles when references/tags/authors data changes.

## Adding a new check

1. Add the check function to `validate.py`. Append to `ERRORS` (fail) or `WARNINGS`/`INFO` (don't fail).
2. Decide if it's strict-only (CI/publish) or relaxed (development).
3. Call it from `check_article()` so all entry points pick it up.
4. Update `validate.yml` only if a new dependency is needed.

## Adding a new JS module

1. Drop `<feature>.js` in `assets/js/extended/`.
2. Load it from `partials/extend_head.html` (early) or `partials/extend_footer.html` (late). Wrap with the right `if .Type` / `if .IsHome` guard so it doesn't ship to every page.
3. Use `data-*` attributes on the markup to find targets; don't reach into PaperMod-controlled selectors.
