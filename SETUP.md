# Development Setup

One-time setup to develop the For&Chips blog locally. When you're done here:
[doc/writing-articles.md](doc/writing-articles.md) to write, [doc/](doc/) to
understand the machinery.

## Prerequisites

- **Hugo Extended** ≥ 0.160 — [install](https://gohugo.io/installation/) (the `extended` build is **required**, plain Hugo can't compile the SCSS)
- **Git** with submodule support
- **uv** — [install](https://docs.astral.sh/uv/getting-started/installation/) (fast Python package manager; runs the validation scripts)
- **Python** 3.10+ (uv can install this for you)

## One-time setup

### 1. Clone the repository

```bash
git clone --recurse-submodules https://github.com/ForNChips/for-and-chips-blog.git
cd for-and-chips-blog
```

If you forgot `--recurse-submodules`, fetch the theme afterwards:

```bash
git submodule update --init --recursive
```

### 2. Install the Python dependencies

```bash
uv sync
```

This creates a project venv from `pyproject.toml` / `uv.lock` with everything
the validation and citation scripts need (`pyyaml`, `bibtexparser`).

### 3. Enable the git hooks

```bash
git config core.hooksPath .githooks
```

Must be re-run on every fresh clone. The hooks then take care of themselves:

- **pre-commit** — regenerates `data/references.yml` when a `.bib` is staged,
  and validates every staged non-draft article. It runs Python through `uv`
  automatically (no venv activation needed).
- **pre-push** — full `hugo --gc --minify` build so a broken build never
  reaches the remote.

## Day-to-day commands

| Task | Command |
|---|---|
| Dev server (with drafts, hot reload) | `hugo server -D` → <http://localhost:1313> |
| Validate the whole repo | `uv run scripts/validate.py` |
| Production build | `hugo --minify` |
| Demo-environment build | `hugo --minify --environment demo` |
| Re-sync one article's citations | `uv run scripts/sync_citations.py content/articles/<slug>/index.md` |
| Rebuild the references data file | `uv run scripts/bib_to_yaml.py` |

Validation output levels: `✖ ERROR` blocks publishing, `▲ WARNING` is worth
reviewing, `· INFO` is informational.

### VS Code shortcut

`Cmd+Shift+B` starts the Hugo dev server (configured in [.vscode/tasks.json](.vscode/tasks.json)).

### Full-text search locally (optional)

The navbar search uses a Pagefind index that only exists on deployed builds;
under `hugo server` it falls back to a title/summary search automatically. To
try the real thing locally:

```bash
hugo -D --destination /tmp/site
uv run --with 'pagefind[bin]' python -m pagefind --site /tmp/site
python3 -m http.server 8000 --directory /tmp/site
```

## Environments

Hugo config lives in `config/`: `_default/` (everything) plus `production/`
and `demo/` overlays. Plain `hugo` builds production; `--environment demo`
builds the noindex demo variant; `hugo server` runs the development
environment. See [doc/deployment.md](doc/deployment.md) for how the two
Cloudflare Pages projects consume this.

## Dependency management

Add new Python dependencies to **both** `scripts/requirements.txt` and
`pyproject.toml`, then run `uv sync` and commit the updated `uv.lock`. CI
(`.github/workflows/validate.yml`) installs from `scripts/requirements.txt`.

## Troubleshooting

### `ModuleNotFoundError: No module named 'yaml'`

Dependencies aren't installed — run `uv sync`. If you don't use uv, the hooks
also accept a legacy `hugo.venv` virtualenv at the repo root:

```bash
python3 -m venv hugo.venv && hugo.venv/bin/pip install -r scripts/requirements.txt
```

### Git hooks aren't running

```bash
git config core.hooksPath   # should print: .githooks
git config core.hooksPath .githooks   # if it doesn't
```

### Hugo can't find the theme

The theme is a git submodule:

```bash
git submodule update --init --recursive
```

### `Error: ... css.Sass ... this feature is not available`

You installed plain Hugo. Reinstall the **extended** build.

### Build is very slow

Publishing (`draft: false`) triggers full validation. Keep `draft: true`
while iterating.

## What's next?

- [doc/writing-articles.md](doc/writing-articles.md) — the authoring guide (folder layout, frontmatter, citations, figures)
- [doc/README.md](doc/README.md) — index of the developer docs (architecture, templates, styles, scripts, data, deployment)
- [README.md](README.md) — project overview and contributor workflow
