# AGENTS.md — guidance for coding agents

If you're an LLM agent (Claude, GPT, etc.) helping someone edit this repo: read this first. Humans, you can skim it too — the rules here are the design contract that keeps `ctp-common` useful for everyone pulling from it.

---

## What this repo is

A small, public, single-source-of-truth repository for **NYU Abu Dhabi Core Technology Platforms (CTP)** facts. It is consumed by *other* repos — slide decks, doc generators, websites, onboarding kits — which pin to a git tag and pull names, contacts, platform descriptions, and equipment lists from here.

Two consequences flow from that:

1. **The repo is public.** Treat it like a published API. Never commit anything that should stay inside CTP.
2. **Every fact lives in exactly one place.** A downstream repo will trust whatever you write here. If two files disagree, the downstream output is wrong.

---

## Non-negotiable rules

| # | Rule | Why |
|---|------|-----|
| 1 | **Never commit chartfields, budget figures, vendor pricing, internal Drive file IDs, internal SOP content, or anything else that wouldn't be appropriate on the public CTP website.** | This repo is public. |
| 2 | **A person's name appears in exactly one file: `data/people.yaml`.** Every other reference uses the NetID. | Single source of truth — if Osama is promoted, change one row, not twelve. |
| 3 | **NetIDs are the foreign keys.** Never rename a NetID, never invent one. Use whatever the registrar uses. | NetID is the only stable identifier across NYU systems. |
| 4 | **Platform identifiers are the filename slug** (e.g. `brain-imaging`, not `Brain Imaging` or `BI`). Used in `platforms/<id>.md` AND in the `platform:` field on each person. | Lets downstream code join platform ↔ people without string matching. |
| 5 | **YAML must be machine-parseable.** Quote strings that start with numbers, contain apostrophes, or look like booleans. Phone numbers are strings, not numbers (leading zeros, spaces). | `data/*.yaml` is parsed in every downstream consumer. |
| 6 | **After edits, run `python3 examples/extract.py`.** It must succeed and produce sensible output. | Regression catch. |

---

## Repository map

```
ctp-common/
├── README.md                ← human overview + extraction examples
├── AGENTS.md                ← this file
├── data/
│   ├── people.yaml          ← CANONICAL: every person, keyed by NetID
│   └── links.yaml           ← CANONICAL: public URLs, generic emails, address
├── platforms/               ← one .md per CTP, with YAML front-matter
│   ├── _index.md            ← one-line summary of each platform
│   └── <id>.md × 12         ← platform description + equipment list
├── operations/
│   ├── scheduling.md        ← CTPSS, training, data save/access
│   └── procurement.md       ← requisition form, CBE, OTPS, lifecycle
├── examples/
│   └── extract.py           ← runnable extraction demo
├── team.md                  ← Jinja-rendered view of data/people.yaml
├── links.md                 ← Jinja-rendered view of data/links.yaml
├── mkdocs.yml               ← MkDocs Material site config
├── requirements.txt         ← Python deps for the site build
└── .github/workflows/pages.yml  ← deploys the site to GitHub Pages
```

## The published site (MkDocs Material → GitHub Pages)

The repo also builds a polished docs site. `team.md` and `links.md` contain **Jinja templates** that mkdocs-macros expands using `data/*.yaml`. This means:

- The single source of truth is still the YAML. `team.md` and `links.md` are presentation templates — never paste rendered names into them.
- After editing `data/people.yaml` or `data/links.yaml`, the site rebuilds automatically; don't also edit `team.md` or `links.md` unless you're changing the *layout*.
- New fields added to people.yaml won't appear on the site until `team.md` references them. To surface a new column, edit `team.md`.
- Platform pages stay pure markdown — no Jinja. If you want to surface team info on a platform page, the Team page already lists members grouped by platform.

**Preview the site:** `pip install -r requirements.txt && mkdocs serve`. The build runs locally without internet once deps are installed.

**Strict-mode build** (catches broken links and missing pages): `mkdocs build --strict`. The GitHub Action runs this; if it fails, the deploy fails.

### Why there's a `docs/` folder you've never seen

MkDocs requires its `docs_dir` to be a sibling of `mkdocs.yml`, not the project root. We don't want to relocate `platforms/` and `operations/` just to satisfy that — downstream consumers depend on those paths. So `hooks/prepare_docs.py` runs `on_pre_build` and **copies** the source files from the repo root into a gitignored `docs/` folder. MkDocs then reads `docs/`.

**Never edit anything inside `docs/`.** It's regenerated on every build. The source of truth is at the repo root (`README.md`, `team.md`, `links.md`, `platforms/*.md`, `operations/*.md`, `data/*.yaml`). If you want to add a new page to the site, create the markdown at the root, then register it in `mkdocs.yml`'s `nav:` block AND add it to `COPY_MAP` in `hooks/prepare_docs.py`.

### `data/people.yaml` schema

```yaml
people:
  - netid:    string          # primary key
    name:     string          # full display name
    role:     string          # current title
    category: leadership | scientist | specialist | machine_shop | adjacent
    email:    string          # NetID@nyu.edu
    ext:      string | null   # NYUAD 5-digit extension
    mobile:   string | null   # UAE mobile, format "0XX XXX XXXX"
    office:   string | null   # building/room (e.g. "A2", "B1", "CTP Workstations")
    platform: string | null   # platform id, or null if cross-CTP / non-platform

services:                     # generic mailboxes — no individual owner
  - id:      string           # short slug
    name:    string
    email:   string | null
    phone:   string
```

### Platform front-matter schema

```yaml
---
id:         string           # MUST match the filename slug
name:       string           # display name
short_name: string           # 2-3 letter abbreviation
location:   string           # optional
specialists: [netid, ...]    # foreign keys into data/people.yaml
techniques: [string, ...]
# Other domain-specific fields allowed (operated_by, environment, zones, etc.)
---
```

---

## Common tasks — how to do them right

### A new person joins CTP

1. Append one record to `data/people.yaml`, in the right `category` block. Fill all fields you have; use `null` for unknowns.
2. If they're the primary specialist on a CTP platform, also add their NetID to `platforms/<id>.md`'s `specialists:` list.
3. Do **not** edit README, do **not** edit the platform body prose, do **not** mention the name anywhere else.

### Someone leaves or changes platform

1. Edit their record in `data/people.yaml` — update `role`, `platform`, or remove the record entirely.
2. Remove their NetID from any platform's `specialists:` list that no longer applies.
3. Run `python3 examples/extract.py` — it must still succeed.

### A platform's lead specialist changes (e.g. promotion to leadership)

1. Update the person's `role` and `category` in `data/people.yaml`. Set `platform: null` if they're now in leadership.
2. Remove their NetID from the old platform's `specialists:` list in front-matter.
3. Add the successor's NetID (or leave empty if vacant). Check README's platform table — it lists NetIDs too (but no names).

### Add a new platform

1. Create `platforms/<new-id>.md` with the standard front-matter schema and a prose body following the existing pattern (description → main equipment).
2. Add a row to `platforms/_index.md`.
3. Add a row to the platform table in `README.md`.
4. If any person staffs it, set their `platform: <new-id>` in `data/people.yaml` and add their NetID to the front-matter `specialists:` list.

### URL or generic email changes

Edit only `data/links.yaml`. Do not duplicate URLs into prose.

### Equipment list changes on a platform

Edit only the equipment section of `platforms/<id>.md`. Equipment is documented in markdown bullets (one per line) — keep that pattern.

---

## What to keep OUT

If you're tempted to add any of these, stop:

- Chartfields (`<fund>-<dept>-<program>-<project>` codes used on POs). They go in the internal CTP Drive, not here. Even example chartfields are out — don't put a real one in a "do not commit" warning either.
- Budget numbers, OTPS line totals, capital request figures.
- Vendor quotes, pricing, contract terms.
- Internal Google Drive file IDs (the long random strings in Drive URLs). Reference docs by title only, and only when necessary.
- Internal SOP attachments — link to the public CTPSS or the Linktree if relevant, do not paste SOP content here.
- Faculty PI lab descriptions and grant-funded research — that's a different repo. This repo is for CTP **operations**.
- Personal information beyond what's already published in the CTP directory (names, NYU emails, NYUAD extensions, mobiles, office numbers — those are fine).
- Anything starting with "this is just internal" — write it in the internal Drive instead.

---

## Verification commands

Before finishing any edit, run these:

```bash
# 1. Smoke test — extract.py must succeed
python3 examples/extract.py

# 2. YAML validity
python3 -c "import yaml; yaml.safe_load(open('data/people.yaml')); yaml.safe_load(open('data/links.yaml')); print('YAML OK')"

# 3. Name uniqueness — no name should appear in more than one file
python3 -c "
import yaml, glob, collections
people = yaml.safe_load(open('data/people.yaml'))['people']
names = [p['name'] for p in people]
loc = collections.defaultdict(list)
for f in sorted(glob.glob('**/*.md', recursive=True)) + ['data/people.yaml','data/links.yaml','examples/extract.py']:
    txt = open(f).read()
    for n in names:
        if n in txt:
            loc[n].append(f)
dupes = {n: fs for n, fs in loc.items() if len(fs) > 1}
print(f'{len(names)} names — duplicates: {len(dupes)}')
for n, fs in dupes.items():
    print(f'  {n}: {fs}')
"

# 4. Every platform's specialists must resolve to a known NetID
python3 -c "
import yaml, re, glob
known = {p['netid'] for p in yaml.safe_load(open('data/people.yaml'))['people']}
bad = []
for f in glob.glob('platforms/*.md'):
    if f.endswith('_index.md'): continue
    fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---', open(f).read(), re.DOTALL).group(1))
    for nid in fm.get('specialists', []):
        if nid not in known:
            bad.append((f, nid))
print('Dangling NetIDs:', bad or 'none')
"

# 5. Cross-link sanity — every .md link in README must resolve
python3 -c "
import re, os
links = re.findall(r'\]\(([^)]+\.md)\)', open('README.md').read())
miss = [l for l in links if not os.path.exists(l)]
print(f'{len(links)} links checked; {len(miss)} missing: {miss}')
"
```

All five should print clean output. If any fails, fix before committing.

### Recommended: run `scripts/check_build.py` before every push

`scripts/check_build.py` bundles every invariant agents and humans rely on:
mkdocs config layout, the prepare-docs hook, nav targets, internal markdown
links, YAML schemas, NetID foreign keys, Jinja render simulation, name
uniqueness, and a sensitivity sweep. It exits non-zero on any failure with a
specific message.

```bash
python3 scripts/check_build.py
```

The GitHub Action runs this **before** `mkdocs build --strict`, so a failure
here will fail the deploy with a clear message instead of an opaque MkDocs
warning. Treat a clean run as the gate for pushing.

---

## When in doubt

- Ask the user before adding a category that doesn't already exist (e.g. faculty leads, grant info, internal-only fields).
- Prefer deletion over partial fixes. If a fact looks stale, ask the user to confirm rather than guessing.
- Keep prose terse. This repo is meant to be parsed and re-rendered, not read cover-to-cover.
- The Admin Coordinator is the human source of truth for live data. When in doubt about a NetID, role, or chartfield, ask them — don't infer.
