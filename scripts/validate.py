#!/usr/bin/env python3
"""Validate all document entries against schema.yml controlled vocabularies."""

import sys, os, glob, yaml, re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.yml")
ENTRY_DIRS = [
    "victim-identification",
    "elements-defences",
    "international-cooperation",
]

REQUIRED_FIELDS = [
    "title", "jurisdiction", "bucket", "document_type",
    "issuing_body", "date_issued", "status", "access",
    "victim_id_tags", "summary",
]

FIELD_TO_SCHEMA_KEY = {
    "jurisdiction": "jurisdictions",
    "bucket": "buckets",
    "document_type": "document_types",
    "status": "statuses",
    "access": "access_levels",
    "backend_source": "backend_sources",
    "backend_confidence": "backend_confidence",
    "victim_id_tags": "victim_id_tags",
}


def parse_frontmatter(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    match = re.search(r'```yaml\n(.+?)\n```\s*$', content, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1))


def validate_entry(filepath, schema):
    errors = []
    fm = parse_frontmatter(filepath)
    if fm is None:
        return [f"  No YAML frontmatter found"]

    for field in REQUIRED_FIELDS:
        if field not in fm or fm[field] is None:
            errors.append(f"  Missing required field: {field}")

    for field, schema_key in FIELD_TO_SCHEMA_KEY.items():
        if field not in fm or fm[field] is None:
            continue
        allowed = schema[schema_key]
        val = fm[field]
        if isinstance(val, list):
            for v in val:
                if v not in allowed:
                    errors.append(f"  Invalid {field} value: '{v}' (allowed: {allowed})")
        else:
            if val not in allowed:
                errors.append(f"  Invalid {field} value: '{val}' (allowed: {allowed})")

    if fm.get("access") == "backend-needed":
        for f in ["backend_source", "backend_confidence", "retrieval_notes"]:
            if f not in fm or fm[f] is None:
                errors.append(f"  Backend-needed entry missing: {f}")

    return errors


def main():
    with open(SCHEMA_PATH) as f:
        schema = yaml.safe_load(f)

    md_files = []
    for d in ENTRY_DIRS:
        full = os.path.join(REPO_ROOT, d)
        md_files.extend(glob.glob(os.path.join(full, "**", "*.md"), recursive=True))

    if not md_files:
        print("No document entries found.")
        sys.exit(0)

    total_errors = 0
    for fp in sorted(md_files):
        rel = os.path.relpath(fp, REPO_ROOT)
        errs = validate_entry(fp, schema)
        if errs:
            print(f"FAIL  {rel}")
            for e in errs:
                print(e)
            total_errors += len(errs)
        else:
            print(f"  OK  {rel}")

    print(f"\n{'='*50}")
    print(f"Files checked: {len(md_files)}  |  Errors: {total_errors}")
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
