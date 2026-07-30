---
title: "Demo: figure rows, numbering and cross-references"
date: 2026-07-28T10:00:00+02:00
lastmod:
type: article
slug: "2026-07-28-demo-figure-rows"
draft: false

authors:
 - id: "bernard-martin"
   affiliations:
      - "Institute of Invented Evidence"

description: "Dummy article for the demo site. It shows how several figures are placed on one row with their captions aligned, how figure numbers are generated automatically, and how the prose refers to a figure by name rather than by a hand-typed number."

tags: [ios, location]

references: []
---

> 📄 This is **dummy content** for the For&Chips demo site. The panels below
> are placeholders, not real data.

## Several figures on one row

Related panels belong side by side. The `figrow` shortcode places them on a
single row and keeps every caption starting on the same line, even when the
images differ in height, which is exactly what a markdown table could not do.
The three phases used in the segmentation are shown in {{< figref "seg-straight" >}}
to {{< figref "seg-junction" >}}.

{{< figrow >}}
{{< figure src="images/segment_straight.svg" alt="Placeholder road panel with the straight approach highlighted" id="seg-straight" caption="Straight-line section, before the curve." >}}
{{< figure src="images/segment_corner.svg" alt="Placeholder road panel with the curve highlighted" id="seg-corner" caption="Cornering section, where the trajectory bends and the recorded points start to drift away from the driven path." >}}
{{< figure src="images/segment_junction.svg" alt="Placeholder road panel with the junction highlighted" id="seg-junction" caption="Junction section." >}}
{{< /figrow >}}

Numbers are never typed by hand: each figure takes the next number in document
order, so inserting a panel renumbers the whole page (and every reference to
it) on the next build.

## Uneven columns

Two panels of different importance can share a row unequally with
`widths="2fr 1fr"`, as in {{< figref "pair-wide" >}} and
{{< figref "pair-detail" >}}.

{{< figrow widths="2fr 1fr" >}}
{{< figure src="images/single_wide.svg" alt="Placeholder wide overview panel" id="pair-wide" caption="Overview of the approach." >}}
{{< figure src="images/segment_corner.svg" alt="Placeholder detail panel" id="pair-detail" caption="Detail of the curve." >}}
{{< /figrow >}}

## A single figure

A lone figure is written the same way and keeps the full body width, as
{{< figref "solo" >}} shows. Referring to it from the prose is what makes the
figure part of the argument rather than decoration, so every figure should be
mentioned at least once, here for instance as {{< figref "solo" "the overview panel" >}}.

{{< figure src="images/single_wide.svg"
           alt="Placeholder overview panel used on its own"
           id="solo"
           caption="A single full-width figure, numbered in the same sequence as the panels above." >}}
