# CTP Common Repository

Single source of truth for **NYU Abu Dhabi Core Technology Platforms (CTP)** facts that are shared across documents, presentations, SOPs, and websites.

Pull from this repo (as a git submodule, sparse checkout, or simple copy) instead of duplicating director names, contact lists, equipment inventories, and procedural links across many places.

## What's in here

```
ctp-common/
├── README.md                           ← you are here
├── AGENTS.md                           ← read this first if you're an LLM agent editing the repo
├── data/                               ← MACHINE-READABLE (YAML — start here for scripts)
│   ├── people.yaml                     ← every person, keyed by NetID
│   └── links.yaml                      ← public URLs, generic emails, mailing address
├── platforms/                          ← one file per CTP, YAML front-matter + prose
│   ├── index.md                        ← one-line summary of every platform
│   ├── analytical-materials-characterization.md
│   ├── spectrometry-spectroscopy.md
│   ├── microfabrication.md
│   ├── molecular-cell-biology.md
│   ├── sequencing.md
│   ├── high-throughput-screening.md
│   ├── light-microscopy.md
│   ├── brain-imaging.md
│   ├── marine-biology.md
│   ├── advanced-manufacturing-electronics.md
│   ├── photonics.md
│   └── kinesis.md
├── operations/                         ← procedural documentation
│   ├── scheduling.md                   ← CTPSS, training, screen lock, data save/access
│   └── procurement.md                  ← requisition form, CBE, OTPS budget, lifecycle
├── examples/
│   └── extract.py                      ← copy-paste examples for downstream consumers
├── mkdocs.yml                          ← site config for the published docs site
├── requirements.txt                    ← Python deps for `mkdocs build`
└── .github/workflows/pages.yml         ← auto-deploys the site to GitHub Pages
```

## Published site

A polished, searchable version of this repo is built with MkDocs Material and auto-deployed to GitHub Pages on every push to `main`. The site renders [`data/people.yaml`](data/people.yaml) into a Team page and [`data/links.yaml`](data/links.yaml) into a Public-links page via Jinja — no duplicated data, no separate build step to remember.

**Preview locally:**

```bash
pip install -r requirements.txt
mkdocs serve              # http://localhost:8000
```

**Publish:**

The included GitHub Action (`.github/workflows/pages.yml`) handles deploys. One-time setup in the repo settings: **Settings → Pages → Source: GitHub Actions**. After that, every push to `main` rebuilds and deploys the site automatically.

> 🔒 **This repo is public.** Chartfields, budget templates, internal Drive file IDs, vendor pricing, and internal SOP attachments are kept out. Names, NYU emails, NYUAD phone extensions, mobiles, office numbers, and equipment lists are fine.

---

## Single source of truth — how to read it

The repo is organised so every fact lives in **exactly one place**:

| Fact | Lives in | Looked up by |
|------|----------|--------------|
| A person's name, role, email, phone, office | `data/people.yaml` | `netid` (e.g. `oa22`) |
| A public URL or generic email | `data/links.yaml` | key (e.g. `public.linktree`) |
| Who works on a given platform | `platforms/<id>.md` front-matter `specialists:` list | NetID(s) referencing `data/people.yaml` |
| Platform description, equipment, location | `platforms/<id>.md` front-matter + prose | platform `id` |
| Booking workflow | `operations/scheduling.md` | — |
| Procurement workflow | `operations/procurement.md` | — |

NetIDs are foreign keys. A platform never repeats a person's name — only the `netid`. To get the name, look up the NetID in `data/people.yaml`.

---

## How to extract data from another repo

Everything that matters as data is YAML. A downstream slide builder or doc generator can pull it in three lines.

**Python (recommended):**

```python
import yaml, re, pathlib
people = {p["netid"]: p for p in yaml.safe_load(open("data/people.yaml"))["people"]}

# Parse a platform's front-matter
md = pathlib.Path("platforms/brain-imaging.md").read_text()
fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---", md, re.DOTALL).group(1))

# Brain Imaging specialists, by name
for nid in fm["specialists"]:
    print(people[nid]["name"], "—", people[nid]["role"])
```

**bash + yq:**

```bash
yq '.people[] | select(.netid == "oa22") | .name' data/people.yaml
yq '.public.linktree' data/links.yaml
```

**Node.js:**

```js
const yaml = require("js-yaml");           // npm i js-yaml
const fs   = require("fs");
const data = yaml.load(fs.readFileSync("data/people.yaml", "utf8"));
const byId = Object.fromEntries(data.people.map(p => [p.netid, p]));
console.log(byId["oa22"].name);            // → current CTP Director's name
```

See [`examples/extract.py`](examples/extract.py) for a runnable demo covering: finding the director, listing a platform's team, generating an email signature, dumping every platform's lead.

---

## The 12 Core Technology Platforms

| # | id | Platform | Specialists (NetID) |
|---|----|----------|---------------------|
| 1 | `analytical-materials-characterization` | Analytical & Materials Characterization | `yh4887` · `jw180` · `rs8743` |
| 2 | `spectrometry-spectroscopy` | Spectrometry & Spectroscopy | `la77` · `moc2` · `sv2102` |
| 3 | `microfabrication` | Microfabrication | `qz19` |
| 4 | `molecular-cell-biology` | Molecular & Cell Biology | `mrk6` |
| 5 | `sequencing` | Sequencing | `mga5` |
| 6 | `high-throughput-screening` | High-Throughput Screening | (CGSB-operated) |
| 7 | `light-microscopy` | Light Microscopy | `rr142` |
| 8 | `brain-imaging` | Brain Imaging | `hp42` · `hz3752` · `mb9720` |
| 9 | `marine-biology` | Marine Biology | `au2411` · `rap9713` |
| 10 | `advanced-manufacturing-electronics` | Advanced Manufacturing & Electronics | `oga2` · `pr2449` · `jg6720` |
| 11 | `photonics` | Photonics | `ma39897` |
| 12 | `kinesis` | Kinesis | `sxp8070` |

The platform `id` matches the filename (`platforms/<id>.md`) and the `platform` field on each person in `data/people.yaml`.

---

## Contributing

When a fact changes:

1. **A person** joined / left / changed role / new mobile → edit only `data/people.yaml`.
2. **A new specialist on a platform** → add them to `data/people.yaml` AND add their NetID to the platform file's front-matter `specialists:` list.
3. **A platform gains/loses equipment** → edit the equipment section of `platforms/<id>.md`.
4. **A URL or generic email changed** → edit `data/links.yaml`.
5. Commit with a descriptive message — downstream repos can pin to a tagged release.

If you find yourself typing the same name in two files, stop — only `data/people.yaml` should contain names.
