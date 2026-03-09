# IJM Legal & Policy Resource Library

A version-controlled, plain-text library of source documents on human trafficking, forced labour, and labour exploitation — curated for legal practitioners and policy teams.

## Why a Git repo?

| Feature | Git repo | SharePoint folders | Excel |
|---|---|---|---|
| Version history | Built in | Manual | Manual |
| Collaboration | PRs, reviews, blame | Co-authoring | Merge conflicts |
| Search | `grep`, scripts, GitHub search | Limited | Ctrl+F |
| Automation | CI validation, auto-build index | Power Automate (paid) | Macros |
| Offline access | Full clone | Sync issues | Single file |
| Portable | Plain text forever | Vendor lock-in | Vendor lock-in |

## Quick start

```bash
git clone <repo-url>
cd ijm-legal-library

# Validate all entries against controlled vocabularies
python scripts/validate.py

# Build the browsable INDEX.md and machine-readable index.json
python scripts/build-index.py

# Download source PDFs/HTML for all public entries
python scripts/download.py

# Link downloaded files back into entry frontmatter
python scripts/link-docs.py

# Filter from the command line
python scripts/filter.py --jurisdiction UK --bucket case-law
python scripts/filter.py --tag child-victim-identification
python scripts/filter.py --access backend-needed
python scripts/filter.py --search "forced labour" --format json
```

Requires Python 3.8+ and `pyyaml` (`pip install pyyaml`).

## Repo structure

```
ijm-legal-library/
├── README.md                  ← you are here
├── CONTRIBUTING.md            ← how to add/edit entries
├── TEMPLATE.md                ← blank entry template (copy this)
├── schema.yml                 ← controlled vocabularies (single source of truth)
├── INDEX.md                   ← auto-generated browsable index
├── index.json                 ← auto-generated machine-readable index
├── scripts/
│   ├── validate.py            ← checks all entries against schema
│   ├── build-index.py         ← generates INDEX.md + index.json
│   ├── filter.py              ← CLI query tool
│   ├── download.py            ← fetches source PDFs/HTML from public URLs
│   └── link-docs.py           ← writes local_file paths back into entries
├── .github/
│   └── workflows/
│       └── validate.yml       ← CI: validates on every push/PR
├── docs/                      ← downloaded source documents (PDFs, HTML)
│   └── (mirrors entry folder structure)
├── victim-identification/     ← Thematic folder 1 (active)
│   ├── legislation/
│   ├── case-law/
│   ├── prosecution-procedure/
│   ├── operational-guidance/
│   ├── policy-commentary/
│   ├── journal-articles/
│   └── global-regional/
├── elements-defences/         ← Thematic folder 2 (future)
└── international-cooperation/ ← Thematic folder 3 (future)
```

## How it works

**Each document = one Markdown file with YAML frontmatter.**

The frontmatter contains all structured metadata (jurisdiction, bucket, tags, access level, etc.). The scripts read this frontmatter to validate, index, and filter. The Markdown body below the frontmatter is optional space for notes.

Example entry (`victim-identification/legislation/uk-modern-slavery-act-2015.md`):

```yaml
---
title: "Modern Slavery Act 2015"
jurisdiction: UK
bucket: legislation
document_type: act-statute
issuing_body: "UK Parliament"
date_issued: 2015-03-26
status: current
source_url: "https://www.legislation.gov.uk/ukpga/2015/30/contents/enacted"
access: public
summary: >
  Primary UK anti-trafficking and modern slavery statute...
victim_id_tags:
  - definition-scope
  - competent-authority-nrm
  - non-punishment-link
---
```

## Controlled vocabularies

All allowed values are defined in `schema.yml`. The `validate.py` script enforces them. To add a new jurisdiction, tag, or document type, edit `schema.yml` first — then entries can use the new value.

## Backend-needed entries

Some documents (paywalled case law, subscription journals) aren't publicly accessible. These still get an entry, flagged like this:

```yaml
access: backend-needed
backend_source: Westlaw
backend_confidence: confirmed-paywalled
retrieval_notes: "487 U.S. 931 (1988). Export full opinion."
```

Run `python scripts/filter.py --access backend-needed` to see all items that need manual retrieval.

## Storing source documents (PDFs)

The `docs/` folder stores actual source documents (PDFs, HTML) alongside the index entries. Documents are committed directly to git — no LFS needed. A library of 500 documents at ~2 MB average is ~1 GB, well within GitHub's limits.

```bash
python scripts/download.py     # fetch all public source docs
python scripts/link-docs.py    # write file paths into entries
git add -A && git commit       # commit everything directly
```

## Thematic scope

| # | Theme | Status |
|---|---|---|
| 1 | Victim Identification | **Active** |
| 2 | Elements & Defences (Evidence & Proof) | Planned |
| 3 | International Cooperation | Planned |

### Priority jurisdictions

US · EU · UK · Australia · ASEAN (regional) · ECHR (where relevant)

Also: UN, ILO, UNODC, OSCE global/regional instruments.

## License

This is a curated index of public legal documents. The index entries and metadata are original work by IJM. Source documents are subject to their own copyright and access terms.
