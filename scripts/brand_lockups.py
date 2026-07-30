#!/usr/bin/env python3
"""Build the two logo lockups from the master logo + the Atelia webfont.

    uv run --with 'fonttools[woff]' --with brotli --with uharfbuzz \
        python scripts/brand_lockups.py

Text is converted to outlines (HarfBuzz shapes it, so kerning matches the
website), which keeps the SVGs readable on machines without Atelia installed —
LinkedIn, print shops, other designers.

Proportions mirror layouts/partials/header.html + header.scss:
  logo height == title font-size (both 2.5rem on the site)
  subtitle    == 0.85rem, i.e. 0.34 x the title
  flag height == subtitle height, 0.3rem to its right
"""
from __future__ import annotations

import re
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "static/fonts/Atelia.woff2"
LOGO = ROOT / "brand/masters/logo_4nchips.svg"
FLAG = ROOT / "assets/images/logos/swiss_flag.svg"

INK = "#1A1204"          # master logo ink / --primary in light mode
TITLE = "For&Chips"
SUBTITLE = "digital forensic"

UPM = 1000               # Atelia unitsPerEm
CAP = 0.700              # Atelia sCapHeight / UPM — cap height of "F"
LOGO_ASPECT = 731.0586 / 1141.9217   # 0.6402

# The logo artwork fills its viewBox edge to edge (no internal padding), so a
# capital letter only matches the icon's height when it is set at
# logo_height / CAP. Sizing the text at the icon's height — as the website
# does — leaves the F visibly 30 % shorter.
#
# LEAN is the visible gap between the icon and the first letter, as a fraction
# of the icon height. The glyph's own left side bearing is subtracted from it
# so the *ink* ends up that far apart, which is what reads as "leaning".
# The stacked mark is tighter still — a hair negative, so the chip just grazes
# the F rather than merely sitting near it.
LEAN = 0.03
LEAN_STACKED = -0.006


_TTF_CACHE: Path | None = None


def _plain_ttf() -> Path:
    """HarfBuzz cannot read woff2, so decompress the webfont once to a TTF.

    Without this every glyph shapes to .notdef: correct advances would look
    plausible but no outlines are produced at all.
    """
    global _TTF_CACHE
    if _TTF_CACHE is None:
        import tempfile

        tt = TTFont(FONT)
        tt.flavor = None
        tmp = Path(tempfile.mkdtemp()) / "Atelia.ttf"
        tt.save(tmp)
        _TTF_CACHE = tmp
    return _TTF_CACHE


def shaped_path(text: str, size: float) -> tuple[str, float]:
    """Return (svg path data, advance width) for `text` at `size` px.

    Baseline sits at y=0; glyphs extend upward (negative y), matching SVG's
    downward-positive axis.
    """
    ttf = _plain_ttf()
    blob = hb.Blob.from_file_path(str(ttf))
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)

    tt = TTFont(ttf)
    glyph_order = tt.getGlyphOrder()
    glyph_set = tt.getGlyphSet()

    scale = size / UPM
    parts, cursor = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = glyph_order[info.codepoint]
        pen = SVGPathPen(glyph_set)
        glyph_set[name].draw(pen)
        d = pen.getCommands()
        if d:
            x = (cursor + pos.x_offset) * scale
            y = pos.y_offset * scale
            # flip vertically: font Y is up, SVG Y is down
            parts.append(
                f'<path transform="translate({x:.3f},{y:.3f}) '
                f'scale({scale:.6f},{-scale:.6f})" d="{d}"/>'
            )
        cursor += pos.x_advance
    return "\n    ".join(parts), cursor * scale


def first_lsb(text: str, size: float) -> float:
    """Left side bearing of the first glyph, in px — the built-in whitespace
    between the text origin and where its ink actually starts."""
    tt = TTFont(_plain_ttf())
    gs = tt.getGlyphSet()
    from fontTools.pens.boundsPen import BoundsPen

    pen = BoundsPen(gs)
    gs[tt.getBestCmap()[ord(text[0])]].draw(pen)
    return (pen.bounds[0] if pen.bounds else 0) * size / UPM


def logo_group(x: float, y: float, height: float) -> str:
    """Nest the master logo, scaled to `height`, with its top-left at (x, y)."""
    inner = LOGO.read_text()
    inner = re.sub(r"^.*?<svg[^>]*>", "", inner, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, flags=re.S)
    width = height * LOGO_ASPECT
    return (
        f'<svg x="{x:.3f}" y="{y:.3f}" width="{width:.3f}" height="{height:.3f}" '
        f'viewBox="0 0 731.0586 1141.9217" overflow="visible">{inner}</svg>'
    )


def flag_group(x: float, y: float, size: float) -> str:
    inner = FLAG.read_text()
    inner = re.sub(r"^.*?<svg[^>]*>", "", inner, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, flags=re.S)
    return (
        f'<svg x="{x:.3f}" y="{y:.3f}" width="{size:.3f}" height="{size:.3f}" '
        f'viewBox="0 0 32 32">{inner}</svg>'
    )


def build_horizontal(out: Path, size: float = 100.0) -> None:
    """Icon + title on one line, subtitle + flag beneath — the site header."""
    logo_h = size
    title_size = size / CAP               # cap height of "F" == icon height
    sub_size = size * 0.34                # 0.85rem vs a 2.5rem icon, as on the site
    pad = size * 0.12

    title_d, title_w = shaped_path(TITLE, title_size)
    sub_d, sub_w = shaped_path(SUBTITLE, sub_size)

    logo_w = logo_h * LOGO_ASPECT
    baseline = pad + logo_h               # icon sits on the baseline
    gap = size * LEAN - first_lsb(TITLE, title_size)
    text_x = pad + logo_w + gap

    flag_size = sub_size
    flag_gap = size * 0.12
    sub_baseline = baseline + sub_size * 1.75   # air under the enlarged title
    block_right = text_x + title_w
    sub_x = block_right - (sub_w + flag_gap + flag_size)

    w = pad + logo_w + gap + title_w + pad
    h = sub_baseline + sub_size * 0.28 + pad

    out.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.3f} {h:.3f}"
     width="{w:.3f}" height="{h:.3f}" role="img"
     aria-label="For&amp;Chips — digital forensic">
  <title>For&amp;Chips — digital forensic</title>
  {logo_group(pad, baseline - logo_h, logo_h)}
  <g fill="{INK}" transform="translate({text_x:.3f},{baseline:.3f})">
    {title_d}
  </g>
  <g fill="{INK}" opacity="0.7" transform="translate({sub_x:.3f},{sub_baseline:.3f})">
    {sub_d}
  </g>
  {flag_group(block_right - flag_size, sub_baseline - flag_size * 0.78, flag_size)}
</svg>
""")
    print(f"  {out.relative_to(ROOT)}  {w:.0f}x{h:.0f}")


def build_stacked(out: Path, size: float = 100.0) -> None:
    """"For&" over "Chips", icon spanning both lines, no subtitle."""
    pad = size * 0.12
    leading = size * 0.92                 # baseline-to-baseline

    l1_d, l1_w = shaped_path("For&", size)
    l2_d, l2_w = shaped_path("Chips", size)

    baseline1 = pad + size * 0.75
    baseline2 = baseline1 + leading
    text_w = max(l1_w, l2_w)

    # Icon spans from the first line's cap height to the second line's baseline.
    logo_h = leading + size * CAP
    logo_w = logo_h * LOGO_ASPECT
    # Lean against the text: both lines start with a capital, so use the
    # smaller of the two left bearings to avoid a visual notch.
    gap = logo_h * LEAN_STACKED - min(first_lsb("For&", size), first_lsb("Chips", size))
    text_x = pad + logo_w + gap

    w = text_x + text_w + pad
    h = baseline2 + size * 0.25 + pad

    out.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.3f} {h:.3f}"
     width="{w:.3f}" height="{h:.3f}" role="img" aria-label="For&amp;Chips">
  <title>For&amp;Chips</title>
  {logo_group(pad, baseline2 - logo_h, logo_h)}
  <g fill="{INK}" transform="translate({text_x:.3f},{baseline1:.3f})">
    {l1_d}
  </g>
  <g fill="{INK}" transform="translate({text_x:.3f},{baseline2:.3f})">
    {l2_d}
  </g>
</svg>
""")
    print(f"  {out.relative_to(ROOT)}  {w:.0f}x{h:.0f}")


if __name__ == "__main__":
    dest = ROOT / "brand/masters"
    dest.mkdir(parents=True, exist_ok=True)
    build_horizontal(dest / "logo-lockup-horizontal.svg")
    build_stacked(dest / "logo-lockup-stacked.svg")
