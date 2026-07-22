# For&Chips — Digital Forensics Blog

An informal community blog about digital forensics, built with [Hugo](https://gohugo.io/) and a customised [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme. A shared space for researchers and practitioners to publish write-ups, document findings, and avoid reinventing the wheel.

> Live site: <https://forandchips.com>

---

## Table of contents

1. [Project at a glance](#1-project-at-a-glance)
2. [Quick start](#2-quick-start)
3. [Writing an article](#3-writing-an-article)
4. [Citing references](#4-citing-references)
5. [Cross-referencing other articles](#5-cross-referencing-other-articles)
6. [Adding images](#6-adding-images)
7. [Adding an author](#7-adding-an-author)
8. [Adding a tag](#8-adding-a-tag)
9. [Publishing an article](#9-publishing-an-article)
10. [Local checks and git hooks](#10-local-checks-and-git-hooks)
11. [Where to dig deeper](#11-where-to-dig-deeper)


---

## 1. Project at a glance

For&Chips is **fully static**. There is no backend, no database, and no admin UI. Every article, author, and reference lives as a flat file in this repository, and Hugo compiles the whole thing into plain HTML/CSS/JS at build time.

The mental model is intentionally simple:

```
content/articles/<slug>/index.md   ─┐
data/authors.yml                    ├─►  Hugo  ─►  public/  ─►  Cloudflare Pages
data/references.yml (← .bib files)  ─┘
```

A few design choices guide the codebase:

- **One article = one folder** under `content/articles/<slug>/`. The folder holds the Markdown body, the cover image, and any inline images. Move the folder, the URL moves with it.
- **Authors are a database, not pages.** `data/authors.yml` is the single source of truth. Author profile pages are generated automatically by a Hugo content adapter — you never write Markdown for an author.
- **References come from BibTeX.** Drop `.bib` files in `bibliography/`, the `bib_to_yaml.py` script (run by CI and the pre-commit hook) regenerates `data/references.yml`. Your articles cite keys, not full citations.
- **Validation runs locally and in CI.** A linter (`scripts/validate.py`) catches missing authors, broken citations, and orphaned data before they reach production. The pre-commit hook runs the same checks on any article you commit with `draft: false`.
- **One flag controls publication: `draft`.** `draft: true` means "work in progress, commit freely". `draft: false` means "ready for the world" — and triggers full validation on commit. There is no separate publish step.

If you want a deeper picture of the build pipeline, read [doc/architecture.md](doc/architecture.md).

---

## 2. Quick start

For detailed setup instructions, see [SETUP.md](SETUP.md).

**TL;DR:**

```bash
git clone --recurse-submodules <repo-url>
cd for-and-chips-blog
uv sync                                 # install Python dependencies
git config core.hooksPath .githooks    # enable git hooks
hugo server -D                          # start dev server at http://localhost:1313
```

**Using VS Code?** Press `Cmd+Shift+B` to start the Hugo dev server directly (see [.vscode/README.md](.vscode/README.md) for more shortcuts).

If you forgot `--recurse-submodules`, fix it with:

```bash
git submodule update --init --recursive
```

---

## 3. Writing an article

### 3.1 Scaffold the folder

```bash
hugo new content articles/my-article-slug/
```

This copies the [archetypes/articles/](archetypes/articles/) skeleton into `content/articles/my-article-slug/`. The folder name becomes the default slug and URL — the archetype has no control over it, so choose it carefully before running the command.

By convention, **use the ISO date as the folder name** (`YYYY-MM-DD`) to keep articles sorted chronologically on disk:

```bash
hugo new content articles/2025-06-24/
```

This copies the [archetypes/articles/](archetypes/articles/) skeleton into `content/articles/2025-06-24/`. You get:

```
content/articles/my-article-slug/
├── index.md           # the article body and frontmatter
└── ressources/        # a folder for working files (not published)
```

### 3.2 Fill in the frontmatter

Open `index.md`. The full set of fields you can use:

```yaml
---
title: "Title shown on the article page and in cards"
date: 2026-04-29T10:00:00+02:00
lastmod:                              # optional — set when you make a substantive update
type: article                         # do not change — drives template lookup
slug: "my-article-slug"               # optional — defaults to the folder name

draft: true                           # set to false when ready — triggers full validation on commit

authors:
  - id: "ben-ten"                     # must match a key in data/authors.yml
    affiliations:                     # optional — overrides the author's default affiliations
      - "University of X, Lab Y"

abstract: "One paragraph shown on cards, in search results, and on the article header."

tags: [logs, ios, mobile_forensic]    # use keys from data/tags.yml; see §8

# Filled in automatically by sync_citations.py when you cite something
references: []
---

Article body in Markdown…
```

**Required**: `title`, `date`, `abstract`, at least one author. Validation will block publication otherwise.

### 3.3 Slug rules

Slugs become URLs (`/articles/<slug>/`). Use lowercase ASCII, digits, `-`, or `_`. No accents, no spaces, no uppercase. The validator warns you if you stray.

### 3.4 Preview

Run `hugo server -D` and open <http://localhost:1313/articles/>. Drafts only show up with the `-D` flag. The dev server hot-reloads on every save, including SCSS.

---

## 4. Citing references

The blog uses Harvard-style citations: `(Author, Year)`. References live in `data/references.yml`, which is generated automatically from BibTeX files.

### 4.1 Add the reference

Drop or edit a `.bib` file under `bibliography/`. Each entry needs at minimum a key, author, year, and title:

```bibtex
@article{smith2020,
  author  = {Smith, Jane and Doe, John},
  title   = {On the forensics of nothing in particular},
  journal = {Journal of Trivia},
  year    = {2020},
  doi     = {10.1234/jot.2020.42}
}
```

The pre-commit hook regenerates `data/references.yml` whenever you stage a `.bib` change, so you don't need to run anything by hand. To do it manually:

```bash
python scripts/bib_to_yaml.py
```

### 4.2 Cite inside the article

```markdown
As shown by {{</* cite "smith2020" */>}}, …

Page-specific citation: {{</* cite "smith2020" "p. 42" */>}}
```

This renders as `(Smith and Doe, 2020)` and `(Smith and Doe, 2020, p. 42)`. Single author becomes `(Smith, 2020)`; three or more become `(Smith et al., 2020)`.

### 4.3 Render the bibliography

End the article with a "References" section and the `bibliography` shortcode:

```markdown
## References

{{</* bibliography */>}}
```

The shortcode reads the `references:` array in your frontmatter and renders a Harvard-formatted list. **You don't need to maintain that array by hand** — the pre-commit hook scans your body for `{{< cite … >}}` shortcodes and rewrites the array whenever you commit a non-draft article. To run it manually: `python scripts/sync_citations.py path/to/article/index.md`.

### 4.4 If a citation is missing

A `{{< cite >}}` pointing to an unknown key renders as `(?, ?)` with a tooltip. Validation flags it as an error before push.

---

## 5. Cross-referencing other articles

Use the `ref` shortcode to link to another article by its content path:

```markdown
We covered this previously in {{</* ref "articles/my-other-article" */>}}.

Custom label: {{</* ref "articles/my-other-article" "this earlier post" */>}}.
```

If the path doesn't resolve, the shortcode renders a `.article-xref-missing` placeholder rather than crashing the build.

---

## 6. Adding images

### 6.1 Cover image

Place a file named `cover.png` (or `.jpg`, `.webp`) in `content/articles/<slug>/images/`:

```
content/articles/my-article/
├── index.md
└── images/
    └── cover.png       ← shown on the homepage card and the article header
```

If absent, the placeholder gradient + tag chip is used automatically.

### 6.2 Inline images

Drop additional images in the same `images/` folder and reference them with relative paths in Markdown:

```markdown
![Phone with broken screen](images/broken-screen.png)
```

The validator checks that every `![](images/…)` reference points to an existing file. Images that sit on disk but are never referenced in any article are reported as orphans (info-level, not blocking) when you run `python scripts/validate.py`.

---

## 7. Adding an author

1. Open [data/authors.yml](data/authors.yml).
2. Add a new entry with a lowercase hyphenated key:

   ```yaml
   alice-dupont:
     first_name: "Alice"
     last_name: "Dupont"
     role: "Researcher"               # Researcher | Practitioner | Founder | Contributor | Law enforcement
     description: "Short bio shown on the author profile page."
     photo: "alice-dupont.png"        # filename inside assets/images/authors/
     current_affiliations:
       "University of X": "PhD student"
     keywords: [mobile_forensic, ios] # tag keys from data/tags.yml
     links:
       linkedin: "https://linkedin.com/in/…"
       github:   "https://github.com/…"
       orcid:    "0000-0000-0000-0000"
       website:  "https://example.com"
   ```

3. Drop a square photo (≥ 300 px) at `assets/images/authors/alice-dupont.png`. If `photo:` is empty, the default placeholder is used.
4. Done. The profile page at `/author/alice-dupont/` is generated on the next build by [content/author/_content.gotmpl](content/author/_content.gotmpl) — no Markdown file to write.

To credit the author in an article:

```yaml
authors:
  - id: "alice-dupont"
```

---

## 8. Adding a tag

Tags appear as colored badges on cards, profiles, and tag pages. Each tag has a *key* (used in frontmatter and URLs), a display *label*, and a *color*.

1. **Display label** — add an entry to [data/tags.yml](data/tags.yml):

   ```yaml
   keywords:
     car_forensic:
       label: "Car forensic"
   ```

2. **Color** — add a line to the `$tags` SCSS map in [assets/css/extended/tags.scss](assets/css/extended/tags.scss):

   ```scss
   $tags: (
     // …
     "car_forensic": #FF6B6B,
   );
   ```

   The map is rendered into CSS via `@each`, so a single entry styles every place the tag appears (article cards, filter pills, author chips, keyword badges).

A tag missing from either file still renders — it falls back to the default `--tag-bg` color and the raw key as label. The validator warns you, but doesn't block.

---

## 9. Publishing an article

Publishing is a single edit: flip `draft: true` to `draft: false` in the frontmatter, then commit normally.

```diff
- draft: true
+ draft: false
```

```bash
git add content/articles/my-article-slug/
git commit -m "publish: my article"
```

The pre-commit hook intercepts every staged article with `draft: false` and runs three steps before letting the commit through:

1. **Sync** — rewrites the `references:` block from your `{{< cite >}}` shortcodes (and re-stages the file if it changed).
2. **Validate** — every check listed in [doc/scripts.md](doc/scripts.md#scriptsvalidatepy).
3. **Commit** — only if everything is green; otherwise the commit is blocked and the errors are printed.

If validation fails, fix the issues and `git commit` again. As long as the article stays `draft: true`, no validation runs — commit early, commit often.

---

## 10. Local checks and git hooks

The `.githooks/` folder contains two hooks. Enable them once per clone:

```bash
git config core.hooksPath .githooks
```

**Pre-commit** — does two things:
1. When a `bibliography/*.bib` file is staged, regenerates `data/references.yml` and stages it so it lands in the same commit.
2. For every staged article with `draft: false`, syncs the citations and runs strict validation. Drafts are skipped, so WIP commits stay fast.

The pre-commit hook automatically installs dependencies using `uv` if they're missing (see `scripts/check_commit.py`), so you don't need to manually install anything — just commit normally.

**Pre-push** — runs `hugo --gc --minify -D=false` as a final build sanity check before the push reaches Cloudflare. Push is blocked on a build failure.

You can run validation manually any time:

```bash
python scripts/validate.py        # full repo sweep
```

Output uses three levels:

- `✖ ERROR` — must fix before publishing (blocks CI)
- `▲ WARNING` — worth reviewing, doesn't block
- `· INFO` — informational (orphaned authors, unused references, etc.)

**CI/CD** — uses `uv` for fast, reproducible builds. GitHub Actions ([.github/workflows/validate.yml](.github/workflows/validate.yml)) installs dependencies via `uv pip install -r scripts/requirements.txt` on every PR. The backing data file [.github/workflows/parse-bibliography.yml](.github/workflows/parse-bibliography.yml) regenerates `data/references.yml` if a `.bib` change slips through without the hook.

---

## 11. Where to dig deeper

This README covers the contributor workflow. For the technical inner workings — how templates compose, what each SCSS file styles, how the build pipeline plumbs together — read the documentation under [doc/](doc/):

| File | What it covers |
|---|---|
| [doc/architecture.md](doc/architecture.md) | Stack, project layout, build pipeline, data flow, deploy, CI |
| [doc/pages.md](doc/pages.md) | Each URL → template + partials + SCSS + JS involved |
| [doc/templates.md](doc/templates.md) | Every layout, partial, and shortcode in `layouts/` |
| [doc/styles.md](doc/styles.md) | SCSS scope, conventions, design tokens, light/dark mode |
| [doc/scripts.md](doc/scripts.md) | JS frontend, Python helper scripts, git hooks, CI |
| [doc/data.md](doc/data.md) | Schemas of `authors.yml`, `tags.yml`, `references.yml`, frontmatter reference |

If you want to add a new feature, debug a layout, or rework the styling, start with `doc/pages.md` to find the page involved, then jump to `doc/templates.md` or `doc/styles.md` for the underlying file.
