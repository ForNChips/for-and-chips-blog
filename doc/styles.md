# Styles

How CSS is organised in the project, the design tokens, and the conventions to follow when adding rules.

## Layering

The site stacks three CSS layers:

1. **PaperMod base** (theme submodule, `themes/PaperMod/assets/css/`) — typography, default layout, dark-mode plumbing. Don't edit.
2. **`assets/css/extended/*.scss`** — our overrides and feature styles. Compiled by Hugo Pipes (`css.Sass`).
3. **Per-template inline styles** — only used when truly local (e.g. the D3 graph). Avoid where possible.

PaperMod's "extended" convention auto-loads any file in `assets/css/extended/`, but we register them explicitly in `layouts/partials/extend_head.html` to control order. **`vars.scss` must be first** so its custom properties are available to all subsequent files.

## File map

| File              | Scope                                                       |
| ----------------- | ----------------------------------------------------------- |
| `vars.scss`       | Design tokens (custom properties) for light + dark themes.  |
| `header.scss`     | Site header, nav, mobile hamburger, navbar search bar.      |
| `footer.scss`     | Site footer.                                                |
| `home.scss`       | Homepage hero + home-only layout.                           |
| `cards.scss`      | The article card component (used on home, list, author, tag pages). |
| `pagination.scss` | Shared pagination bar (`.pagination-bar`, `.page-btn`).     |
| `search.scss`     | Shared filter bar (`.search-bar`, `.article-list-search`).  |
| `404.scss`        | 404 page + `wobble` animation.                              |
| `authors.scss`    | `/authors` directory grid.                                  |
| `author.scss`     | Single author profile page.                                 |
| `keywords.scss`   | Tag/keyword chip styles.                                    |
| `tags.scss`       | `/tags` page (taxonomy + term).                             |
| `article.scss`    | Single article body (typography, headings, callouts).       |
| `chroma.scss`     | Theme-aware syntax highlighting. Every colour comes from `vars.scss`: `--code-*` (canvas, inks) + `--chroma-*` (one var per token family; dark = nord originals, light = HSL-darkened variants ≥ 4.5:1 on white). Requires `markup.highlight.noClasses: false`. |
| `tools.scss`      | `/tools` intro + single-tool link row (the card grid reuses `cards.scss`). |
| `article_list.scss`| `/articles` page layout.                                   |
| `citations.scss`  | `{{< cite >}}` and `{{< bibliography >}}` rendering.        |
| `page-titles.scss`| Shared page-title typography.                               |
| `donation.scss`   | Donation CTA block.                                         |
| `accessibility.scss`| Focus rings, skip-links, reduced-motion overrides.        |
| `about.scss`      | About page typography.                                      |
| `print.scss`      | Two-column elsarticle-style print stylesheet (`media="print"`). |

## Design tokens (`vars.scss`)

Tokens are CSS custom properties on `:root` (light) and `:root[data-theme="dark"]` (dark). PaperMod swaps `data-theme` via JS; we just provide the values.

### Layout

| Token             | Value     | Used for                            |
| ----------------- | --------- | ----------------------------------- |
| `--gap`           | `24px`    | Default gap between cards.          |
| `--content-gap`   | `20px`    | Gap inside content blocks.          |
| `--nav-width`     | `95%`     | Header rail width.                  |
| `--main-width`    | `85%`     | Article content rail width.         |
| `--header-height` | `100px`   | Reserved space for sticky header.   |
| `--footer-height` | `60px`    | Reserved space for footer.          |
| `--radius`        | `8px`     | Default corner radius.              |

### Elevation

`--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-lg-hover` — pre-tuned drop shadows. Use them instead of writing new `box-shadow` values.

### Color roles

PaperMod uses these names with strict roles. **Don't repurpose them.**

| Token         | Role                                                  |
| ------------- | ----------------------------------------------------- |
| `--theme`     | Page background.                                      |
| `--background`| Same as `--theme` for our setup.                      |
| `--entry`     | Card / entry surface (slightly raised).               |
| `--primary`   | Body text color + pagination button bg.               |
| `--secondary` | Meta text (dates, reading time, footer links).        |
| `--tertiary`  | Subtle bg (blockquotes, chips, search border).        |
| `--content`   | Article body text inside `.post-content`.             |
| `--text`      | Custom-CSS-only text (interchangeable with `--primary`). |
| `--accent`    | Buttons, links, active tags.                          |
| `--border`    | Default border color.                                 |
| `--code-bg`   | Inline code background.                               |
| `--code-block-bg` | Block code background.                            |
| `--logo-white`| The "white" in the logo SVG (inverted in dark mode).  |

### Brand palette

| Theme  | Background  | Accent              | Notes                                                  |
| ------ | ----------- | ------------------- | ------------------------------------------------------ |
| Light  | `#FFFFFF`   | `#C42B0C` salsa red | Warm cream cards (`#F7F5F0`), brown-black text.        |
| Dark   | `#141414`   | `#F0B429` melted cheese yellow | Warm off-white text, dark warm chip backgrounds. |

The food-coded names exist on purpose: this is a fish-and-chips blog wearing a salsa-and-cheese coat.

## Tag colors

Each entry in `data/tags.yml` carries a `color:` field. `keywords.scss` uses an SCSS map + `@each` loop to generate one CSS class per tag (e.g. `.kw-genomics`). Adding a tag is two steps:

1. Add the entry to `data/tags.yml` (key, label, color, optional icon).
2. Add the matching color to the SCSS map in `keywords.scss`. It will get its `.kw-<key>` class automatically.

If the tag class doesn't render, the SCSS map likely doesn't have the new entry yet.

## Conventions

- **Class names use kebab-case**: `.article-card`, `.section-header`, `.page-btn`. BEM-light: `.parent__child` only when scoping helps; otherwise nested SCSS rules are fine because Hugo Pipes ships compiled CSS without nesting.
- **Don't write new top-level files for one-off rules.** Add them to the closest existing scope file.
- **Always reference tokens via `var(--...)`** — never hard-code hex values outside `vars.scss`. The whole point is the dark-mode swap.
- **Print rules** live in `print.scss` only (loaded with `media="print"`); do not put `@media print` blocks elsewhere.
- **No `!important`** unless overriding a PaperMod base rule that itself uses `!important`. Document why if you do.
- **No emojis in CSS** unless explicitly requested by content.

## Adding a new SCSS file

1. Create `assets/css/extended/<feature>.scss`.
2. Register it in `layouts/partials/extend_head.html` after `vars.scss` (order matters for cascade).
3. Use existing tokens. If a new token is needed, add it to `vars.scss` for **both** themes.

## Debugging

- **Token undefined / falls back to white?** Check `vars.scss` has it under both `:root` blocks.
- **Style not applied?** Check the SCSS file is registered in `extend_head.html` and that Hugo's resource pipeline didn't fail (look in the dev-server output for sass errors).
- **Dark mode looks broken?** Open devtools → check `data-theme="dark"` is on `:root`. If missing, PaperMod's toggle script didn't run.
- **Print preview wrong?** Edit `print.scss` (loaded only in print media). Other files are not in scope when printing.
