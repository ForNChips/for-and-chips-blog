---
title: "Demo: citing references and building a bibliography"
date: 2026-07-01T10:00:00+02:00
lastmod:
type: article
slug: "2026-07-01-demo-citations"
draft: false

authors:
 - id: "alice-dupont"
   affiliations:
      - "Dummy University of Crispville"

description: "Dummy article for the demo site. It shows how the citation system works: cite shortcodes in the prose, a per-article BibTeX file, and an automatically generated bibliography at the end. Every reference here is invented."

tags: [ios, database]
bags:
  demo-case-file: 1

references:
  - crunchy_placeholder_2026
  - chips_field_2025
  - potato_dataset_2024
---

> 📄 This is **dummy content** for the For&Chips demo site. The study it pretends to accompany does not exist.

# Introduction

This placeholder article demonstrates the academic citation workflow. A claim
can be backed by a source, like the entirely fictional finding that crisps
survive database journaling {{< cite "crunchy_placeholder_2026" >}}. Citations
with a locator are supported too {{< cite "chips_field_2025" "p. 42" >}}.

# Method

Each article folder carries its own `references.bib`. The `references:` block
in the frontmatter is regenerated automatically at commit time, so authors only
maintain the BibTeX file and the cite shortcodes. A dataset citation looks the
same as any other {{< cite "potato_dataset_2024" >}}.

# Take-aways

The bibliography below is rendered by a shortcode and lists exactly the works
cited above, formatted consistently in every article.

## Références

{{< bibliography >}}
