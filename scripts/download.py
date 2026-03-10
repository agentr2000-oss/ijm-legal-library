#!/usr/bin/env python3
"""Download source PDFs for all public entries that have a source_url.

Usage:
    python scripts/download.py                    # download all missing PDFs
    python scripts/download.py --jurisdiction UK   # only UK entries
    python scripts/download.py --force             # re-download even if file exists
    python scripts/download.py --dry-run           # show what would be downloaded
    python scripts/download.py --entry victim-identification/legislation/us-tvpa-2000.md
"""

import argparse, glob, os, re, sys, time, yaml
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
ENTRY_DIRS = ["victim-identification", "elements-defences", "international-cooperation"]
USER_AGENT = "IJM-Legal-Library/1.0 (research; non-commercial)"

# Map of URL patterns to expected content types / download strategies
DIRECT_PDF_DOMAINS = [
    "hudoc.echr.coe.int",
    "eur-lex.europa.eu",
    "austlii.edu.au",
    "bailii.org",
    "unodc.org",
    "ilo.org",
    "osce.org",
]


def parse_frontmatter(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    m = re.search(r'```yaml\n(.+?)\n```\s*$', content, re.DOTALL)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def entry_to_pdf_path(entry_path):
    """Convert entry .md path to corresponding docs/ .pdf path."""
    rel = Path(entry_path).relative_to(REPO_ROOT)
    return DOCS_DIR / rel.with_suffix(".pdf")


def download_file(url, dest, dry_run=False):
    """Download a URL to a local path. Returns (success, message)."""
    if dry_run:
        return True, f"DRY RUN: would download {url}"

    dest.parent.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": USER_AGENT}
    req = Request(url, headers=headers)

    try:
        with urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()

            # Check if we got a PDF
            if data[:5] == b"%PDF-":
                with open(dest, "wb") as f:
                    f.write(data)
                size_kb = len(data) / 1024
                return True, f"OK ({size_kb:.0f} KB)"

            # Check if we got HTML (common for legislation sites)
            if b"<html" in data[:500].lower() or "text/html" in content_type:
                # Save as .html instead — still useful
                html_dest = dest.with_suffix(".html")
                with open(html_dest, "wb") as f:
                    f.write(data)
                size_kb = len(data) / 1024
                return True, f"OK — saved as .html ({size_kb:.0f} KB, source is HTML not PDF)"

            # Unknown format — save with original extension
            with open(dest, "wb") as f:
                f.write(data)
            return True, f"OK (content-type: {content_type})"

    except HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except URLError as e:
        return False, f"URL error: {e.reason}"
    except Exception as e:
        return False, f"Error: {e}"


def collect_entries(args):
    entries = []
    for d in ENTRY_DIRS:
        full = REPO_ROOT / d
        for fp in sorted(full.glob("**/*.md")):
            fm = parse_frontmatter(fp)
            if not fm:
                continue
            if fm.get("access") != "public":
                continue
            if not fm.get("source_url"):
                continue
            if args.jurisdiction and fm.get("jurisdiction") != args.jurisdiction:
                continue
            if args.entry and str(fp.relative_to(REPO_ROOT)) != args.entry:
                continue
            entries.append((fp, fm))
    return entries


def main():
    p = argparse.ArgumentParser(description="Download source documents for library entries")
    p.add_argument("--jurisdiction", "-j", help="Only download for this jurisdiction")
    p.add_argument("--entry", "-e", help="Only download for this specific entry path")
    p.add_argument("--force", "-f", action="store_true", help="Re-download even if file exists")
    p.add_argument("--dry-run", "-n", action="store_true", help="Show what would be downloaded")
    p.add_argument("--delay", type=float, default=1.0, help="Seconds between requests (default: 1.0)")
    args = p.parse_args()

    entries = collect_entries(args)
    if not entries:
        print("No downloadable entries found.")
        sys.exit(0)

    print(f"Found {len(entries)} downloadable entries\n")

    stats = {"downloaded": 0, "skipped": 0, "failed": 0, "exists": 0}

    for fp, fm in entries:
        pdf_path = entry_to_pdf_path(fp)
        rel = fp.relative_to(REPO_ROOT)
        url = fm["source_url"]

        if pdf_path.exists() and not args.force:
            # Also check .html variant
            html_path = pdf_path.with_suffix(".html")
            if html_path.exists() and not args.force:
                print(f"  EXISTS  {rel}")
                stats["exists"] += 1
                continue
            if not pdf_path.exists():
                pass  # proceed to download
            else:
                print(f"  EXISTS  {rel}")
                stats["exists"] += 1
                continue

        print(f"  FETCH   {rel}")
        print(f"          {url}")

        ok, msg = download_file(url, pdf_path, dry_run=args.dry_run)

        if ok:
            print(f"          {msg}")
            stats["downloaded"] += 1
        else:
            print(f"          FAILED: {msg}")
            stats["failed"] += 1

        if not args.dry_run:
            time.sleep(args.delay)

    print(f"\n{'='*60}")
    print(f"Downloaded: {stats['downloaded']}  |  Existed: {stats['exists']}  |  Failed: {stats['failed']}")

    # Write a manifest of what we have
    if not args.dry_run:
        manifest_path = DOCS_DIR / "MANIFEST.md"
        manifest_lines = [
            "# Downloaded Documents Manifest",
            "",
            f"*Last run: {time.strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "| Entry | File | Size |",
            "|---|---|---|",
        ]
        for f in sorted(DOCS_DIR.glob("**/*")):
            if f.is_file() and f.name != "MANIFEST.md" and f.name != ".gitkeep":
                size = f.stat().st_size / 1024
                manifest_lines.append(f"| `{f.relative_to(DOCS_DIR)}` | {f.suffix} | {size:.0f} KB |")

        manifest_path.write_text("\n".join(manifest_lines) + "\n")


if __name__ == "__main__":
    main()
