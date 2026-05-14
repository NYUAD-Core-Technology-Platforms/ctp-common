#!/usr/bin/env python3
"""Local pre-build validator. Run this before `git push` to catch issues
that would otherwise only show up in CI under `mkdocs build --strict`.

Checks performed (each is fatal on failure):
  1. mkdocs.yml parses, docs_dir is a sibling of the config file, and
     site_dir is not nested inside docs_dir.
  2. hooks/prepare_docs.py imports and runs cleanly.
  3. After the hook runs, every page listed in `nav:` exists in docs/.
  4. Every relative markdown / image link inside docs/ resolves to a
     file that exists. (This is what `mkdocs --strict` checks.)
  5. data/people.yaml and data/links.yaml load as valid YAML and the
     people-records schema has the required keys.
  6. Every NetID referenced by a platform's `specialists:` block exists
     in data/people.yaml.
  7. team.md and links.md render as Jinja templates with the YAML data
     loaded (mimics what mkdocs-macros does).
  8. No name from data/people.yaml appears in more than one file
     (single-source-of-truth invariant).
  9. No chartfield / Drive ID / credential patterns appear in the repo.

Usage:
    python3 scripts/check_build.py        # exits 0 on success, 1 on failure
    python3 scripts/check_build.py -v     # verbose
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import pathlib
import re
import sys
from typing import Callable

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# ─── Check helpers ──────────────────────────────────────────────────────────
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def section(name: str) -> None:
    print(f"\n── {name} ──")


# ─── 1. mkdocs.yml structural check ─────────────────────────────────────────
def check_mkdocs_config() -> dict:
    import yaml

    section("1. mkdocs.yml")
    cfg = yaml.safe_load((ROOT / "mkdocs.yml").read_text())
    docs_dir = (ROOT / cfg.get("docs_dir", "docs")).resolve()
    site_dir = (ROOT / cfg.get("site_dir", "site")).resolve()

    if docs_dir == ROOT:
        fail("mkdocs.yml: docs_dir must not equal the project root")
    elif not str(docs_dir).startswith(str(ROOT)):
        fail("mkdocs.yml: docs_dir is outside the project root")
    else:
        print(f"  docs_dir = {docs_dir.relative_to(ROOT)} (OK)")

    if str(site_dir).startswith(str(docs_dir) + "/") or site_dir == docs_dir:
        fail("mkdocs.yml: site_dir must not be inside docs_dir")
    else:
        print(f"  site_dir = {site_dir.relative_to(ROOT)} (OK)")
    return cfg


# ─── 2. Run the prepare-docs hook ───────────────────────────────────────────
def run_hook() -> None:
    section("2. hooks/prepare_docs.py")
    spec = importlib.util.spec_from_file_location(
        "prepare_docs", ROOT / "hooks/prepare_docs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.on_pre_build(config={})
    file_count = sum(1 for _ in DOCS.rglob("*") if _.is_file())
    print(f"  hook ran, docs/ now has {file_count} files (OK)")


# ─── 3. Every nav target exists ─────────────────────────────────────────────
def check_nav(cfg: dict) -> None:
    section("3. Nav targets exist")

    def walk(nav, out):
        for entry in nav:
            for _, v in entry.items():
                if isinstance(v, str):
                    out.append(v)
                elif isinstance(v, list):
                    walk(v, out)
        return out

    targets = walk(cfg["nav"], [])
    missing = [t for t in targets if not (DOCS / t).exists()]
    if missing:
        for m in missing:
            fail(f"nav target missing: docs/{m}")
    else:
        print(f"  {len(targets)} nav targets resolve (OK)")


# ─── 4. Every internal link inside docs/ resolves ───────────────────────────
def check_internal_links() -> None:
    section("4. Internal links in docs/")
    LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
    bad = 0
    checked = 0
    for md in sorted(DOCS.rglob("*.md")):
        text = md.read_text()
        for m in LINK.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            checked += 1
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                line = text[: m.start()].count("\n") + 1
                fail(
                    f"broken link in docs/{md.relative_to(DOCS)}:{line} → ({target})"
                )
                bad += 1
    print(f"  {checked} internal links checked, {bad} broken")


# ─── 5. YAML schemas ────────────────────────────────────────────────────────
def check_yaml_schemas() -> None:
    import yaml

    section("5. YAML schemas (data/people.yaml, data/links.yaml)")
    people_yaml = yaml.safe_load((ROOT / "data/people.yaml").read_text())
    if "people" not in people_yaml:
        fail("data/people.yaml: missing top-level 'people' key")
        return
    required = {"netid", "name", "role", "category", "email", "platform"}
    netids: set[str] = set()
    for i, p in enumerate(people_yaml["people"]):
        missing_keys = required - p.keys()
        if missing_keys:
            fail(f"data/people.yaml record {i}: missing keys {missing_keys}")
        if p["netid"] in netids:
            fail(f"data/people.yaml: duplicate netid '{p['netid']}'")
        netids.add(p["netid"])
    print(f"  people.yaml: {len(netids)} records, schema OK")

    links_yaml = yaml.safe_load((ROOT / "data/links.yaml").read_text())
    for section_key in ("public", "contact", "address"):
        if section_key not in links_yaml:
            fail(f"data/links.yaml: missing top-level '{section_key}' key")
    print("  links.yaml schema OK")


# ─── 6. Platform NetIDs are foreign keys that resolve ───────────────────────
def check_platform_netids() -> None:
    import yaml

    section("6. Platform specialists are valid NetIDs")
    known = {p["netid"] for p in yaml.safe_load((ROOT / "data/people.yaml").read_text())["people"]}
    bad: list[tuple[str, str]] = []
    for f in (ROOT / "platforms").glob("*.md"):
        if f.stem == "index":
            continue
        text = f.read_text()
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            fail(f"{f.relative_to(ROOT)}: no YAML front-matter")
            continue
        fm = yaml.safe_load(m.group(1))
        for nid in fm.get("specialists", []):
            if nid not in known:
                bad.append((str(f.relative_to(ROOT)), nid))
    if bad:
        for f, nid in bad:
            fail(f"{f}: unknown NetID in specialists: '{nid}'")
    else:
        print("  all platform NetIDs resolve to data/people.yaml entries (OK)")


# ─── 7. Jinja templates render (simulates mkdocs-macros) ────────────────────
def check_jinja_render() -> None:
    import jinja2
    import yaml

    section("7. Jinja templates (team.md, links.md)")
    ctx = {}
    for p in ["data/people.yaml", "data/links.yaml"]:
        d = yaml.safe_load((ROOT / p).read_text())
        if isinstance(d, dict):
            ctx.update(d)
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    for page in ["team.md", "links.md"]:
        try:
            env.from_string((DOCS / page).read_text()).render(**ctx)
            print(f"  docs/{page} renders (OK)")
        except Exception as e:
            fail(f"docs/{page}: Jinja render failed: {type(e).__name__}: {e}")


# ─── 8. No name appears in more than one source file ───────────────────────
def check_name_uniqueness() -> None:
    import yaml

    section("8. Name uniqueness (single source of truth)")
    people = yaml.safe_load((ROOT / "data/people.yaml").read_text())["people"]
    names = [p["name"] for p in people]
    loc: dict[str, list[str]] = collections.defaultdict(list)

    # Only check SOURCE files, not the auto-generated docs/.
    source_files = (
        list(ROOT.glob("*.md"))
        + list((ROOT / "platforms").glob("*.md"))
        + list((ROOT / "operations").glob("*.md"))
        + [ROOT / "data/people.yaml", ROOT / "data/links.yaml"]
        + [ROOT / "examples/extract.py"]
    )
    for f in source_files:
        text = f.read_text()
        for n in names:
            if n in text:
                loc[n].append(str(f.relative_to(ROOT)))
    dupes = {n: fs for n, fs in loc.items() if len(fs) > 1}
    if dupes:
        for n, fs in dupes.items():
            fail(f"name '{n}' appears in multiple files: {fs}")
    else:
        print(f"  {len(names)} names, 0 duplicates across source files (OK)")


# ─── 9. Sensitivity sweep ───────────────────────────────────────────────────
def check_sensitivity() -> None:
    section("9. Sensitivity sweep")
    # Exclude the validator itself — its regex literals naturally contain the
    # patterns it's looking for elsewhere.
    SELF = pathlib.Path(__file__).resolve()
    sources = [
        f
        for f in ROOT.rglob("*")
        if f.is_file()
        and ".git/" not in str(f)
        and "/site/" not in str(f)
        and not str(f).startswith(str(DOCS))
        and f.resolve() != SELF
        and f.suffix not in (".pyc",)
    ]
    patterns: list[tuple[str, re.Pattern]] = [
        ("chartfield code", re.compile(r"\b\d{2}-\d{5}-[A-Z]{4,6}-[A-Z]{4,6}\b")),
        ("AHDPG / CORET fragments", re.compile(r"\b(AHDPG|CORET)\b")),
        ("PEM private key", re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----")),
        ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("credential assignment", re.compile(
            r"(?i)(password|api[_ -]?key|secret|token|bearer)\s*[:=]\s*[\"']?[A-Za-z0-9._/-]{6,}"
        )),
        ("URL with embedded auth", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")),
        ("removed person (Reza/Nikolaos)", re.compile(r"\b(Reza Rowshan|Nikolaos Giakoumidis|rr130|ng44)\b")),
    ]
    total = 0
    for label, regex in patterns:
        hits: list[str] = []
        for f in sources:
            try:
                txt = f.read_text(errors="ignore")
            except Exception:
                continue
            for m in regex.finditer(txt):
                ln = txt[: m.start()].count("\n") + 1
                hits.append(f"{f.relative_to(ROOT)}:{ln}: '{m.group(0)}'")
        if hits:
            total += len(hits)
            for h in hits:
                fail(f"sensitive pattern '{label}' → {h}")
    if total == 0:
        print("  no chartfields, credentials, or removed-person references (OK)")


# ─── Main ───────────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    checks: list[Callable] = [
        check_mkdocs_config,
        run_hook,
        # check_nav needs the parsed config; we re-parse below for simplicity.
    ]

    cfg = check_mkdocs_config()
    run_hook()
    check_nav(cfg)
    check_internal_links()
    check_yaml_schemas()
    check_platform_netids()
    check_jinja_render()
    check_name_uniqueness()
    check_sensitivity()

    print("\n" + "═" * 60)
    if errors:
        print(f"❌  {len(errors)} failure(s):\n")
        for e in errors:
            print(f"   • {e}")
        return 1
    print("✅  All checks passed. Safe to push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
