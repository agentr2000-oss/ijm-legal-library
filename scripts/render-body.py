#!/usr/bin/env python3
"""Render a human-readable markdown body below the YAML frontmatter of each entry.

Idempotent: always regenerates the body from frontmatter, so running twice
produces the same output. Frontmatter is never modified.

Usage:
    python scripts/render-body.py           # process all entries
    python scripts/render-body.py --dry-run # show what would change without writing
"""

import os, sys, re, glob, yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_DIRS = ["victim-identification", "elements-defences", "international-cooperation"]

BUCKET_LABELS = {
    "legislation": "Legislation",
    "case-law": "Case Law",
    "prosecution-procedure": "Prosecution & Procedure",
    "operational-guidance": "Operational Guidance",
    "policy-commentary": "Policy & Commentary",
    "journal-articles": "Journal Article",
    "global-regional": "Global & Regional Instrument",
}

DOC_TYPE_LABELS = {
    "act-statute": "Act / Statute",
    "regulation-rule": "Regulation / Rule",
    "directive": "Directive",
    "framework-decision": "Framework Decision",
    "convention-treaty": "Convention / Treaty",
    "protocol": "Protocol",
    "guideline-sop": "Guideline / SOP",
    "practice-direction": "Practice Direction",
    "judgment-opinion": "Judgment / Opinion",
    "decision": "Decision",
    "advisory-opinion": "Advisory Opinion",
    "issue-paper": "Issue Paper",
    "report": "Report",
    "model-law-template": "Model Law / Template",
    "journal-article": "Journal Article",
    "working-paper": "Working Paper",
    "commentary-analysis": "Commentary / Analysis",
    "toolkit-manual": "Toolkit / Manual",
    "factsheet": "Factsheet",
    "declaration": "Declaration",
}


def parse_frontmatter(filepath):
    """Return (yaml_block_with_delimiters, parsed_dict) or (None, None)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"^(---\n.+?\n---)", content, re.DOTALL)
    if not match:
        return None, None
    raw_block = match.group(1)
    fm_text = re.match(r"^---\n(.+?)\n---", content, re.DOTALL).group(1)
    fm = yaml.safe_load(fm_text)
    return raw_block, fm


def render_body(fm):
    """Generate the markdown body from frontmatter fields."""
    lines = []

    # Title
    title = fm.get("title", "Untitled")
    lines.append(f"# {title}")
    lines.append("")

    # Metadata table
    rows = []
    rows.append(("Jurisdiction", fm.get("jurisdiction", "")))
    rows.append(("Bucket", BUCKET_LABELS.get(fm.get("bucket", ""), fm.get("bucket", ""))))
    rows.append(("Document Type", DOC_TYPE_LABELS.get(fm.get("document_type", ""), fm.get("document_type", ""))))
    if fm.get("issuing_body"):
        rows.append(("Issuing Body", fm["issuing_body"]))
    if fm.get("date_issued"):
        rows.append(("Date Issued", str(fm["date_issued"])))
    rows.append(("Status", fm.get("status", "")))
    rows.append(("Access", fm.get("access", "")))

    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for label, value in rows:
        lines.append(f"| **{label}** | {value} |")
    lines.append("")

    # Summary
    summary = fm.get("summary", "")
    if summary:
        summary = str(summary).strip()
        lines.append("## Summary")
        lines.append("")
        lines.append(summary)
        lines.append("")

    # Key Provisions / Pinpoint
    key_pinpoint = fm.get("key_pinpoint", "")
    if key_pinpoint:
        key_pinpoint = str(key_pinpoint).strip()
        lines.append("## Key Provisions")
        lines.append("")
        lines.append(key_pinpoint)
        lines.append("")

    # Victim Identification Tags
    tags = fm.get("victim_id_tags", [])
    if tags:
        tag_str = " · ".join(f"`{t}`" for t in tags)
        lines.append("## Victim Identification Tags")
        lines.append("")
        lines.append(tag_str)
        lines.append("")

    # Access section for backend-needed entries
    if fm.get("access") == "backend-needed":
        lines.append("## Access")
        lines.append("")
        lines.append("This document requires backend retrieval.")
        lines.append("")

        access_rows = []
        if fm.get("backend_source"):
            access_rows.append(("Backend Source", fm["backend_source"]))
        if fm.get("backend_confidence"):
            access_rows.append(("Confidence", fm["backend_confidence"]))

        if access_rows:
            lines.append("| Field | Value |")
            lines.append("|---|---|")
            for label, value in access_rows:
                lines.append(f"| **{label}** | {value} |")
            lines.append("")

        retrieval_notes = fm.get("retrieval_notes", "")
        if retrieval_notes:
            retrieval_notes = str(retrieval_notes).strip()
            lines.append("### Retrieval Notes")
            lines.append("")
            lines.append(retrieval_notes)
            lines.append("")

    # Source section
    source_url = fm.get("source_url", "")
    local_file = fm.get("local_file", "")
    if source_url or local_file:
        lines.append("## Source")
        lines.append("")
        if source_url:
            lines.append(f"[View source document]({source_url})")
            lines.append("")
        if local_file:
            lines.append(f"**Local copy:** `{local_file}`")
            lines.append("")

    return "\n".join(lines)


def process_file(filepath, dry_run=False):
    """Render the body for a single entry file. Returns True if file was changed."""
    raw_block, fm = parse_frontmatter(filepath)
    if fm is None:
        return False

    body = render_body(fm)
    new_content = raw_block + "\n\n" + body + "\n"

    with open(filepath, "r", encoding="utf-8") as f:
        old_content = f.read()

    if new_content == old_content:
        return False

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
    return True


def main():
    dry_run = "--dry-run" in sys.argv

    md_files = []
    for d in ENTRY_DIRS:
        full = os.path.join(REPO_ROOT, d)
        md_files.extend(glob.glob(os.path.join(full, "**", "*.md"), recursive=True))

    if not md_files:
        print("No entry files found.")
        sys.exit(0)

    changed = 0
    for fp in sorted(md_files):
        rel = os.path.relpath(fp, REPO_ROOT)
        was_changed = process_file(fp, dry_run=dry_run)
        if was_changed:
            changed += 1
            print(f"  {'WOULD UPDATE' if dry_run else 'UPDATED'}  {rel}")
        else:
            print(f"  OK  {rel}")

    action = "would be updated" if dry_run else "updated"
    print(f"\n{'='*50}")
    print(f"Files checked: {len(md_files)}  |  {action.capitalize()}: {changed}")


if __name__ == "__main__":
    main()
