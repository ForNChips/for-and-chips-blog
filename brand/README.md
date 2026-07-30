# Brand assets

Visual identity **sources and platform exports**. Nothing in `exports/` is
published by Hugo — it sits outside `static/` and `assets/` so the repo cleanly
separates "what the website serves" from "what we upload by hand to LinkedIn,
Buy Me a Coffee, GitHub…".

Everything is derived from the two masters with `rsvg-convert` (vector →
raster) and `magick` (crop, pad, convert). No AI-generated imagery.

```
brand/
├── masters/          the originals + the two composed lockups
│   ├── logo_4nchips.svg
│   ├── banner.png
│   ├── logo-lockup-horizontal.svg
│   └── logo-lockup-stacked.svg
└── exports/
    ├── logo/         square avatars + the dark-background vector
    ├── lockup/       icon + wordmark, light/dark/transparent
    └── banner/       wide covers, social cards, optimised banner
```

## Regenerating everything

```bash
./scripts/brand_export.sh          # needs: brew install librsvg imagemagick
```

That script is the source of truth — it rewrites `brand/exports/` **and**
`static/logos/favicons/`. The per-asset commands below are what it runs, if
you need a one-off.

Shared values (from `assets/css/extended/vars.scss`):
`CREAM=#F7F5F0` · `DARK=#1F1F1F` · logo ink `#1A1204` · cream ink `#EEEAD8`.

## masters/

**Only true originals live here.**

| File | What it is |
|---|---|
| `logo_4nchips.svg` | The logo, vector, 731×1142 (aspect 0.642). Coloured for **light backgrounds** — use it as-is on white/cream. |
| `banner.png` | The homepage illustration, 9569×3295. |
| `logo-lockup-horizontal.svg` | Icon + "For&Chips" + "digital forensic" + flag, on one line (799×193). Mirrors the site header. |
| `logo-lockup-stacked.svg` | Icon + "For&" over "Chips", no subtitle (389×216). |

The two lockups are **composed** from the logo master and the Atelia webfont by
`scripts/brand_lockups.py`, but live here because everything else derives from
them. Their text is converted to **outlines**, so they render correctly on
machines without Atelia installed (LinkedIn, print, other designers).

```bash
uv run --with 'fonttools[woff]' --with brotli --with uharfbuzz \
    python scripts/brand_lockups.py
```

Tunable constants at the top of that script: `LEAN` / `LEAN_STACKED` (how
closely the chip leans on the F) and the subtitle offset. Two things it gets
right that are easy to miss — Atelia's cap height is 0.7 em, so the title is
set at `icon_height / 0.7` for the F to match the icon; and each glyph's left
side bearing is subtracted from the gap so the *ink* lands where intended.

`brand/masters/` is mounted into Hugo's asset pipeline as `assets/brand`
(see `module.mounts` in `config/_default/hugo.yaml`), so the site derives its
banner WebP variants and its social card straight from the master instead of
keeping a second 25 MB copy. Referenced in templates as `brand/banner.png`.

The site does **not** load the logo file: `layouts/partials/logo.html` inlines
the SVG markup and recolours it at runtime via the `--logo-white` custom
property. If the logo changes, update the master here **and** that inlined
markup.

## exports/logo/

Square canvases with the logo centred at **83 % of the side**. `-cream` for
light backgrounds, `-dark` for dark ones.

| File | Size | Use |
|---|---|---|
| `linkedin-logo-400-*.png` | 400×400 | LinkedIn organisation logo |
| `bmc-avatar-1000-*.png` | 1000×1000 | Buy Me a Coffee avatar |
| `github-avatar-500-*.png` | 500×500 | GitHub organisation avatar |
| `logo-on-dark.svg` | vector | The only recolour needed: master ink → `#EEEAD8` |

```bash
# Any square avatar: SIZE and background colour are the only variables.
SIZE=400; BG='#F7F5F0'                       # use #1F1F1F for the -dark file
rsvg-convert -h $((SIZE*83/100)) brand/masters/logo_4nchips.svg -o /tmp/l.png
magick /tmp/l.png -background "$BG" -gravity center -extent ${SIZE}x${SIZE} out.png

# Dark-background vector — swap the ink only
sed 's/fill:#1A1204/fill:#EEEAD8/' brand/masters/logo_4nchips.svg > logo-on-dark.svg
```

## exports/lockup/

| File | Use |
|---|---|
| `logo-lockup-{horizontal,stacked}-1200-cream.png` | Light backgrounds |
| `logo-lockup-{horizontal,stacked}-1200-dark.png` | Dark backgrounds |
| `logo-lockup-{horizontal,stacked}-1200-transparent.png` | Place over any background |
| `logo-lockup-{horizontal,stacked}-on-dark.svg` | Vector, cream ink |

Horizontal suits email signatures, slide footers and wide profile headers;
stacked suits square-ish placements. 1200px wide covers every social use —
scale down, never up.

```bash
# Raster at any width, on a brand background or transparent
rsvg-convert -w 1200 brand/masters/logo-lockup-horizontal.svg -o out.png
magick out.png -background '#F7F5F0' -flatten out-cream.png

# Dark-background vector — the ink appears as both style: and fill=
sed -e 's/fill:#1A1204/fill:#EEEAD8/g' -e 's/fill="#1A1204"/fill="#EEEAD8"/g' \
    brand/masters/logo-lockup-horizontal.svg > logo-lockup-horizontal-on-dark.svg
```

## exports/banner/

Full-bleed **centre crops** of the banner (no letterboxing), so every platform
shows the same artwork framed to its aspect ratio.

| File | Size | Use |
|---|---|---|
| `linkedin-cover-4200x700.jpg` | 4200×700 | LinkedIn page cover |
| `linkedin-post-1200x627.jpg` | 1200×627 | LinkedIn link-share / post image |
| `bmc-cover-1500x500.jpg` | 1500×500 | Buy Me a Coffee cover |
| `og-default-1200x630.jpg` | 1200×630 | Reference copy of the social card |
| `banner-3840.webp` | 3840×1322 | Optimised banner for slide decks / press use |

```bash
# Any cover / social crop — the ^ makes it fill then centre-crop
magick brand/masters/banner.png -resize 1200x630^ -gravity center \
       -extent 1200x630 -quality 85 og-default-1200x630.jpg

# Optimised full banner (aspect preserved, no crop)
magick brand/masters/banner.png -resize 3840x -quality 85 banner-3840.webp
```

The site generates its **own** OpenGraph image at build time from
`params.defaultSocialImage`, so `og-default-1200x630.jpg` here is a reference
copy for manual use, not what the site serves.

## Favicons (served by the site)

`static/logos/favicons/` holds the 7 files the site serves. Paths are wired in
`config/_default/hugo.yaml` and `static/site.webmanifest` — moving them breaks
the site — but they are still *derived*, so `brand_export.sh` regenerates them:

```bash
# Same square recipe as the avatars, at 16/32/48/180/192/512
magick /tmp/f-16.png /tmp/f-32.png /tmp/f-48.png favicon.ico   # multi-resolution

# Safari pinned tab: flat monochrome silhouette, Safari recolours it itself
sed -E 's/fill:#[0-9a-fA-F]{6}/fill:#000000/g' \
    brand/masters/logo_4nchips.svg > safari-pinned-tab.svg
```

## What lives elsewhere

- `assets/images/logos/swiss_flag.svg` — used by the header partial.
- `assets/images/authors/`, `assets/images/article_list/` — content imagery,
  not brand identity.
