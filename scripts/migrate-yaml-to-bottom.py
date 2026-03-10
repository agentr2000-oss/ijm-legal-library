#!/usr/bin/env python3
"""One-time migration: move YAML from frontmatter (top) to fenced code block (bottom).

Idempotent — skips files already in the new format.

Usage:
    python scripts/migrate-yaml-to-bottom.py           # migrate all entries
    python scripts/migrate-yaml-to-bottom.py --dry-run  # preview only
"""

import os, sys, re, glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY_DIRS = ["victim-identification", "elements-defences", "international-cooperation"]


def migrate_file(filepath, dry_run=False):
    """Migrate a single file. Returns (changed, message)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Already in new format — skip
    if re.search(r'```yaml\n.+?\n```\s*$', content, re.DOTALL):
        return False, "already migrated"

    # Extract old frontmatter
    m = re.match(r'^---\n(.+?)\n---\n*(.*)$', content, re.DOTALL)
    if not m:
        return False, "no frontmatter found"

    yaml_text = m.group(1)
    body = m.group(2).strip()

    # Build new content: body first, then YAML block at bottom
    new_content = body + "\n\n---\n\n<!-- entry metadata (parsed by scripts — do not remove) -->\n```yaml\n" + yaml_text + "\n```\n"

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return True, "migrated"


def main():
    dry_run = "--dry-run" in sys.argv

    md_files = []
    for d in ENTRY_DIRS:
        full = os.path.join(REPO_ROOT, d)
        md_files.extend(glob.glob(os.path.join(full, "**", "*.md"), recursive=True))

    if not md_files:
        print("No entry files found.")
        sys.exit(0)

    migrated = 0
    skipped = 0
    for fp in sorted(md_files):
        rel = os.path.relpath(fp, REPO_ROOT)
        changed, msg = migrate_file(fp, dry_run=dry_run)
        if changed:
            migrated += 1
            prefix = "WOULD MIGRATE" if dry_run else "MIGRATED"
            print(f"  {prefix}  {rel}")
        else:
            skipped += 1

    action = "would migrate" if dry_run else "migrated"
    print(f"\n{'='*50}")
    print(f"Files: {len(md_files)}  |  {action.capitalize()}: {migrated}  |  Skipped: {skipped}")


if __name__ == "__main__":
    main()
