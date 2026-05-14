"""MkDocs pre-build hook: populate ./docs from the repo root.

Why this exists
---------------
This repo's primary purpose is to be a *source of truth* for downstream
consumers — slide decks, doc generators, websites — that read
`platforms/*.md`, `operations/*.md`, and `data/*.yaml` directly. We don't
want to move those into a `docs/` folder just to satisfy MkDocs, because
that would break every downstream that's pinned to `platforms/<id>.md`.

MkDocs requires `docs_dir` to be a sibling of `mkdocs.yml`, not the
project root itself. So we use this hook to *copy* root-level markdown
into a gitignored `docs/` directory at build time. The mapping is below.

`docs/` is regenerated on every build, including `mkdocs serve`'s
live-reload rebuilds. Never commit anything inside `docs/`.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Source path (relative to ROOT) → target path inside docs/.
# README.md becomes index.md so MkDocs renders it as the site landing page.
COPY_MAP: dict[str, str] = {
    "README.md":  "index.md",
    "AGENTS.md":  "AGENTS.md",
    "team.md":    "team.md",
    "links.md":   "links.md",
    "platforms":  "platforms",
    "operations": "operations",
    # Copy the data/ folder too so links from README.md to data/*.yaml
    # resolve on the deployed site (GitHub renders them at the same path).
    "data":       "data",
    "examples":   "examples",
}


def on_pre_build(config, **kwargs):
    # Wipe everything inside docs/ EXCEPT .gitkeep (which is tracked so the
    # directory exists at checkout — MkDocs validates docs_dir before this
    # hook runs).
    DOCS.mkdir(parents=True, exist_ok=True)
    for entry in DOCS.iterdir():
        if entry.name == ".gitkeep":
            continue
        if entry.is_file() or entry.is_symlink():
            entry.unlink()
        else:
            shutil.rmtree(entry)

    for src, dst in COPY_MAP.items():
        src_path = ROOT / src
        dst_path = DOCS / dst
        if not src_path.exists():
            # Tolerate missing optional sources (e.g. team.md or links.md
            # could be intentionally absent in a stripped-down build).
            continue
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
        elif src_path.is_dir():
            shutil.copytree(src_path, dst_path)
