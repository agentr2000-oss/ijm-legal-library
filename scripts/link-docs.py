#!/usr/bin/env python3
"""Update entry frontmatter with local_file paths after download.

Run this after download.py to write the local_file field into each entry
that has a corresponding file in docs/.

Usage:
    python scripts/link-docs.py              # update all entries
    python scripts/link-docs.py --dry-run    # preview changes
"""

import argparse, glob, os, re, yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
ENTRY_DIRS = ["victim-identification", "elements-defences", "international-cooperation"]


def find_doc_file(entry_path):
    """Find the downloaded doc file corresponding to an entry."""
    rel = Path(entry_path).relative_to(REPO_ROOT)
    base = DOCS_DIR / rel.with_suffix("")

    for ext in [".pdf", ".html", ".doc", ".docx"]:
        candidate = base.with_suffix(ext)
        if candidate.exists():
            return str(candidate.relative_to(REPO_ROOT))
    return None


def update_local_file(entry_path, doc_path, dry_run=False):
    """Insert or update local_file in frontmatter."""
    with open(entry_path, "r") as f:
        content = f.read()

    m = re.match(r"^(---\n)(.+?)(\n---)", content, re.DOTALL)
    if not m:
        return False, "No frontmatter"

    fm_text = m.group(2)

    # Check if local_file already set correctly
    if f'local_file: "{doc_path}"' in fm_text:
        return False, "Already set"

    # Replace or insert local_file
    if re.search(r'^local_file:', fm_text, re.MULTILINE):
        new_fm = re.sub(r'^local_file:.*$', f'local_file: "{doc_path}"', fm_text, flags=re.MULTILINE)
    else:
        # Insert after access line
        new_fm = re.sub(
            r'^(access:.*?)$',
            f'\\1\nlocal_file: "{doc_path}"',
            fm_text,
            flags=re.MULTILINE
        )

    if dry_run:
        return True, f"Would set local_file: {doc_path}"

    new_content = m.group(1) + new_fm + m.group(3) + content[m.end():]
    with open(entry_path, "w") as f:
        f.write(new_content)

    return True, f"Set local_file: {doc_path}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", "-n", action="store_true")
    args = p.parse_args()

    updated = 0
    for d in ENTRY_DIRS:
        full = REPO_ROOT / d
        for fp in sorted(full.glob("**/*.md")):
            doc_path = find_doc_file(fp)
            if not doc_path:
                continue

            changed, msg = update_local_file(fp, doc_path, dry_run=args.dry_run)
            rel = fp.relative_to(REPO_ROOT)
            if changed:
                print(f"  UPDATE  {rel}  →  {msg}")
                updated += 1
            # silently skip already-set entries

    print(f"\nUpdated {updated} entries.")


if __name__ == "__main__":
    main()
