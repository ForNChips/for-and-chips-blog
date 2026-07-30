#!/usr/bin/env bash
# Regenerate every derived brand asset from the two masters.
#
#   ./scripts/brand_export.sh
#
# Inputs  : brand/masters/logo_4nchips.svg  (light-mode colours)
#           brand/masters/banner.png        (9569x3295)
# Outputs : brand/exports/{logo,banner}/    platform assets, not served
#           static/logos/favicons/          served by the site
#
# Requires: librsvg (rsvg-convert) + imagemagick (magick).
#           brew install librsvg imagemagick
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

LOGO=brand/masters/logo_4nchips.svg
BANNER=brand/masters/banner.png
CREAM='#F7F5F0'    # --theme, light palette
DARK='#1F1F1F'     # --theme, dark palette
INK='#1A1204'      # logo ink in the master
CREAM_INK='#EEEAD8'
LOGO_PCT=83        # logo occupies this % of a square canvas

OUT_LOGO=brand/exports/logo
OUT_BANNER=brand/exports/banner
FAV=static/logos/favicons
mkdir -p "$OUT_LOGO" "$OUT_BANNER" "$FAV"

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# ── Logo: square canvas, logo centred at LOGO_PCT of the side ───────────
square() {  # square <size> <bg> <outfile>
  local size=$1 bg=$2 out=$3
  rsvg-convert -h $(( size * LOGO_PCT / 100 )) "$LOGO" -o "$tmp/l.png"
  magick "$tmp/l.png" -background "$bg" -gravity center -extent "${size}x${size}" "$out"
}

# ── Banner: full-bleed centre crop to the target aspect ─────────────────
crop() {    # crop <WxH> <outfile> [quality]
  local wh=$1 out=$2 q=${3:-85}
  magick "$BANNER" -resize "${wh}^" -gravity center -extent "$wh" -quality "$q" "$out"
}

echo "logo → $OUT_LOGO"
square 400  "$CREAM" "$OUT_LOGO/linkedin-logo-400-cream.png"
square 400  "$DARK"  "$OUT_LOGO/linkedin-logo-400-dark.png"
square 1000 "$CREAM" "$OUT_LOGO/bmc-avatar-1000-cream.png"
square 1000 "$DARK"  "$OUT_LOGO/bmc-avatar-1000-dark.png"
square 500  "$CREAM" "$OUT_LOGO/github-avatar-500-cream.png"
square 500  "$DARK"  "$OUT_LOGO/github-avatar-500-dark.png"
# Dark-background variant of the vector: swap only the ink colour.
sed "s/fill:${INK}/fill:${CREAM_INK}/" "$LOGO" > "$OUT_LOGO/logo-on-dark.svg"

echo "banner → $OUT_BANNER"
magick "$BANNER" -resize 3840x -quality 85 "$OUT_BANNER/banner-3840.webp"
crop 1200x630 "$OUT_BANNER/og-default-1200x630.jpg"
crop 1200x627 "$OUT_BANNER/linkedin-post-1200x627.jpg"
crop 4200x700 "$OUT_BANNER/linkedin-cover-4200x700.jpg"
crop 1500x500 "$OUT_BANNER/bmc-cover-1500x500.jpg"

echo "favicons → $FAV"
for s in 16 32 48 180 192 512; do
  square "$s" "$CREAM" "$tmp/f-$s.png"
done
cp "$tmp/f-16.png"  "$FAV/favicon-16x16.png"
cp "$tmp/f-32.png"  "$FAV/favicon-32x32.png"
cp "$tmp/f-180.png" "$FAV/apple-touch-icon.png"
cp "$tmp/f-192.png" "$FAV/icon-192.png"
cp "$tmp/f-512.png" "$FAV/icon-512.png"
magick "$tmp/f-16.png" "$tmp/f-32.png" "$tmp/f-48.png" "$FAV/favicon.ico"
# Safari pinned tab: flat monochrome silhouette (Safari recolours it itself).
sed -E 's/fill:#[0-9a-fA-F]{6}/fill:#000000/g' "$LOGO" > "$FAV/safari-pinned-tab.svg"

echo "done."
