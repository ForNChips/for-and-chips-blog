---
title: "Demo: figures, captions and copyable code blocks"
date: 2026-07-05T10:00:00+02:00
lastmod:
type: article
slug: "2026-07-05-demo-figures-code"
draft: false

authors:
 - id: "bernard-martin"
   affiliations:
      - "Institute of Invented Evidence"

description: "Dummy article for the demo site. It shows captioned figures, syntax-highlighted code blocks with a copy button, and the reading-progress bar on longer pages. Nothing in here is a real finding."

tags: [android, logs, database]
bags:
  demo-case-file: 2
  demo-crumbs-sampler: 1

files_path:
  - label: "Dummy database"
    path: "/data/data/com.example.crisps/databases/crumbs.db"
    datastructure: "SQLite"

references: []
---

> 📄 This is **dummy content** for the For&Chips demo site. The queries below run against a database that does not exist.

## Introduction

This placeholder article shows how technical material is presented. Figures
always carry a caption and are referenced from the prose, as Figure 1
demonstrates with a placeholder illustration.

{{< figure src="images/example_figure.png"
           alt="Placeholder illustration used by the demo article"
           caption="Figure 1 — A placeholder image standing in for a real chart or screenshot." >}}

## Code blocks

Code snippets are syntax highlighted, follow the light and dark theme, and get
a copy button:

{{<code lang="sql" >}}
-- Entirely fictional query
SELECT crumb_id, flavour, dropped_at
FROM   crumbs
WHERE  flavour = 'salt & vinegar'
ORDER  BY dropped_at DESC;
{{</code >}}

Shell examples work the same way:

{{<code lang="bash" >}}
# Extract the imaginary database
demo-crumb-extractor --input backup.zip --table crumbs --output crumbs.csv
{{</code >}}

## Take-aways

Figures, file-path boxes and code blocks cover most of what a technical
article needs; everything else is plain markdown.
