#!/usr/bin/env python3
"""
Validate consistency across articles, authors, and data files.

Exit code 0 = OK (warnings allowed)
Exit code 1 = errors found
"""

import datetime
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
ARTICLES_GLOB = "content/articles/**/*.md"

SLUG_RE  = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
IMG_RE   = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
CITE_RE  = re.compile(r'\{\{<\s*cite\s+"([^"]+)"')

# Figure shortcodes. FIGURE_RE grabs the whole opening tag (they often span
# several lines, hence DOTALL + non-greedy) so the attributes can then be read
# from it individually; FIGREF_RE grabs the id an in-text cross-reference
# points at. Kept in sync with layouts/shortcodes/{figure,figref}.html.
FIGURE_RE   = re.compile(r"\{\{<\s*figure\s.*?>\}\}", re.DOTALL)
FIG_SRC_RE  = re.compile(r'\bsrc="([^"]+)"')
FIG_ID_RE   = re.compile(r'\bid="([^"]+)"')
FIG_NONUM_RE = re.compile(r'numbered="false"')
FIGREF_RE   = re.compile(r'\{\{<\s*figref\s+"([^"]+)"')


# ---------------------------------------------------------------------------
# Findings: accumulator passed through every check.
# Replaces the previous global ERRORS/WARNINGS/INFO + reset_findings() pattern.
# ---------------------------------------------------------------------------

@dataclass
class Findings:
    errors:   list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info:     list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.info.append(msg)

    def fail_or_warn(self, msg: str, *, strict: bool) -> None:
        (self.error if strict else self.warn)(msg)

    def merge(self, other: "Findings") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def report(self) -> None:
        print(f"\n{'═' * 50}")
        for msg in sorted(self.errors):
            print(f"  ✖  {msg}")
        for msg in sorted(self.warnings):
            print(f"  ▲  {msg}")
        for msg in sorted(self.info):
            print(f"  ·  {msg}")
        print(f"\n  {len(self.errors)} error(s)   "
              f"{len(self.warnings)} warning(s)   {len(self.info)} info")
        print(f"{'═' * 50}\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath: Path, findings: Findings) -> tuple[dict, str]:
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as e:
        findings.error(f"[{filepath}] Cannot read file: {e}")
        return {}, ""

    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        findings.error(f"[{filepath}] YAML parse error: {e}")
        return {}, parts[2]
    return fm, parts[2]


def load_yaml(filepath: Path, findings: Findings) -> dict:
    try:
        with open(filepath, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        findings.error(f"[{filepath.relative_to(ROOT)}] File not found")
        return {}
    except yaml.YAMLError as e:
        findings.error(f"[{filepath.relative_to(ROOT)}] YAML parse error: {e}")
        return {}


def section(title: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def list_articles() -> list[Path]:
    return sorted(
        p for p in (ROOT / "content" / "articles").rglob("*.md")
        if not p.name.startswith("_")
    )


def list_bags() -> list[Path]:
    """Each bag is a directory under content/bags/ containing an _index.md."""
    bags_dir = ROOT / "content" / "bags"
    if not bags_dir.is_dir():
        return []
    return sorted(
        sub / "_index.md"
        for sub in bags_dir.iterdir()
        if sub.is_dir() and (sub / "_index.md").exists()
    )


def known_bag_slugs() -> set[str]:
    """Set of valid bag slugs (folder names under content/bags/)."""
    bags_dir = ROOT / "content" / "bags"
    if not bags_dir.is_dir():
        return set()
    return {sub.name for sub in bags_dir.iterdir() if sub.is_dir() and (sub / "_index.md").exists()}


def _rel(filepath: Path) -> Path:
    return filepath.relative_to(ROOT)


def _coerce_date(value: object) -> datetime.datetime | None:
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time())
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Per-article checks (shared with check_commit.py and CI)
# ---------------------------------------------------------------------------

def check_article(
    filepath: Path,
    findings: Findings,
    authors_data: dict,
    references_data: dict,
    tags_data: dict,
    *,
    strict: bool = False,
) -> None:
    """
    Validate a single article. When strict=True, missing 'description' and
    'authors' are errors instead of warnings (used at commit time).
    """
    rel = _rel(filepath)
    fm, body = parse_frontmatter(filepath, findings)
    keyword_colors = tags_data.get("keyword_color", {})

    if not fm:
        findings.fail_or_warn(f"[{rel}] Empty or missing frontmatter", strict=strict)
        return

    # Required fields
    if not fm.get("title"):
        findings.error(f"[{rel}] Missing required field: 'title'")
    if not fm.get("date"):
        findings.error(f"[{rel}] Missing required field: 'date'")
    if not fm.get("description"):
        findings.fail_or_warn(
            f"[{rel}] Missing 'description' (used as abstract in cards, RSS, search, and SEO)",
            strict=strict,
        )

    # Date sanity
    raw_date = fm.get("date")
    if raw_date:
        date_obj = _coerce_date(raw_date)
        if date_obj and date_obj > datetime.datetime.now(date_obj.tzinfo):
            findings.warn(f"[{rel}] Date {raw_date} is in the future")

    # Slug format
    slug = fm.get("slug") or filepath.parent.name
    if not SLUG_RE.match(slug):
        findings.warn(f"[{rel}] Slug '{slug}' should be lowercase ASCII (letters, digits, - or _)")

    # Authors
    post_authors = fm.get("authors") or []
    if not post_authors:
        findings.fail_or_warn(f"[{rel}] No authors defined", strict=strict)
    for entry in post_authors:
        if not isinstance(entry, dict):
            findings.error(f"[{rel}] Author entry must be a dict with an 'id' key, got: {entry!r}")
            continue
        author_id = entry.get("id")
        if not author_id:
            findings.error(f"[{rel}] Author entry is missing 'id'")
        elif author_id not in authors_data:
            findings.error(f"[{rel}] Author '{author_id}' not found in data/authors.yml")

    # files_path — list of {label, path, datastructure}
    if "file_path" in fm:
        findings.error(
            f"[{rel}] Deprecated key 'file_path' — rename to 'files_path' (list of {{label, path, datastructure}})"
        )
    for i, entry in enumerate(fm.get("files_path") or []):
        if not isinstance(entry, dict):
            findings.error(f"[{rel}] files_path[{i}] must be a mapping, got: {entry!r}")
            continue
        for required_key in ("label", "path", "datastructure"):
            if not entry.get(required_key):
                findings.error(f"[{rel}] files_path[{i}] missing required field '{required_key}'")

    # Tags — warn if no color defined
    for tag in fm.get("tags") or []:
        if str(tag) not in keyword_colors:
            findings.warn(f"[{rel}] Tag '{tag}' has no color entry in data/tags.yml")

    # Bags — { <bag-slug>: <order> }. Each slug must resolve to a bag, each
    # value must be a positive integer. Articles can legitimately not belong
    # to any bag, so an empty map (or missing key) is fine.
    bags_field = fm.get("bags")
    if bags_field is not None and bags_field != {}:
        if not isinstance(bags_field, dict):
            findings.error(
                f"[{rel}] 'bags' must be a map of {{<bag-slug>: <order>}}, got: {type(bags_field).__name__}"
            )
        else:
            valid_bag_slugs = known_bag_slugs()
            for bag_slug, order in bags_field.items():
                bag_slug_str = str(bag_slug)
                if bag_slug_str not in valid_bag_slugs:
                    findings.error(
                        f"[{rel}] Bag '{bag_slug_str}' not found — expected content/bags/{bag_slug_str}/_index.md"
                    )
                if not isinstance(order, int) or isinstance(order, bool) or order < 1:
                    findings.error(
                        f"[{rel}] Bag '{bag_slug_str}' order must be a positive integer, got: {order!r}"
                    )

    # References declared in frontmatter
    declared_refs = set(fm.get("references") or [])
    for ref_key in declared_refs:
        if ref_key not in references_data:
            findings.error(f"[{rel}] Reference '{ref_key}' not found in data/references.yml")

    # Citations in body must match references: block
    body_refs = set(CITE_RE.findall(body))
    for key in body_refs - declared_refs:
        findings.error(f"[{rel}] Cite shortcode '{key}' not declared in references: (run sync_citations.py)")

    # Per-article .bib must contain exactly the cited keys (strict mode only).
    # Each article folder may carry its own .bib alongside the index — the
    # invariant is "what's cited == what's in the local .bib", no more, no
    # less. Only enforced when the article is being published (strict),
    # because drafts often cite ahead of the bibliography.
    if strict:
        post_dir = filepath.parent
        local_bibs = sorted(post_dir.glob("*.bib"))
        local_keys: set[str] = set()
        bib_key_re = re.compile(r"^\s*@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
        for bib_path in local_bibs:
            try:
                local_keys.update(
                    bib_key_re.findall(bib_path.read_text(encoding="utf-8"))
                )
            except OSError as e:
                findings.error(f"[{_rel(bib_path)}] Cannot read file: {e}")

        if body_refs and not local_bibs:
            findings.error(
                f"[{rel}] Article cites references but has no .bib in {post_dir.relative_to(ROOT)}/"
            )
        else:
            for key in body_refs - local_keys:
                findings.error(
                    f"[{rel}] Cited key '{key}' missing from local .bib in {post_dir.relative_to(ROOT)}/"
                )
            for key in local_keys - body_refs:
                findings.error(
                    f"[{rel}] Local .bib in {post_dir.relative_to(ROOT)}/ contains '{key}' but it is never cited"
                )

    # Image references in body must exist on disk — markdown images and the
    # src of every figure shortcode alike.
    post_dir = filepath.parent
    figure_tags = FIGURE_RE.findall(body)
    figure_srcs = [m.group(1) for m in (FIG_SRC_RE.search(t) for t in figure_tags) if m]
    for src in IMG_RE.findall(body) + figure_srcs:
        if src.startswith(("http://", "https://", "data:")):
            continue
        target = (post_dir / src).resolve()
        if not target.exists():
            findings.error(f"[{rel}] Image reference '{src}' not found on disk")

    # Figure ids and cross-references. An id is what {{< figref >}} resolves
    # against, so a duplicate or a dangling one silently sends the reader to
    # the wrong figure (or nowhere) — both are errors, not style issues.
    figure_ids: list[str] = []
    for tag in figure_tags:
        id_match = FIG_ID_RE.search(tag)
        if not id_match:
            continue
        if FIG_NONUM_RE.search(tag):
            findings.error(
                f"[{rel}] Figure id '{id_match.group(1)}' on a numbered=\"false\" figure — "
                "unnumbered figures get no anchor and cannot be referenced"
            )
            continue
        figure_ids.append(id_match.group(1))

    for fig_id in sorted({i for i in figure_ids if figure_ids.count(i) > 1}):
        findings.error(f"[{rel}] Duplicate figure id '{fig_id}'")

    # A figure with no id is numbered by its src, so the same image used twice
    # without ids makes the second occurrence display the first one's number.
    numbered = [
        (m.group(1), bool(FIG_ID_RE.search(t)))
        for t, m in ((t, FIG_SRC_RE.search(t)) for t in figure_tags)
        if m and not FIG_NONUM_RE.search(t)
    ]
    all_srcs = [src for src, _ in numbered]
    for src in sorted(
        {src for src, has_id in numbered if not has_id and all_srcs.count(src) > 1}
    ):
        findings.error(
            f"[{rel}] Image '{src}' is used by several figures with no id — "
            "give each of them a distinct id, or they share one figure number"
        )

    for fig_id in sorted(set(FIGREF_RE.findall(body)) - set(figure_ids)):
        findings.error(f"[{rel}] figref '{fig_id}' has no matching figure id on this page")

    # Cover image (info only)
    if not list(post_dir.glob("images/cover.*")):
        findings.note(f"[{rel}] No cover image — default thumbnail will be used")


# ---------------------------------------------------------------------------
# Repo-wide checks
# ---------------------------------------------------------------------------

def check_articles(
    findings: Findings,
    authors_data: dict,
    references_data: dict,
    tags_data: dict,
) -> None:
    section("Articles")
    slugs: dict[str, Path] = {}
    for filepath in list_articles():
        rel = _rel(filepath)
        fm, _ = parse_frontmatter(filepath, findings)
        if not fm:
            findings.warn(f"[{rel}] Empty or missing frontmatter")
            continue

        if fm.get("draft"):
            findings.note(f"[{rel}] Draft — will not appear in production build")

        check_article(filepath, findings, authors_data, references_data, tags_data, strict=False)

        slug = fm.get("slug") or filepath.parent.name
        if slug in slugs:
            findings.error(f"[{rel}] Duplicate slug '{slug}' — also used by {slugs[slug]}")
        else:
            slugs[slug] = rel


def check_authors(findings: Findings, authors_data: dict, tags_data: dict) -> None:
    section("Authors (data/authors.yml)")
    keyword_colors = tags_data.get("keyword_color", {})
    photos_dir = ROOT / "assets" / "images" / "authors"

    for author_id, author in authors_data.items():
        prefix = f"[authors.yml / {author_id}]"

        if not isinstance(author, dict):
            findings.error(f"{prefix} Entry is not a valid mapping")
            continue

        for required in ("first_name", "last_name"):
            if not author.get(required):
                findings.error(f"{prefix} Missing required field: '{required}'")

        photo = (author.get("photo") or "").strip()
        if photo:
            if not (photos_dir / photo).exists():
                findings.error(f"{prefix} Photo '{photo}' not found in assets/images/authors/")
        else:
            findings.warn(f"{prefix} No 'photo' defined — default image will be used")

        for kw in author.get("keywords") or []:
            if str(kw) not in keyword_colors:
                findings.warn(f"{prefix} Keyword '{kw}' has no color entry in data/tags.yml")

        for link_type, url in (author.get("links") or {}).items():
            if url and not str(url).startswith(("http://", "https://")):
                findings.warn(f"{prefix} Link '{link_type}' doesn't look like a valid URL: '{url}'")


def check_references(findings: Findings, references_data: dict) -> None:
    section("References (data/references.yml)")
    if not references_data:
        findings.note("[references.yml] File is empty — run scripts/bib_to_yaml.py to populate it")
        return

    for ref_key, entry in references_data.items():
        prefix = f"[references.yml / {ref_key}]"
        if not isinstance(entry, dict):
            findings.error(f"{prefix} Entry is not a valid mapping")
            continue
        for required in ("title", "authors", "year"):
            if not entry.get(required):
                findings.error(f"{prefix} Missing required field: '{required}'")


def check_bags(findings: Findings) -> None:
    """
    Validate each bag's _index.md and the consistency of its member articles.

    - Each bag must have a title and a description.
    - Within a single bag, no two articles may claim the same order value
      (otherwise the bag page renders them in an arbitrary order).
    - Bags with no member articles are surfaced as info notes.
    """
    section("Bags")

    bag_paths = list_bags()
    if not bag_paths:
        findings.note("[content/bags] No bags defined yet")
        return

    # Index articles by bag slug → list of (article_path, order)
    bag_members: dict[str, list[tuple[Path, int]]] = {}
    for article_path in list_articles():
        fm, _ = parse_frontmatter(article_path, findings)
        bags_field = fm.get("bags")
        if not isinstance(bags_field, dict):
            continue
        for bag_slug, order in bags_field.items():
            if not isinstance(order, int) or isinstance(order, bool):
                continue  # invalid order already reported by check_article
            bag_members.setdefault(str(bag_slug), []).append((article_path, order))

    for bag_path in bag_paths:
        rel = _rel(bag_path)
        bag_slug = bag_path.parent.name
        fm, _ = parse_frontmatter(bag_path, findings)

        if not fm:
            findings.error(f"[{rel}] Empty or missing frontmatter")
            continue

        if not fm.get("title"):
            findings.error(f"[{rel}] Missing required field: 'title'")
        if not fm.get("description"):
            findings.warn(f"[{rel}] Missing 'description' (shown on the /bags/ index card)")

        if fm.get("draft"):
            findings.note(f"[{rel}] Draft — will not appear in production build")

        members = bag_members.get(bag_slug, [])
        if not members:
            findings.note(f"[{rel}] Bag has no articles yet")
            continue

        # Duplicate-order detection within this bag
        seen: dict[int, Path] = {}
        for art_path, order in members:
            if order in seen:
                findings.error(
                    f"[{rel}] Two articles claim order={order} in bag '{bag_slug}': "
                    f"{seen[order].relative_to(ROOT)} and {art_path.relative_to(ROOT)}"
                )
            else:
                seen[order] = art_path


def check_orphans(
    findings: Findings,
    authors_data: dict,
    references_data: dict,
    tags_data: dict,
) -> None:
    """Surface unused entries across data files — info only."""
    section("Orphans")

    cited_authors: set[str] = set()
    cited_refs:    set[str] = set()
    used_tags:     set[str] = set()
    used_bags:     set[str] = set()

    for filepath in list_articles():
        fm, body = parse_frontmatter(filepath, findings)
        if fm.get("draft"):
            continue
        for entry in fm.get("authors") or []:
            if isinstance(entry, dict) and entry.get("id"):
                cited_authors.add(entry["id"])
        for tag in fm.get("tags") or []:
            used_tags.add(str(tag))
        bags_field = fm.get("bags")
        if isinstance(bags_field, dict):
            for bag_slug in bags_field:
                used_bags.add(str(bag_slug))
        cited_refs.update(fm.get("references") or [])
        cited_refs.update(CITE_RE.findall(body))

        # Per-post orphan images: files in images/ not referenced by body or cover
        post_dir = filepath.parent
        images_dir = post_dir / "images"
        if images_dir.is_dir():
            body_srcs = IMG_RE.findall(body) + [
                m.group(1)
                for m in (FIG_SRC_RE.search(t) for t in FIGURE_RE.findall(body))
                if m
            ]
            referenced = {
                (post_dir / src).resolve()
                for src in body_srcs
                if not src.startswith(("http://", "https://", "data:"))
            }
            for img in images_dir.iterdir():
                if img.name.startswith("cover."):
                    continue
                if img.resolve() not in referenced:
                    findings.note(f"[{_rel(img)}] Image not referenced in any article body")

    for author_id in authors_data:
        if author_id not in cited_authors:
            findings.note(f"[authors.yml / {author_id}] Has no published articles yet")

    for ref_key in references_data:
        if ref_key not in cited_refs:
            findings.note(f"[references.yml / {ref_key}] Reference never cited")

    for tag in tags_data.get("keyword_color") or {}:
        if str(tag) not in used_tags:
            findings.note(f"[tags.yml / {tag}] Tag never used")

    for bag_slug in known_bag_slugs():
        if bag_slug not in used_bags:
            findings.note(f"[content/bags/{bag_slug}] No published article references this bag")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("For&Chips — content validation")
    findings = Findings()

    authors_data    = load_yaml(ROOT / "data" / "authors.yml",    findings)
    references_data = load_yaml(ROOT / "data" / "references.yml", findings)
    tags_data       = load_yaml(ROOT / "data" / "tags.yml",       findings)

    if not authors_data and not findings.has_errors:
        findings.warn("[data/authors.yml] File is empty")
    if not tags_data:
        findings.warn("[data/tags.yml] File is empty or missing — no keyword colors will apply")

    check_articles  (findings, authors_data, references_data, tags_data)
    check_authors   (findings, authors_data, tags_data)
    check_references(findings, references_data)
    check_bags      (findings)
    check_orphans   (findings, authors_data, references_data, tags_data)

    findings.report()

    if findings.has_errors:
        print("Fix errors before deploying.")
        sys.exit(1)
    elif findings.warnings:
        print("Checks passed — warnings worth reviewing.")
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()
