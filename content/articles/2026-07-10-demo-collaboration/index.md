---
title: "Demo: multi-author articles and cross-references"
date: 2026-07-10T10:00:00+02:00
lastmod:
type: article
slug: "2026-07-10-demo-collaboration"
draft: false

authors:
 - id: "alice-dupont"
   affiliations:
      - "Dummy University of Crispville"
 - id: "bernard-martin"
   affiliations:
      - "Institute of Invented Evidence"
 - id: "claire-lefevre"

description: "Dummy article for the demo site. Three fictional authors co-sign it, which feeds the collaboration graph on the authors page, and it links to its sibling demo articles with the ref shortcode."

tags: [mobile_forensic, location, ios]
bags:
  demo-case-file: 3

references: []
---

> 📄 This is **dummy content** for the For&Chips demo site. The authors are fictional and so is their collaboration.

## Introduction

This placeholder article is co-signed by three fictional authors. Multi-author
articles feed the collaboration graph on the authors page, where each shared
publication becomes an edge between chips.

## Cross-references

Articles never link each other with relative markdown paths; they use a
shortcode that survives slug changes. See
{{< ref "articles/2026-07-01-demo-citations" >}} for the citation workflow and
{{< ref "articles/2026-07-05-demo-figures-code" "the figures and code demo" >}}
for technical presentation.

## Take-aways

Shared tags between the demo articles also populate the article graph, which
draws one node per article and connects those with overlapping flavours.
