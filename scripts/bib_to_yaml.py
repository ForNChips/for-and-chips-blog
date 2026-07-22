#!/usr/bin/env python3
"""Parse all .bib files in bibliography/ and generate data/references.yml."""

import re
import sys
from pathlib import Path

import bibtexparser
import yaml

ROOT = Path(__file__).parent.parent


def strip_braces(s: object) -> str:
    """Remove LaTeX curly braces from a string."""
    if not s:
        return ""
    return re.sub(r"[{}]", "", str(s)).strip()


def _initial(name_part: str) -> str:
    """
    Build the initials for a single first-name component.

    Hyphenated compounds are preserved: "Jean-Pierre" -> "J.-P."
    while plain names produce a single initial: "Jean" -> "J.".
    """
    if not name_part:
        return ""
    return "-".join(f"{piece[0]}." for piece in name_part.split("-") if piece)


def format_authors(author_string: str) -> str:
    """Convert BibTeX 'Last, First and Last, First' to 'Last, F.; Last, F.'"""
    if not author_string:
        return ""
    formatted: list[str] = []
    for raw in re.split(r"\s+and\s+", author_string):
        author = strip_braces(raw)
        if "," in author:
            last, first = author.split(",", 1)
            initials = " ".join(_initial(part) for part in first.strip().split() if part)
            formatted.append(f"{last.strip()}, {initials}")
        else:
            parts = author.split()
            if len(parts) >= 2:
                formatted.append(f"{parts[-1]}, {_initial(parts[0])}")
            else:
                formatted.append(author)
    return "; ".join(formatted)


def entry_to_dict(entry: dict) -> dict:
    """Convert a bibtexparser entry to a clean reference dict, omitting empty fields."""
    journal = strip_braces(
        entry.get("journal")
        or entry.get("booktitle")
        or entry.get("publisher")
        or entry.get("school")
        or ""
    )

    year_raw = strip_braces(entry.get("year", ""))
    try:
        year: int | str = int(year_raw)
    except (ValueError, TypeError):
        year = year_raw

    fields = {
        "type":     entry.get("ENTRYTYPE", "misc").lower(),
        "authors":  format_authors(entry.get("author", "")),
        "title":    strip_braces(entry.get("title", "")),
        "journal":  journal,
        "volume":   strip_braces(entry.get("volume", "")),
        "number":   strip_braces(entry.get("number", "")),
        "pages":    strip_braces(entry.get("pages", "")),
        "year":     year,
        "doi":      strip_braces(entry.get("doi", "")),
        "url":      strip_braces(entry.get("url", "")),
    }
    return {k: v for k, v in fields.items() if v not in ("", None)}


def main() -> None:
    bib_dir     = ROOT / "bibliography"
    output_file = ROOT / "data" / "references.yml"

    # Two sources: the shared bibliography/ folder, and per-article .bib files
    # colocated with their article (content/articles/<slug>/*.bib). Each article
    # carries its own references so that moving or removing the article folder
    # also moves or removes its bibliography.
    bib_files = sorted(bib_dir.glob("*.bib")) + sorted(
        (ROOT / "content" / "articles").rglob("*.bib")
    )
    if not bib_files:
        print(f"No .bib files found in {bib_dir.relative_to(ROOT)}/", file=sys.stderr)
        sys.exit(0)

    references: dict[str, dict] = {}
    sources:    dict[str, list[str]] = {}
    total = 0

    for bib_file in bib_files:
        with bib_file.open(encoding="utf-8") as f:
            db = bibtexparser.load(f)
        # Display path relative to repo root so per-article .bib files are
        # distinguishable from the shared bibliography/ ones in logs and in
        # the `sources` field of references.yml.
        rel_name = str(bib_file.relative_to(ROOT))
        count = 0
        for entry in db.entries:
            key = entry["ID"]
            sources.setdefault(key, []).append(rel_name)
            if key in references:
                # Same key in multiple .bib files: keep the first occurrence's
                # data and let the sources list expose the duplication. If the
                # contents differ, surface it so the user can reconcile.
                if entry_to_dict(entry) != references[key]:
                    print(
                        f"WARNING: '{key}' in {rel_name} differs from earlier "
                        f"definition in {sources[key][0]} — keeping the first.",
                        file=sys.stderr,
                    )
                continue
            references[key] = entry_to_dict(entry)
            count += 1
            total += 1
        print(f"  {rel_name}: {count} entries")

    # Attach the source list to each reference so the YAML is self-documenting:
    # if you see a bad entry in references.yml, you immediately know which
    # .bib file(s) to fix. Put `sources` first for at-a-glance scanning.
    for key in references:
        references[key] = {"sources": sources[key], **references[key]}

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        # sort_keys=False preserves the .bib file order (and field order
        # inside each entry), so references.yml mirrors the source Zotero
        # export — easier to diff against the .bib when something changes.
        yaml.dump(
            references,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    print(f"\nWrote {total} references → {output_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
