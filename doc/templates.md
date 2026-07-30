# Templates

Every file under `layouts/` and what it does. Hugo resolves templates by `kind` + `type` + `layout`; see [`pages.md`](pages.md) for the URL → template mapping.

## Top-level layouts

| File                       | Used for                              | Notes                                          |
| -------------------------- | ------------------------------------- | ---------------------------------------------- |
| `404.html`                 | 404 page                              | Standalone, ships its own `<main>`.            |
| `index.html`               | Homepage (`/`)                        | Hero + latest posts grid + CTA.                |
| `articles.html`            | `/articles` list                      | Tag-filter UI + pagination container.          |
| `article/single.html`      | `/articles/<slug>`                    | Reading progress bar, citations, footer meta.  |
| `authors.html`             | `/authors`                            | Grid + fuzzy search input.                     |
| `author/single.html`       | `/author/<slug>`                      | Generated pages (content adapter).             |
| `collab/single.html`       | `/collab`                             | D3 force graph; data prepared in template.     |
| `article-graph/single.html`| `/article-graph`                      | D3 force graph of articles (tags + refs).      |
| `bags/list.html`           | `/bags` and `/bags/<slug>`            | Branches on `.Path`; lists member articles.    |
| `tools/list.html`          | `/tools`                              | Card grid + search + tag pills.                |
| `tool/single.html`         | `/tools/<slug>`                       | Tool page: category, platforms, repo link.     |
| `tags/list.html`           | `/tags/…` (retired)                   | Redirect shim → `/articles/?tag=` (see `static/_redirects`). |
| `_default/baseof.html`     | Wrapper for everything                | Defines the `<head>` / `<body>` skeleton.      |
| `_default/about.html`      | About page                            | Custom layout invoked via `layout: "about"`.   |
| `_default/index.json`      | `/index.json` (Fuse fallback index)   | Titles + summaries only; Pagefind covers full text. |
| `_default/rss.xml`         | RSS                                   | Standard PaperMod-derived feed.                |
| `robots.txt` / `_robots.txt`| `/robots.txt`                        | Hugo picks `robots.txt`; `_robots.txt` is a backup. |

## Partials

### `partials/` (root)

| File                  | Purpose                                                |
| --------------------- | ------------------------------------------------------ |
| `head.html`           | `<head>` content: meta, OpenGraph, JSON-LD, fonts.     |
| `header.html`         | Site header (logo, nav, search, hamburger).            |
| `footer.html`         | Site footer (links, donation block, copyright).        |
| `extend_head.html`    | **Compiles SCSS** via `css.Sass` + adds CDN links (Fuse, D3). |
| `extend_footer.html`  | Includes JS modules (`paginator`, `tag-filter`, etc.). |
| `logo.html`           | Inline SVG logo.                                       |
| `analytics.html`      | Analytics tag (no-op by default).                      |
| `comments.html`       | Comments embed (currently empty/placeholder).          |
| `donation.html`       | Donation CTA used in footer and article end.           |
| `search_bar.html`     | Page-level search bar (icon + input) used on `/articles`, `/bags`, `/authors`. |

### `partials/articles/`

| File                       | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| `cards.html`               | Renders a single article card (cover, title, meta). The grid wrapper is provided by callers. |
| `articles_list.html`       | The full filtered + paginated list used on `/articles`. |
| `article_authors.html`     | Inline list of author chips with avatars + links.       |
| `article_meta.html`        | Date / reading-time / tag row above an article body.    |
| `citation.html`            | "How to cite this article" block at the bottom.         |

### `partials/authors/`

| File                  | Purpose                                                |
| --------------------- | ------------------------------------------------------ |
| `authors_list.html`   | Grid of author cards consumed by `authors.html`.       |
| `author_name.html`    | Returns an author's display name from `data/authors.yml` by id. |

### `partials/home/`

| File                          | Purpose                                            |
| ----------------------------- | -------------------------------------------------- |
| `post_list_homepage.html`     | The "latest articles" block on `/`.                |

### `partials/tags/`

| File                     | Purpose                                            |
| ------------------------ | -------------------------------------------------- |
| `keyword_badges.html`    | Rounded keyword pills (read from `data/tags.yml`). |
| `tag_label.html`         | Returns a tag's display label from `data/tags.yml`. |
| `tag_link.html`          | Standard tag badge linking to `/articles/?tag=…`.  |

### `partials/helpers/`

| File           | Purpose                                                  |
| -------------- | -------------------------------------------------------- |
| `thumb.html`   | Resolves an article cover image with sensible fallbacks. |

### `partials/seo/`

| File                    | Purpose                                                 |
| ----------------------- | ------------------------------------------------------- |
| `google_scholar.html`   | `citation_*` meta tags so articles are indexable by Google Scholar. |

### `partials/templates/`

| File                  | Purpose                                                |
| --------------------- | ------------------------------------------------------ |
| `opengraph.html`      | OG tags (title, image, type, etc.).                    |
| `schema_json.html`    | Schema.org JSON-LD blob for the current page.          |

## Shortcodes

Authors use these in article bodies. They all live in `layouts/shortcodes/`.

| Shortcode             | Usage                                            | What it does                                                                 |
| --------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------- |
| `{{< cite "key" >}}`  | Inline citation                                  | Looks up `key` in `data/references.yml` and prints `(Author, Year)` linking to the bibliography section. Records the key for the `references:` frontmatter sync. |
| `{{< bibliography >}}`| End-of-article bibliography                      | Renders the article's `references:` list as a numbered list pulled from `data/references.yml`. |
| `{{< ref "slug" >}}`  | Cross-reference another article                  | Resolves to a `<a href="/articles/<slug>/">Title</a>` with the target article's title. Fails the build if the slug doesn't exist. |
| `{{< figure … >}}`    | An image with a caption                          | Overrides PaperMod's. Prefixes the caption with an auto-generated `Figure N` and, when `id` is set, adds an `id="fig-<id>"` anchor. `numbered="false"` opts out. |
| `{{< figrow >}}…{{< /figrow >}}` | Several figures side by side           | CSS-grid container; the figures share the row's image and caption tracks (`subgrid`) so every caption starts on the same line. `widths` / `cols` tune the columns. |
| `{{< figref "id" >}}` | In-text reference to a figure                    | Renders `Figure N` linked to `#fig-<id>`; an unknown id renders a visible `Figure ?` marker (and is reported by `scripts/validate.py`). |

Figure numbers come from `partials/helpers/figure-numbers.html`, which scans
the page's **raw markdown** for `figure` shortcodes in document order and caches
the resulting `id → number` map in the page store. It deliberately does not use
a render-time counter: a page's content is rendered several times (page, RSS,
search index), which would make a counter keep climbing.

## Conventions

- **`define "main"`** — every top-level layout defines a `main` block consumed by `_default/baseof.html`.
- **`hugo.Data.<name>`** is preferred over the older `site.Data` because it's clearer about read-only data lookup. Both work in this project.
- **`type` over `section`** — templates are picked by frontmatter `type:`, not by URL section. That's why article and author pages can live anywhere.
- **No JS in templates** — JS is loaded once via `extend_footer.html` and uses `data-*` attributes on the rendered HTML to pick its targets.

## Adding a new template

1. Drop the file in `layouts/<type>/single.html` (or wherever fits the kind).
2. Reference it from frontmatter (`type: foo`) or rely on Hugo's lookup order.
3. If you need new CSS, add an `assets/css/extended/<feature>.scss` file and import it from `partials/extend_head.html`.
4. If you need new JS, add `assets/js/extended/<feature>.js` and load it from `partials/extend_footer.html`.
