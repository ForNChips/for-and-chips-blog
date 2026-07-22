---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
type: tool
slug: "{{ .Name }}"
draft: true

# --- Abstract ---
# Rendered on the /tools card and as the SEO <meta name="description">.
# Keep it self-contained: no markdown headings, no inline links.
description: ""

# --- Classification ---
# category  — what kind of tool this is (e.g. "CLI", "GUI", "Library", "Script")
# platforms — targets it runs on / analyses (e.g. ["iOS", "Android", "macOS"])
# Both are shown on the card meta line as: category · platform, platform
category: ""
platforms: []

# --- Links ---
# repo    — source repository URL (shown on the tool page)
# website — homepage / documentation URL, if distinct from the repo
repo: ""
website: ""

# --- Tags ---
# Lowercase, underscore-separated. Shared vocabulary with articles: pick from
# existing tags (data/tags.yml) when possible so labels and colours apply.
# Filtering stays per-section — a tag pill on /tools/ filters tools, the same
# tag on /articles/ filters articles.
tags: []

# --- Cover image ---
# Place the file at images/cover.png alongside this index.md.
---
