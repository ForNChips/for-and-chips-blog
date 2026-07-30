# Writing an article — step by step

The complete authoring guide: how to create an article folder, what every
frontmatter key means, how to add authors, tags and references, and what
features are available in the body (citations, figures, code, cross-links).

Everything here is enforced by `scripts/validate.py`; the pre-commit hook runs
it automatically on any staged article with `draft: false`.

## 0. TL;DR checklist

1. Create `content/articles/<YYYY-MM-slug>/` with `index.md` (copy an existing
   article or use `hugo new articles/<slug>`).
2. Fill the frontmatter (§2). Keep `draft: true` while writing.
3. Write the body; cite with `{{</* cite */>}}`, add figures with captions,
   cross-link with `{{</* ref */>}}` (§5–§8).
4. Put every cited BibTeX entry in the article's own `references.bib` (§6).
5. Preview with `hugo server -D`, check `python scripts/validate.py`.
6. Flip `draft: false`, commit — the hook syncs citations and blocks on errors.

## 1. Create the folder

```
content/articles/<slug>/
├── index.md            # frontmatter + body
├── references.bib      # per-article BibTeX (only if you cite something)
└── images/
    ├── cover.png       # optional — card thumbnail + page header
    └── <figure>.png    # inline figures
```

- **Slug convention**: `YYYY-MM-subject`, e.g. `2026-01-my-first-article`.
  Lowercase ASCII, digits, `-`, `_` only — no accents, no spaces. The folder
  name is the URL (unless `slug:` overrides it).
- `hugo new articles/<slug>` scaffolds this from `archetypes/articles/`. It
  also creates a `ressources/` folder for working notes; published images must
  live in `images/` (the validator checks there).

## 2. Frontmatter — every key

```yaml
---
title: "Human-readable title shown on the page and cards"
date: 2026-01-15T10:00:00+02:00
lastmod:                              # optional — set on substantive updates
type: article                         # REQUIRED, never change — selects the template
slug: "2026-01-my-article"            # optional — defaults to the folder name
draft: true                           # flip to false to publish

authors:
 - id: "ines-labidi"                  # must exist in data/authors.yml (§3)
   affiliations:                      # optional — overrides the author's defaults
      - "Université de Lausanne, ESC"

description: "One to several sentences. This is the abstract on cards, the RSS
  summary, the search index entry and the SEO meta description. Plain text
  only: no markdown, no links."

tags: [ios, location, car_crash]      # keys from data/tags.yml (§4)

bags:                                 # optional — memberships in /bags/ (§9)
  iphone-road-accidents: 1            #   value = reading order inside the bag

files_path:                           # optional — "where to look" box on the page
  - label: "Cache.sqlite"
    path: "/private/var/mobile/Library/Cache/com.apple.routined/Cache.sqlite"
    datastructure: "SQLite"

references: []                        # AUTO-GENERATED from cite shortcodes — never edit
---
```

| Key | Required to publish | Notes |
|---|---|---|
| `title` | yes | Page + card title. |
| `date` | yes | Publication date; drives sort order. |
| `lastmod` | no | Shown as "updated"; leave empty otherwise. |
| `type` | yes | Always `article`. Drives template lookup. |
| `slug` | no | Set it if you ever rename the folder — keeps the URL stable. |
| `draft` | yes | `true` = invisible in production, validation relaxed. |
| `authors` | yes (≥ 1) | List of `{id, affiliations?}`; `id` must match `data/authors.yml`. |
| `description` | yes | The abstract. Self-contained plain text. |
| `tags` | recommended | Keys from the tag registry; unknown keys warn, not block. |
| `bags` | no | Map of `<bag-slug>: <order>`. |
| `files_path` | no | List of `{label, path, datastructure}` artefact locations. |
| `references` | auto | Rebuilt by `scripts/sync_citations.py` at commit time. |

## 3. Authors — adding a new one

Authors live in `data/authors.yml`, keyed by a kebab-case id:

```yaml
jane-doe:
  first_name: "Jane"
  last_name: "Doe"
  role: "Researcher"            # Researcher | Practitioner | Law enforcement | Founder | …
  description: "One-line bio shown on the author page."
  photo: "jane.png"             # file in assets/images/authors/ ("" → default.png)
  links:                        # each key gets an inline SVG icon; "" = hidden
    website: ""
    linkedin: ""
    orcid: ""
    github: ""
  current_affiliations:
    "Some University": "Position held"
  keywords:                     # shown as chips on the author card
    - "iOS"
    - "database"
```

Steps: add the block, drop the photo in `assets/images/authors/` (a missing or
typo'd photo falls back to `default.png`), then reference the id from the
article frontmatter. The author page at `/author/<id>/` is generated
automatically, listing every article that credits the id.

## 4. Tags — adding a new one

Tags are registry **keys**, not free text. Two files must agree:

1. `data/tags.yml` — add `key: {label: "Display name"}`.
2. `assets/css/extended/tags.scss` — add a colour to the `$tags` map.

A tag missing from either file still works (raw key as label, default colour)
and only triggers a validation warning. Tags are shared between articles and
tools; every listing page filters them per section.

## 5. Citing — the `cite` shortcode

```markdown
As shown by {{</* cite "smith_example_2024" */>}}, …
With a locator: {{</* cite "smith_example_2024" "p. 42" */>}}
```

Renders as `(Spek et al., 2023)` / `(Spek et al., 2023, p. 42)`. Do **not**
use Pandoc's `[@key]` — only the shortcode works. End the article with:

```markdown
## Références

{{</* bibliography */>}}
```

## 6. References — `references.bib`

Each article carries its own BibTeX file. Strict-mode rules (`draft: false`):

1. Every cited key must exist in the article's `references.bib`.
2. The `.bib` must contain **only** cited keys — no orphan entries.
3. Citing anything without a `references.bib` in the folder is an error.

The pre-commit hook regenerates `data/references.yml` and the frontmatter
`references:` block for you. Manual runs:

```bash
python scripts/bib_to_yaml.py                                  # .bib → data/references.yml
python scripts/sync_citations.py content/articles/<slug>/index.md
```

## 7. Figures and images

Drop files in `images/` and use the `figure` shortcode — every image needs a
caption and must be mentioned in the surrounding prose:

```markdown
{{</* figure src="images/speed_quality.png"
            alt="Comparison of iPhone vs reference speed"
            id="speed-quality"
            caption="Reported iPhone speed vs VBOX reference, by phase." */>}}
```

- **Never write the figure number in the caption.** `Figure N — ` is added
  automatically, numbering in document order across the whole page (rows
  included), so inserting or moving a figure renumbers everything by itself.
- `id` is optional but required to cross-reference the figure; use a short
  slug, unique within the page.
- `numbered="false"` opts a purely decorative image out of numbering (it then
  gets no anchor and cannot be referenced).
- No bare `![](images/…)` and no orphan figures (house style).
- `images/cover.png` (or `.jpg`/`.webp`) becomes the card thumbnail and page
  header; without it a placeholder gradient + tag chip is used.
- Converting a PDF figure: `pdftoppm -png -r 200 source.pdf images/name`, then
  rename the `-1` suffix away.

### Several figures on one row

Wrap two or more figures in `figrow`. Each keeps its own number and caption,
and the captions all start on the same line even when the images differ in
height:

```markdown
{{</* figrow */>}}
{{</* figure src="images/straight.png" alt="…" id="seg-straight" caption="Straight-line section." */>}}
{{</* figure src="images/corner.png"   alt="…" id="seg-corner"   caption="Cornering section." */>}}
{{</* /figrow */>}}
```

- Default: one equal column per figure. `widths="2fr 1fr"` gives uneven
  columns, `cols="2"` forces a fixed column count (figures then wrap onto
  further rows).
- Below 700 px the row stacks vertically.
- Do **not** use a markdown table for this — cells size to their own content,
  which is what pushed the captions out of line.

### Referring to a figure in the text

Use `figref` with the figure's `id`; the number is resolved at build time:

```markdown
The points overshoot the impact point ({{</* figref "case1-b" */>}}).
Compare with {{</* figref "seg-corner" "the cornering panel" */>}}.
```

`{{</* figref */>}}` renders `Figure 6` as a link to the figure. A dangling id
renders a visible `Figure ?` and is reported by `scripts/validate.py`, which
also flags duplicate ids and missing image files.

## 8. Other body features

- **Code blocks** with copy button and theme-aware highlighting:

  ```markdown
  {{</*code lang="sql" */>}}
  SELECT * FROM crumbs;
  {{</*/code */>}}
  ```

- **Cross-references** to sibling articles (never relative markdown links):

  ```markdown
  See {{</* ref "articles/2026-01-another-article" */>}}
  or {{</* ref "articles/<slug>" "custom label" */>}}.
  ```

- **Tables** for synthetic results; prose for interpretation.
- **Paper call-out** at the top when the article derives from a publication:
  `> 📄 This blog post accompanies …`.

## 9. Bags

A bag is a curated pack of articles around one use case. Create
`content/bags/<bag-slug>/_index.md` with `title`, `date`, `description` and a
prose introduction; then add `bags: {<bag-slug>: <order>}` to each member
article. The bag page lists members sorted by that order.

## 10. House style (enforced by convention)

- **British English** throughout (`colour`, `behaviour`, `analyse`).
- **No em/en dashes in prose** — commas, parentheses or a new sentence. Em
  dashes are fine in figure/table captions after the number.
- **No `---` horizontal rules** in the body (reserved for frontmatter).
- Classical section scaffolding (Introduction / Method / Results / …).
  **Start body sections at `##`**, sub-sections at `###`, and so on. The page
  title comes from frontmatter and is rendered as the page's single `<h1>`;
  using `#` in the body would add competing h1s and flatten the outline that
  screen readers and the table of contents rely on. Section headings still
  *look* the same size — the stylesheet remaps the scale.
- End with a "See also" block of `{{</* ref */>}}` links, then the References.

## 11. Publish

```bash
python scripts/validate.py    # full sweep — fix every ✖ error
```

Set `draft: false` and commit. The pre-commit hook re-syncs citations and
blocks the commit on any strict-mode error. `hugo server -D` previews drafts;
production builds only include `draft: false` articles.
