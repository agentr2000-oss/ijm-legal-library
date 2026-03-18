#!/usr/bin/env python3
"""One-time migration: rename victim_id_tags -> tags in all entry YAML blocks."""

import os, glob, re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_DIRS = [
    "victim-identification",
    "elements-defences",
    "international-cooperation",
]


def migrate_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace in YAML block: victim_id_tags: -> tags:
    new_content = content.replace("victim_id_tags:", "tags:")

    # Also replace in rendered body heading
    new_content = new_content.replace("## Victim Identification Tags", "## Tags")

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    md_files = []
    for d in ENTRY_DIRS:
        full = os.path.join(REPO_ROOT, d)
        md_files.extend(glob.glob(os.path.join(full, "**", "*.md"), recursive=True))

    changed = 0
    for fp in sorted(md_files):
        rel = os.path.relpath(fp, REPO_ROOT)
        if migrate_file(fp):
            changed += 1
            print(f"  MIGRATED  {rel}")
        else:
            print(f"  OK        {rel}")

    print(f"\n{'='*50}")
    print(f"Files checked: {len(md_files)}  |  Migrated: {changed}")


if __name__ == "__main__":
    main()
