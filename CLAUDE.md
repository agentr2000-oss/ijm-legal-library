# CLAUDE.md — Claude Code project configuration

## Project overview
This is a git-versioned legal research library on human trafficking, forced labour, and labour exploitation. Each source document = one Markdown file with YAML frontmatter. PDFs are committed directly to git in `docs/`.

## Key files
- `schema.yml` — all controlled vocabularies. Every frontmatter value MUST match.
- `TEMPLATE.md` — the exact entry format. Copy this for new entries.
- `scripts/validate.py` — validates all entries. Run after every batch.
- `scripts/build-index.py` — regenerates INDEX.md + index.json. Run before committing.
- `scripts/download.py` — fetches source PDFs/HTML for public entries into `docs/`.
- `scripts/link-docs.py` — writes `local_file` paths back into entry frontmatter.

## Workflow for adding entries
1. Create .md file in the correct subfolder (e.g., `victim-identification/case-law/`)
2. Fill in YAML frontmatter matching schema.yml values exactly
3. `python scripts/validate.py` — must pass with 0 errors
4. `python scripts/build-index.py` — regenerate index
5. `git add -A && git commit`

## File naming
`[jurisdiction]-[short-slug].md` — e.g., `uk-modern-slavery-act-2015.md`

## Rules
- Summaries: 1-3 sentences, victim-identification relevance only
- Tags: 1-5 from schema.yml, only genuinely relevant ones
- Paywalled sources: set `access: backend-needed` with full retrieval instructions
- Do NOT create synthesized memos, toolkits, or policy drafts
- Do NOT create entries outside the current scope (victim identification)

## Commit messages
```
add: [jurisdiction] [short description]
fix: [what was fixed]
schema: [what changed in controlled vocabularies]
```

## Dependencies
Python 3.8+ and `pyyaml` (`pip install pyyaml`)
