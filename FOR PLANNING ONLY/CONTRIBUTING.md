# Contributing to the IJM Legal & Policy Resource Library

## Adding a new document entry

1. **Copy the template:**
   ```bash
   cp TEMPLATE.md victim-identification/legislation/au-my-new-entry.md
   ```

2. **Choose the right folder:**
   - `victim-identification/legislation/` — Acts, statutes, regulations, directives
   - `victim-identification/case-law/` — Judgments, opinions, decisions
   - `victim-identification/prosecution-procedure/` — Practice directions, statutory guidance, CPS/DPP policies
   - `victim-identification/operational-guidance/` — SOPs, screening tools, NRM guidance, first responder protocols
   - `victim-identification/policy-commentary/` — Issue papers, reports, policy analysis
   - `victim-identification/journal-articles/` — Academic articles, working papers
   - `victim-identification/global-regional/` — UN, ILO, UNODC, OSCE, ASEAN instruments

3. **Name the file:** `[jurisdiction]-[short-slug].md`
   - `us-tvpa-2000.md`
   - `uk-vsc-v-sshd-2021.md`
   - `asean-actip-2015.md`
   - `un-palermo-protocol-2000.md`

4. **Fill in the frontmatter.** All values must match `schema.yml`. Required fields:
   - `title`, `jurisdiction`, `bucket`, `document_type`
   - `issuing_body`, `date_issued`, `status`, `access`
   - `summary`, `victim_id_tags`

5. **If the document is paywalled**, set `access: backend-needed` and fill in:
   - `backend_source` — where to retrieve it
   - `backend_confidence` — how sure you are it exists
   - `retrieval_notes` — full citation, docket, what to export

6. **Validate:**
   ```bash
   python scripts/validate.py
   ```

7. **Rebuild the index:**
   ```bash
   python scripts/build-index.py
   ```

8. **Commit and push** (or open a PR for review).

## Editing controlled vocabularies

Need a new jurisdiction, tag, or document type? Edit `schema.yml`, then all entries can use the new value. Run `validate.py` to make sure nothing broke.

## Commit message convention

```
add: [jurisdiction] [short description]
    add: UK VCL and AN v SSHD (2021) case law entry

fix: [what was fixed]
    fix: corrected source_url for ACTIP entry

schema: [what changed]
    schema: added 'forced-marriage' to victim_id_tags
```

## Review checklist

Before merging a PR:

- [ ] `validate.py` passes with zero errors
- [ ] Source URL is reachable (for public entries)
- [ ] Summary is 1–3 sentences, focused on victim-identification relevance
- [ ] Tags are specific and accurate (don't over-tag)
- [ ] Backend-needed entries have complete retrieval instructions
