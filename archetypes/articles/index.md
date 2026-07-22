---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
# lastmod: set automatically or fill manually when the article is updated
lastmod:
type: article
slug: "{{ .Name }}"
draft: true

# --- Authors ---
# Each entry needs an id (matches data/authors.yml) and one or more affiliations.
authors:
  - id: ""
    affiliations:
      - ""

# --- Abstract ---
# Rendered in card lists, the print header, RSS, the JSON search index,
# and as the SEO <meta name="description">.
# Keep it self-contained: no markdown headings, no inline links.
description: ""

# --- Source files ---
# List every forensic artefact file discussed in this article.
# Each entry requires three fields:
#   label        — short human-readable name shown before the path
#   path         — full on-device path to the file
#   datastructure — storage format (e.g. SQLite, plist, JSON, leveldb…)
# Rendered as: 📍 label: path (datastructure: datastructure)
files_path:
  - label: ""
    path: ""
    datastructure: ""

# --- Tags ---
# Lowercase, underscore-separated. Pick from existing tags when possible.
tags: []

# --- Bags ---
# A "bag" is a themed series of articles (e.g. all the iPhone-in-road-accident
# experiments). To put this article in one or more bags, list each bag slug
# (the folder name under content/bags/) followed by this article's reading
# order *within that bag* (1 = first, 2 = second, ...). The order value lets
# the same article sit at a different position in different bags.
#
# Leave the section empty if the article is standalone.
#
# Example:
# bags:
#   iphone-road-accidents: 2
#   ios-fundamentals: 5
bags: {}

# --- Cover image ---
# Place the file at images/cover.png alongside this index.md.
# images/cover.png

# --- References ---
# List BibTeX keys from data/references.yml cited in this article via {{< cite "key" >}}.
references: []
---


