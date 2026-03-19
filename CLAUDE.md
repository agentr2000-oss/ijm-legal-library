# CLAUDE.md — Claude Code project configuration

## Project overview
This is a git-versioned legal research library on human trafficking, forced labour, and labour exploitation. Each source document = one Markdown file with YAML frontmatter. PDFs are committed directly to git in `docs/`. The library covers multiple themes: victim identification, prosecution, investigations, sentencing, victim compensation, trauma-informed courtroom practice, and international cooperation.

## Key files
- `scripts/schema.yml` — all controlled vocabularies. Every frontmatter value MUST match.
- `scripts/TEMPLATE.md` — the exact entry format. Copy this for new entries.
- `scripts/validate.py` — validates all entries. Run after every batch.
- `scripts/build-index.py` — regenerates INDEX.md + index.json. Run before committing.
- `scripts/render-body.py` — regenerates human-readable markdown bodies from YAML.
- `scripts/download.py` — fetches source PDFs/HTML for public entries into `docs/`.
- `scripts/link-docs.py` — writes `local_file` paths back into entry frontmatter.
- `index.html` — interactive HTML index (reads from index.json, works offline).

## Thematic folders
- `victim-identification/` — NRM, indicators, first responder duties, screening tools
- `prosecution/` — offence elements (act/means/purpose), defences, CPS guidance, evidence
- `investigations/` — police investigation guidance, financial investigation, intelligence, digital forensics
- `sentencing/` — sentencing guidelines, sentencing case law, sentencing principles, confiscation/forfeiture
- `victim-compensation/` — restitution, reparation orders, civil remedies, compensation funds
- `trauma-informed-courtroom-practice/` — special measures, witness protection, judicial directions, trauma-informed approaches
- `elements-defences/` — (reserved for future use)
- `international-cooperation/` — MLA, JITs, Eurojust, country assessments

Each theme folder contains bucket subdirectories: `legislation/`, `case-law/`, `prosecution-procedure/`, `operational-guidance/`, `policy-commentary/`, `journal-articles/`, `global-regional/`.

## Tag taxonomy (legal process flow)

1. **Victim Identification:** `indicators-screening`, `first-responder-duties`, `competent-authority-nrm`, `referral-pathway`, `child-victim-identification`, `labour-exploitation-indicators`, `sex-trafficking-indicators`, `definition-scope`, `detention-immigration-interface`, `reflection-period-temporary-stay`, `assistance-entitlements`, `data-protection-confidentiality`, `non-punishment-link`, `cross-border-referral-return`, `interviewing-trauma-informed`
2. **Investigations:** `proactive-intelligence`, `financial-investigation`, `crime-scene-evidence`, `victim-engagement-interview`, `multi-agency-cooperation`, `digital-forensics`, `threat-assessment`
3. **Prosecution — Elements:** `element-act` (recruitment, transport, transfer, harbouring, receipt), `element-means` (force, fraud, coercion, deception, abuse of power/vulnerability), `element-purpose` (exploitation: sexual, labour, organs, criminal activity, begging), `consent-irrelevance`, `defences` (s.45, duress, non-punishment principle), `statutory-defence-s45`, `evidence-corroboration`, `abuse-of-process`, `victimless-prosecution`, `sentencing-penalty`
4. **Sentencing:** `sentencing-guidelines`, `sentencing-principles`, `confiscation-forfeiture`
5. **Victim Compensation:** `mandatory-restitution`, `civil-remedy`, `reparation-order`, `compensation-fund`
6. **Courtroom Practice:** `special-measures`, `witness-protection`, `judicial-directions`, `trauma-informed-approach`
7. **Cross-cutting:** `mutual-legal-assistance`, `joint-investigation-team`, `extradition-transfer`, `country-assessment`, `supply-chain-due-diligence`, `transparency-reporting`

## Workflow for adding entries
1. Create .md file in the correct subfolder (e.g., `prosecution/case-law/`)
2. Fill in YAML frontmatter matching scripts/schema.yml values exactly
3. `python scripts/validate.py` — must pass with 0 errors
4. `python scripts/render-body.py` — regenerate readable body
5. `python scripts/build-index.py` — regenerate index
6. `git add -A && git commit`

## File naming
`[jurisdiction]-[short-slug].md` — e.g., `uk-modern-slavery-act-2015.md`

## Rules
- Summaries: 1-3 sentences, focused on thematic relevance (not just victim identification)
- Tags: 1-5 from scripts/schema.yml, only genuinely relevant ones
- Cross-theme tags: entries may have tags from multiple themes for discoverability
- Paywalled sources: set `access: backend-needed` with full retrieval instructions
- Do NOT create synthesized memos, toolkits, or policy drafts

## Commit messages
```
add: [jurisdiction] [short description]
fix: [what was fixed]
schema: [what changed in controlled vocabularies]
```

## Dependencies
Python 3.8+ and `pyyaml` (`pip install pyyaml`)
