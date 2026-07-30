# Brand assets

Visual identity **sources and platform exports**. Nothing in this folder is
published by Hugo — it is deliberately outside `static/` and `assets/` so the
repo cleanly separates "what the website serves" from "what we upload by hand
to LinkedIn, Buy Me a Coffee, GitHub…".

Everything here is derived from `masters/logo_4nchips.svg` and the homepage
banner using `rsvg-convert` (vector → raster) and `magick` (crop, pad,
convert). No AI-generated imagery.

## masters/

| File | What it is |
|---|---|
| `logo_4nchips.svg` | **The source of truth.** Vector, 731×1142, aspect 0.642. |
| `logo-on-light.svg` | Variant for light backgrounds — the themed fill recoloured to `#1A1204`. |
| `logo-on-dark.svg` | Variant for dark backgrounds — the themed fill recoloured to `#EEEAD8`. |
| `favicon-48x48.png` | Build input for the multi-resolution `favicon.ico`, not served on its own. |
| `legacy_logo_4nchips_*.svg` | Earlier variants of unknown origin, kept for reference. Prefer the master above. |

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
| `banner-3840.webp` | 3840 wide | Optimised banner master |

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
- `assets/images/homepage/banner.png` — the banner master Hugo processes.
