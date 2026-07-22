# Documentation

Reference docs for the For&Chips blog. Two kinds of reader:

- **Authors** — start (and probably end) with
  [`writing-articles.md`](writing-articles.md): the step-by-step guide to
  creating an article, every frontmatter key, authors, tags, references and
  the body features (citations, figures, code, cross-links).
- **Developers** — the remaining files cover **how the site is built** so you
  can debug, extend, or adapt it.

## How the docs are organised

| File                                       | Read it when…                                                                                  |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| [`../SETUP.md`](../SETUP.md)               | First time here: prerequisites, clone, `uv sync`, git hooks, dev server.                       |
| [`writing-articles.md`](writing-articles.md) | You want to write, edit, or publish an article (the authoring guide).                        |
| [`architecture.md`](architecture.md)       | You need the big picture: stack, file tree, build pipeline, data flow, CI.                     |
| [`pages.md`](pages.md)                     | Something renders wrong on a specific URL and you want to know which files are responsible.    |
| [`templates.md`](templates.md)             | You're editing a layout, partial, or shortcode in `layouts/`.                                  |
| [`styles.md`](styles.md)                   | You're touching SCSS, design tokens, or dark mode in `assets/css/extended/`.                   |
| [`scripts.md`](scripts.md)                 | You're working on the JS modules, Python helpers, git hooks, or CI workflows.                  |
| [`data.md`](data.md)                       | You're editing `data/*.yml`, the article archetype, or want the full frontmatter reference.    |
| [`deployment.md`](deployment.md)           | You're deploying: Cloudflare Pages setup, environments (production/demo), search index, third-party services. |

## Suggested reading order

- **First time in the repo** — read [`architecture.md`](architecture.md) end to end. It contains the diagrams that make the rest navigable.
- **Debugging a page** — jump straight to [`pages.md`](pages.md) and follow its links into the other files.
- **Adding a feature** — start at [`architecture.md`](architecture.md) for the relevant layer, then drill into the corresponding file.

## What's *not* in here

- Hugo and PaperMod internals — the upstream docs are better. We only document the parts we override or extend.
- Per-commit history or rationale — `git log` is authoritative.

## Keeping the docs honest

These files describe the codebase as it is, not as it was. If you change something structural — add a layout, rename a token, retire a script — update the matching doc in the same change. The tables are the parts most likely to drift; keep them in sync.
