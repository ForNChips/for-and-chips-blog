#!/usr/bin/env python3
"""
Scan posts for {{< cite "key" >}} shortcodes and sync the 'references:'
frontmatter list to match (order of first appearance in the text).

Run locally before committing. Only rewrites the references: block —
the rest of the frontmatter is left byte-for-byte identical.

Usage:
    python scripts/sync_citations.py               # all articles
    python scripts/sync_citations.py FILE...       # specific files
"""

import argparse
import re
import sys
from pathlib import Path

from validate import CITE_RE, ROOT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_cite_keys(body: str) -> list[str]:
    """Return ordered unique keys from {{< cite "key" ... >}} shortcodes."""
    keys: list[str] = []
    seen: set[str] = set()
    for m in CITE_RE.finditer(body):
        key = m.group(1)
        if key not in seen:
            keys.append(key)
            seen.add(key)
    return keys


def split_frontmatter(content: str) -> tuple[str, str] | None:
    """Return (frontmatter_text, body) or None if no YAML front matter."""
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    return content[3:end], content[end + 4:]


def replace_references_block(fm: str, keys: list[str]) -> tuple[str, bool]:
    """Replace the references: block in the frontmatter text. Returns (new_fm, changed)."""
    new_block = ["references:"] + [f"  - {k}" for k in keys] if keys else ["references: []"]

    lines = fm.split("\n")
    result: list[str] = []
    i = 0
    found = False

    while i < len(lines):
        line = lines[i]
        if re.match(r"^references\s*:", line):
            found = True
            result.extend(new_block)
            i += 1
            # Skip continuation lines: indented (any whitespace) or the bare "[]" sentinel.
            while i < len(lines) and (
                (lines[i] and lines[i][0] in " \t") or lines[i].strip() == "[]"
            ):
                i += 1
        else:
            result.append(line)
            i += 1

    if not found:
        result.extend(new_block)

    new_fm = "\n".join(result)
    return new_fm, new_fm != fm


def sync_file(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")
    parts = split_frontmatter(content)
    if parts is None:
        return False

    fm, body = parts
    keys = extract_cite_keys(body)
    new_fm, changed = replace_references_block(fm, keys)

    if not changed:
        return False

    filepath.write_text(f"---{new_fm}\n---{body}", encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Article files to sync. Defaults to every content/articles/**/*.md.",
    )
    args = parser.parse_args()

    files = args.files or sorted(
        p for p in (ROOT / "content" / "articles").rglob("*.md")
        if not p.name.startswith("_")
    )

    if not files:
        print("No articles found.", file=sys.stderr)
        return

    updated = 0
    for filepath in sorted(files):
        rel = filepath.resolve().relative_to(ROOT)
        if sync_file(filepath):
            print(f"  synced   {rel}")
            updated += 1
        else:
            print(f"  ok       {rel}")

    print(f"\n{updated} file(s) updated.")


if __name__ == "__main__":
    main()
