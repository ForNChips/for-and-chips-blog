---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
description: ""
draft: true
---

<!--
HOW A BAG WORKS
================
This file IS the bag's landing page (its intro). It does NOT list articles
itself — articles opt in from their own frontmatter via:

    bags:
      {{ .Name }}: 1     # this article is #1 in the reading order of this bag

The bag layout collects every article whose `bags` map contains this bag's
slug ("{{ .Name }}") and sorts them by the order value.
-->

Short intro for this bag: what the series is about, who it is for, and in
what order to read the articles. The articles below the intro are listed
automatically.
