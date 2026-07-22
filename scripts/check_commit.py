#!/usr/bin/env python3
"""
Validate articles being committed.

Receives a list of article paths on argv (typically the staged set)
and runs strict per-article checks on every article whose frontmatter
has draft: false.

For each non-draft article:
  1. Sync the references: frontmatter block from {{< cite >}} shortcodes
  2. Run strict validation
  3. If everything passes, re-stage the synced files so the sync lands
     in the same commit. On any failure, leave the working tree as-is
     (no files re-staged) so the user can fix and retry.

Drafts are skipped entirely so commits that are still WIP stay fast.

Exit code 0 = all clear (no work, or every non-draft article passed)
Exit code 1 = at least one article failed
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Ensure dependencies are installed using uv
try:
    import yaml
except ImportError:
    root = Path(__file__).parent.parent
    subprocess.run(
        ["uv", "pip", "install", "-q", "pyyaml"],
        cwd=root,
        check=True,
    )

from validate import (
    Findings,
    ROOT,
    check_article,
    load_yaml,
    parse_frontmatter,
)
from sync_citations import sync_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict per-article validation for the pre-commit hook.")
    parser.add_argument("paths", nargs="+", type=Path, help="Staged article files.")
    args = parser.parse_args()

    paths = [p.resolve() for p in args.paths if p.exists() and p.suffix == ".md"]
    if not paths:
        sys.exit(0)

    setup = Findings()
    authors_data    = load_yaml(ROOT / "data" / "authors.yml",    setup)
    references_data = load_yaml(ROOT / "data" / "references.yml", setup)
    tags_data       = load_yaml(ROOT / "data" / "tags.yml",       setup)
    if setup.has_errors:
        setup.report()
        sys.exit(1)

    failed  = 0
    skipped = 0
    checked = 0
    pending_stage: list[Path] = []

    for path in paths:
        findings = Findings()
        fm, _ = parse_frontmatter(path, findings)
        if not fm:
            continue

        # Treat "missing" the same as "draft: true" — be conservative.
        if fm.get("draft", True):
            skipped += 1
            continue

        if sync_file(path):
            print(f"  ↺  {path.relative_to(ROOT)} — references: synced")
            pending_stage.append(path)

        check_article(path, findings, authors_data, references_data, tags_data, strict=True)

        if findings.has_errors:
            print(f"\n✖  {path.relative_to(ROOT)}")
            findings.report()
            failed += 1
        else:
            checked += 1

    print(
        f"\npre-commit: {checked} checked, {skipped} draft(s) skipped, "
        f"{failed} failed"
    )

    if failed:
        # Leave synced files in the working tree but unstaged: the user can
        # review, fix, and re-stage manually.
        print("Fix the errors above before committing (or set draft: true to defer).")
        if pending_stage:
            print("Note: references: blocks were updated on disk but not re-staged.")
        sys.exit(1)

    for path in pending_stage:
        subprocess.run(["git", "add", str(path)], check=True)


if __name__ == "__main__":
    main()
