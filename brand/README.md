# Brand assets

Visual identity **sources and platform exports**. Nothing in this folder is
published by Hugo — it is deliberately outside `static/` and `assets/` so the
repo cleanly separates "what the website serves" from "what we upload by hand
to LinkedIn, Buy Me a Coffee, GitHub…".

Everything here is derived from `masters/logo_4nchips.svg` and the homepage
banner using `rsvg-convert` (vector → raster) and `magick` (crop, pad,
convert). No AI-generated imagery.

## masters/

**Only true originals live here — everything else in the repo derives from
these two files.**

| File | What it is |
|---|---|
| `logo_4nchips.svg` | The logo, vector, 731×1142 (aspect 0.642). Coloured for **light backgrounds** — use it as-is on white/cream. |
| `banner.png` | The homepage illustration, 9569×3295. |

`brand/masters/` is mounted into Hugo's asset pipeline as `assets/brand`
(see `module.mounts` in `config/_default/hugo.yaml`), so the site derives its
banner WebP variants and its social card straight from the master instead of
keeping a second 25 MB copy. Referenced in templates as `brand/banner.png`.

The site itself does **not** load these files: `layouts/partials/logo.html`
inlines the SVG markup and recolours it at runtime through the `--logo-white`
custom property (`#1A1204` in light mode, `#EEEAD8` in dark). If the logo
changes, update both the master here **and** the inlined markup in
`logo.html`.

## exports/

Upload these by hand; reuse the same file across platforms so the identity
stays consistent instead of re-cropping per site.

| File | Size | Use |
|---|---|---|
| `linkedin-logo-400-*.png` | 400×400 | LinkedIn organisation logo |
| `linkedin-cover-4200x700.jpg` | 4200×700 | LinkedIn page cover |
| `linkedin-post-1200x627.jpg` | 1200×627 | LinkedIn link-share / post image |
| `bmc-avatar-1000-*.png` | 1000×1000 | Buy Me a Coffee avatar |
| `bmc-cover-1500x500.jpg` | 1500×500 | Buy Me a Coffee cover |
| `github-avatar-500-*.png` | 500×500 | GitHub organisation avatar |
| `og-default-1200x630.jpg` | 1200×630 | Reference copy of the social card |
| `banner-3840.webp` | 3840 wide | Optimised banner for slide decks / press use |
| `logo-on-dark.svg` | vector | The **only** recolour needed: the master's `#1A1204` ink swapped for `#EEEAD8` so it reads on dark backgrounds |
| `favicon-48x48.png` | 48×48 | Build input for the multi-resolution `favicon.ico` |

`-dark` = for dark backgrounds, `-cream` = for light backgrounds.

Note the site generates its own OpenGraph image at build time from
`params.defaultSocialImage` (the banner in `assets/`), so `og-default…jpg`
here is a reference copy, not what the site serves.

## What lives elsewhere (and must stay there)

- `static/logos/favicons/` — the 7 files the site actually serves
  (`favicon.ico`, `favicon-16x16`, `favicon-32x32`, `apple-touch-icon`,
  `safari-pinned-tab.svg`, `icon-192`, `icon-512`). Paths are wired in
  `config/_default/hugo.yaml` and `static/site.webmanifest`; moving them
  breaks the site.
- `assets/images/logos/swiss_flag.svg` — used by the header partial.
