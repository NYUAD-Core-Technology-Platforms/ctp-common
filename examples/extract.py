#!/usr/bin/env python3
"""Examples of extracting data from ctp-common.

Run from the repo root:
    python3 examples/extract.py

This script demonstrates the canonical lookup patterns. Copy what you need
into your downstream repo (docs generator, slide builder, website, etc.).
"""
import re
from pathlib import Path

import yaml  # pip install pyyaml

REPO = Path(__file__).resolve().parent.parent


def load_people():
    """Return a dict of {netid: person} from data/people.yaml."""
    data = yaml.safe_load((REPO / "data/people.yaml").read_text())
    return {p["netid"]: p for p in data["people"]}


def load_links():
    return yaml.safe_load((REPO / "data/links.yaml").read_text())


def load_platform(platform_id: str):
    """Parse a platform .md file: returns (frontmatter_dict, body_markdown)."""
    md = (REPO / f"platforms/{platform_id}.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)", md, re.DOTALL)
    return yaml.safe_load(m.group(1)), m.group(2)


def all_platforms():
    """Yield (id, frontmatter, body) for every platform.

    Skips files without YAML front-matter (e.g. platforms/index.md, which is the
    section overview page rendered by MkDocs).
    """
    for md in sorted((REPO / "platforms").glob("*.md")):
        if md.stem in ("index", "_index"):
            continue
        yield md.stem, *load_platform(md.stem)


# ─── Examples ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    people = load_people()
    links = load_links()

    # 1. Who is the CTP Director?
    print("Director :", next(p for p in people.values()
                              if p["role"].startswith("Director, Core Technology"))["name"])

    # 2. Who runs Brain Imaging?
    fm, _ = load_platform("brain-imaging")
    print("Brain Imaging team:")
    for nid in fm["specialists"]:
        p = people[nid]
        print(f"  - {p['name']:30} {p['role']}  <{p['email']}>")

    # 3. List every platform with a one-line summary.
    print("\nAll platforms:")
    for pid, fm, _ in all_platforms():
        leads = ", ".join(people[n]["name"] for n in fm.get("specialists", []))
        print(f"  {fm['name']:45} — {leads or '(unmanned/external)'}")

    # 4. Generate an email signature block for a person.
    me = people["hz3752"]
    print("\nSignature for hz3752:")
    print(f"  {me['name']}\n  {me['role']}\n  NYU Abu Dhabi · Core Technology Platforms")
    print(f"  {me['email']} · ext {me['ext']} · {me['mobile']}")

    # 5. Useful URLs for a slide deck.
    print("\nPublic links:")
    for k, v in links["public"].items():
        print(f"  {k:25} {v}")
