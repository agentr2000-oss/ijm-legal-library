#!/usr/bin/env python3
"""Build INDEX.md and index.json from all document entries.

Usage:
    python scripts/build-index.py              # builds both files at repo root
    python scripts/build-index.py --json-only  # only index.json
"""

import os, sys, glob, re, json, yaml
from collections import defaultdict
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_DIRS = ["victim-identification", "elements-defences", "international-cooperation"]

THEME_LABELS = {
    "victim-identification": "Victim Identification",
    "elements-defences": "Elements & Defences (Evidence & Proof)",
    "international-cooperation": "International Cooperation",
}
BUCKET_ORDER = [
    "legislation", "case-law", "prosecution-procedure",
    "operational-guidance", "policy-commentary",
    "journal-articles", "global-regional",
]
BUCKET_LABELS = {
    "legislation": "Legislation & Regulations",
    "case-law": "Case Law",
    "prosecution-procedure": "Prosecution & Procedure / Statutory Guidance",
    "operational-guidance": "Operational Guidance",
    "policy-commentary": "Policy Papers & Commentary",
    "journal-articles": "Journal Articles",
    "global-regional": "Global & Regional Instruments",
}


def parse_frontmatter(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    m = re.search(r'```yaml\n(.+?)\n```\s*$', content, re.DOTALL)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def collect_entries():
    entries = []
    for d in ENTRY_DIRS:
        full = os.path.join(REPO_ROOT, d)
        for fp in glob.glob(os.path.join(full, "**", "*.md"), recursive=True):
            fm = parse_frontmatter(fp)
            if fm:
                fm["_path"] = os.path.relpath(fp, REPO_ROOT)
                fm["_theme"] = d
                entries.append(fm)
    return entries


def build_json(entries):
    out = []
    for e in entries:
        row = {k: v for k, v in e.items() if not k.startswith("_")}
        row["file"] = e["_path"]
        out.append(row)
    path = os.path.join(REPO_ROOT, "index.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Wrote {path} ({len(out)} entries)")


def build_markdown(entries):
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for e in entries:
        grouped[e["_theme"]][e["bucket"]][e["jurisdiction"]].append(e)

    lines = [
        "# IJM Legal & Policy Resource Library — Index",
        "",
        f"*Auto-generated on {date.today().isoformat()} by `scripts/build-index.py`. Do not edit manually.*",
        "",
        f"**Total entries: {len(entries)}**",
        "",
    ]

    # Stats table
    lines += ["| Jurisdiction | Count |", "|---|---|"]
    jcounts = defaultdict(int)
    for e in entries:
        jcounts[e["jurisdiction"]] += 1
    for j in sorted(jcounts, key=lambda x: -jcounts[x]):
        lines.append(f"| {j} | {jcounts[j]} |")
    lines.append("")

    # Grouped listing
    for theme in ENTRY_DIRS:
        if theme not in grouped:
            continue
        lines += [f"## {THEME_LABELS.get(theme, theme)}", ""]
        for bucket in BUCKET_ORDER:
            if bucket not in grouped[theme]:
                continue
            lines += [f"### {BUCKET_LABELS.get(bucket, bucket)}", ""]
            for juris in sorted(grouped[theme][bucket]):
                items = grouped[theme][bucket][juris]
                lines.append(f"**{juris}**")
                lines.append("")
                for e in sorted(items, key=lambda x: str(x.get("date_issued", ""))):
                    access_badge = "🔒" if e.get("access") == "backend-needed" else "🔓"
                    link = e.get("source_url", "")
                    title = e.get("title", "Untitled")
                    title_md = f"[{title}]({link})" if link else title
                    tags = ", ".join(f"`{t}`" for t in e.get("victim_id_tags", []))
                    lines.append(f"- {access_badge} **{title_md}** ({e.get('document_type', '?')}, {e.get('date_issued', '?')})")
                    lines.append(f"  - *{e.get('summary', 'No summary.')}*")
                    if tags:
                        lines.append(f"  - Tags: {tags}")
                    lines.append(f"  - Entry: [`{e['_path']}`]({e['_path']})")
                    if e.get("local_file"):
                        lines.append(f"  - Source file: [`{e['local_file']}`]({e['local_file']})")
                    lines.append("")

    path = os.path.join(REPO_ROOT, "INDEX.md")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path} ({len(entries)} entries)")


def main():
    entries = collect_entries()
    if not entries:
        print("No entries found.")
        sys.exit(0)
    build_json(entries)
    if "--json-only" not in sys.argv:
        build_markdown(entries)


if __name__ == "__main__":
    main()
