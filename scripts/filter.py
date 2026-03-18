#!/usr/bin/env python3
"""Filter and query the document library from the command line.

Usage examples:
    python scripts/filter.py --jurisdiction UK
    python scripts/filter.py --bucket case-law --jurisdiction US
    python scripts/filter.py --tag child-victim-identification
    python scripts/filter.py --access backend-needed
    python scripts/filter.py --search "modern slavery"
    python scripts/filter.py --jurisdiction EU --bucket legislation --format json
"""

import argparse, os, glob, re, json, yaml, sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_DIRS = [
    "victim-identification", "prosecution", "investigations",
    "victim-compensation", "elements-defences", "international-cooperation",
]


def parse_frontmatter(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    m = re.search(r'```yaml\n(.+?)\n```\s*$', content, re.DOTALL)
    if not m:
        return None, ""
    yaml_data = yaml.safe_load(m.group(1))
    body = content[:m.start()]
    return yaml_data, body


def collect():
    entries = []
    for d in ENTRY_DIRS:
        full = os.path.join(REPO_ROOT, d)
        for fp in glob.glob(os.path.join(full, "**", "*.md"), recursive=True):
            fm, body = parse_frontmatter(fp)
            if fm:
                fm["_path"] = os.path.relpath(fp, REPO_ROOT)
                fm["_body"] = body
                entries.append(fm)
    return entries


def matches(entry, args):
    if args.jurisdiction and entry.get("jurisdiction") != args.jurisdiction:
        return False
    if args.bucket and entry.get("bucket") != args.bucket:
        return False
    if args.tag and args.tag not in entry.get("tags", []):
        return False
    if args.access and entry.get("access") != args.access:
        return False
    if args.doc_type and entry.get("document_type") != args.doc_type:
        return False
    if args.search:
        needle = args.search.lower()
        haystack = " ".join([
            str(entry.get("title", "")),
            str(entry.get("summary", "")),
            str(entry.get("issuing_body", "")),
            entry.get("_body", ""),
        ]).lower()
        if needle not in haystack:
            return False
    return True


def display_table(results):
    if not results:
        print("No matching entries.")
        return
    print(f"\n{'='*90}")
    print(f"  {len(results)} result(s)")
    print(f"{'='*90}\n")
    for e in results:
        access = "🔒 BACKEND" if e.get("access") == "backend-needed" else "🔓 PUBLIC"
        print(f"  [{e.get('jurisdiction','?')}] [{e.get('bucket','?')}] {access}")
        print(f"  {e.get('title','Untitled')}")
        print(f"  {e.get('issuing_body','?')} | {e.get('date_issued','?')} | {e.get('document_type','?')}")
        if e.get("source_url"):
            print(f"  Link: {e['source_url']}")
        print(f"  Summary: {e.get('summary','—')}")
        tags = e.get("tags", [])
        if tags:
            print(f"  Tags: {', '.join(tags)}")
        print(f"  File: {e['_path']}")
        print()


def main():
    p = argparse.ArgumentParser(description="Filter the IJM document library")
    p.add_argument("--jurisdiction", "-j", help="Filter by jurisdiction (US, EU, UK, AU, ECHR, ASEAN, UN, etc.)")
    p.add_argument("--bucket", "-b", help="Filter by bucket (legislation, case-law, etc.)")
    p.add_argument("--tag", "-t", help="Filter by victim-ID tag")
    p.add_argument("--access", "-a", help="Filter by access level (public, backend-needed)")
    p.add_argument("--doc-type", "-d", help="Filter by document type")
    p.add_argument("--search", "-s", help="Free-text search across title, summary, body")
    p.add_argument("--format", "-f", default="table", choices=["table", "json", "paths"],
                   help="Output format (default: table)")
    args = p.parse_args()

    entries = collect()
    results = [e for e in entries if matches(e, args)]
    results.sort(key=lambda e: (e.get("jurisdiction",""), e.get("bucket",""), str(e.get("date_issued",""))))

    if args.format == "json":
        out = [{k: v for k, v in e.items() if not k.startswith("_")} for e in results]
        print(json.dumps(out, indent=2, default=str))
    elif args.format == "paths":
        for e in results:
            print(e["_path"])
    else:
        display_table(results)


if __name__ == "__main__":
    main()
