#!/usr/bin/env python3
"""Import new entries from resources.json into the library.

Usage:
    python scripts/import-resources.py /path/to/resources.json
    python scripts/import-resources.py /path/to/resources.json --dry-run
"""

import json, os, sys, re, textwrap
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mapping: resource ID -> (folder, bucket, jurisdiction_code, document_type, filename, tags)
IMPORT_MAP = {
    2: ("victim-identification", "legislation", "US", "act-statute",
        "us-jvta-2015.md",
        ["definition-scope", "child-victim-identification", "compensation-fund"]),
    3: ("prosecution", "legislation", "US", "act-statute",
        "us-trafficking-survivors-relief-act-2026.md",
        ["non-punishment-link"]),
    5: ("victim-identification", "legislation", "US", "act-statute",
        "us-uflpa-2021.md",
        ["supply-chain-due-diligence", "labour-exploitation-indicators"]),
    8: ("victim-identification", "legislation", "UK", "act-statute",
        "uk-human-trafficking-exploitation-ni-2015.md",
        ["definition-scope", "non-punishment-link", "first-responder-duties"]),
    11: ("victim-identification", "legislation", "AU", "act-statute",
         "au-modern-slavery-act-2018-nsw.md",
         ["supply-chain-due-diligence", "transparency-reporting"]),
    12: ("victim-identification", "legislation", "IN", "act-statute",
         "in-bonded-labour-abolition-act-1976.md",
         ["definition-scope", "labour-exploitation-indicators"]),
    13: ("victim-identification", "legislation", "IN", "act-statute",
         "in-constitution-arts-21-23-24.md",
         ["definition-scope", "labour-exploitation-indicators"]),
    14: ("victim-identification", "legislation", "IN", "act-statute",
         "in-immoral-traffic-prevention-act-1956.md",
         ["definition-scope", "sex-trafficking-indicators"]),
    21: ("investigations", "operational-guidance", "UK", "guideline-sop",
         "uk-college-of-policing-modern-slavery.md",
         ["proactive-intelligence", "financial-investigation", "victim-engagement-interview", "multi-agency-cooperation"]),
    22: ("prosecution", "operational-guidance", "US", "guideline-sop",
         "us-doj-htpu-resources.md",
         ["offence-elements", "sentencing-penalty", "evidence-corroboration"]),
    25: ("victim-identification", "operational-guidance", "AU", "guideline-sop",
         "au-ag-modern-slavery-guidance.md",
         ["supply-chain-due-diligence", "transparency-reporting"]),
    26: ("prosecution", "policy-commentary", "UK", "report",
         "uk-iasc-s45-defence-call-for-evidence.md",
         ["statutory-defence-s45", "non-punishment-link", "abuse-of-process"]),
    29: ("prosecution", "case-law", "UK", "judgment-opinion",
         "uk-r-v-aad-2022.md",
         ["statutory-defence-s45", "abuse-of-process", "non-punishment-link"]),
    30: ("prosecution", "case-law", "UK", "judgment-opinion",
         "uk-r-v-brecani-2021.md",
         ["statutory-defence-s45", "evidence-corroboration"]),
    34: ("victim-compensation", "case-law", "US", "judgment-opinion",
         "us-doe-v-apple-2024.md",
         ["civil-remedy", "supply-chain-due-diligence"]),
    35: ("prosecution", "case-law", "IN", "judgment-opinion",
         "in-bandhua-mukti-morcha-1984.md",
         ["definition-scope", "labour-exploitation-indicators", "offence-elements"]),
    37: ("victim-identification", "operational-guidance", "UNODC", "toolkit-manual",
         "unodc-first-aid-kit-first-responders.md",
         ["first-responder-duties", "indicators-screening", "interviewing-trauma-informed"]),
    38: ("victim-identification", "operational-guidance", "US", "toolkit-manual",
         "us-shared-hope-intervene-tool.md",
         ["indicators-screening", "child-victim-identification", "sex-trafficking-indicators"]),
    40: ("investigations", "operational-guidance", "ILO", "toolkit-manual",
         "ilo-ioe-employers-handbook-3rd-ed-2025.md",
         ["supply-chain-due-diligence", "labour-exploitation-indicators", "indicators-screening"]),
    41: ("victim-compensation", "policy-commentary", "US", "report",
         "us-htlc-federal-civil-trafficking-report.md",
         ["civil-remedy", "mandatory-restitution"]),
    42: ("victim-compensation", "legislation", "UK", "act-statute",
         "uk-msa-2015-reparation-orders-ss8-10.md",
         ["reparation-order", "sentencing-penalty"]),
    43: ("victim-compensation", "legislation", "US", "act-statute",
         "us-mandatory-restitution-18-usc-1593.md",
         ["mandatory-restitution", "sentencing-penalty"]),
    45: ("prosecution", "operational-guidance", "UNODC", "toolkit-manual",
         "unodc-case-digest-evidential-issues.md",
         ["evidence-corroboration", "offence-elements", "victimless-prosecution"]),
    46: ("international-cooperation", "operational-guidance", "EU", "guideline-sop",
         "eu-eurojust-jits-trafficking.md",
         ["joint-investigation-team", "mutual-legal-assistance"]),
    48: ("prosecution", "policy-commentary", "US", "report",
         "us-hti-federal-trafficking-report.md",
         ["offence-elements", "sentencing-penalty", "evidence-corroboration"]),
    49: ("victim-compensation", "policy-commentary", "US", "database-portal",
         "us-htlc-civil-criminal-databases.md",
         ["civil-remedy", "mandatory-restitution"]),
    51: ("prosecution", "policy-commentary", "UK", "resource-collection",
         "uk-modern-slavery-pec-resources.md",
         ["offence-elements", "victimless-prosecution", "evidence-corroboration"]),
    54: ("victim-identification", "policy-commentary", "US", "report",
         "us-shared-hope-state-report-cards.md",
         ["child-victim-identification", "non-punishment-link", "sex-trafficking-indicators"]),
    55: ("prosecution", "operational-guidance", "ILO", "toolkit-manual",
         "ilo-forced-labour-casebook-2009.md",
         ["offence-elements", "evidence-corroboration", "labour-exploitation-indicators"]),
}

# Jurisdiction display -> code mapping for resources.json
JURIS_MAP = {
    "US": "US",
    "UK": "UK",
    "Australia": "AU",
    "India": "IN",
    "International": None,  # handled per-entry in IMPORT_MAP
}


def make_entry(resource, folder, bucket, jurisdiction, doc_type, filename, tags):
    """Generate a markdown entry file content from a resource JSON object."""
    title = resource["title"]
    summary = resource["summary"]
    key_pinpoint = resource.get("keyParas", "")
    url = resource.get("url", "")

    tags_yaml = "\n".join(f"  - {t}" for t in tags)

    yaml_block = f'''title: "{title}"
jurisdiction: {jurisdiction}
bucket: {bucket}
document_type: {doc_type}
issuing_body: "{resource.get('issuing_body', infer_issuing_body(resource, jurisdiction))}"
date_issued: {infer_date(resource)}
status: current
source_url: "{url}"
access: public

summary: >
  {summary}

key_pinpoint: "{key_pinpoint}"

tags:
{tags_yaml}

added_by: "Claude (import from resources.json)"
date_added: {date.today().isoformat()}'''

    return yaml_block


def infer_issuing_body(resource, jurisdiction):
    """Infer issuing body from context."""
    title = resource["title"]
    rtype = resource.get("type", "")

    if rtype == "Case Law":
        if jurisdiction == "UK":
            if "EWCA" in title or "Court of Appeal" in title:
                return "Court of Appeal (Criminal Division)"
            if "UKSC" in title or "Supreme Court" in title:
                return "UK Supreme Court"
            return "England & Wales Courts"
        if jurisdiction == "US":
            if "SCOTUS" in resource.get("summary", "") or "Supreme Court" in resource.get("summary", ""):
                return "US Supreme Court"
            if "D.C. Cir" in title:
                return "US Court of Appeals, D.C. Circuit"
            return "US Federal Courts"
        if jurisdiction == "IN":
            if "SC " in title or "Supreme Court" in resource.get("summary", "") or "AIR" in resource.get("summary", ""):
                return "Supreme Court of India"
            return "Indian Courts"
        if "ECtHR" in title or "ECHR" in title or "Grand Chamber" in title:
            return "European Court of Human Rights"
        return "Courts"

    if "ILO" in title:
        return "ILO"
    if "UNODC" in title:
        return "UNODC"
    if "Eurojust" in title:
        return "Eurojust"
    if "DOJ" in title or "HTPU" in title:
        return "US Department of Justice"
    if "College of Policing" in title:
        return "College of Policing"
    if "AG Dept" in title or "Attorney" in title or "AG" in resource.get("summary", "")[:50]:
        return "Attorney-General's Department"
    if "Anti-Slavery Commissioner" in title or "IASC" in title:
        return "Independent Anti-Slavery Commissioner"
    if "Shared Hope" in title:
        return "Shared Hope International"
    if "HTLC" in title or "Human Trafficking Legal Center" in title:
        return "Human Trafficking Legal Center"
    if "HTI" in title or "Human Trafficking Institute" in title:
        return "Human Trafficking Institute"
    if "PEC" in title or "Modern Slavery PEC" in title:
        return "Modern Slavery PEC"
    if "AFP" in title:
        return "Australian Federal Police"

    # Legislature-based
    if jurisdiction == "US":
        return "US Congress"
    if jurisdiction == "UK":
        return "UK Parliament"
    if jurisdiction == "AU":
        if "NSW" in title:
            return "NSW Parliament"
        return "Australian Parliament"
    if jurisdiction == "IN":
        return "Parliament of India"

    return "Unknown"


def infer_date(resource):
    """Extract date from title or summary."""
    title = resource["title"]
    summary = resource.get("summary", "")

    # Look for year in title
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', title)
    if years:
        return years[-1]  # Use last year mentioned (most specific)

    # Look in summary
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', summary)
    if years:
        return years[0]

    return "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import-resources.py /path/to/resources.json [--dry-run]")
        sys.exit(1)

    json_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    with open(json_path) as f:
        resources = json.load(f)

    res_by_id = {r["id"]: r for r in resources}

    created = 0
    skipped = 0

    for rid, (folder, bucket, juris, doc_type, filename, tags) in sorted(IMPORT_MAP.items()):
        if rid not in res_by_id:
            print(f"  SKIP  ID {rid}: not in resources.json")
            skipped += 1
            continue

        resource = res_by_id[rid]
        dest_dir = os.path.join(REPO_ROOT, folder, bucket)
        dest_path = os.path.join(dest_dir, filename)

        if os.path.exists(dest_path):
            print(f"  EXISTS  {os.path.relpath(dest_path, REPO_ROOT)}")
            skipped += 1
            continue

        yaml_content = make_entry(resource, folder, bucket, juris, doc_type, filename, tags)

        # Build the full file (body will be generated by render-body.py later)
        # For now, create a minimal file with just the YAML block
        md_content = f"<!-- Body is auto-generated by scripts/render-body.py -->\n\n---\n\n<!-- entry metadata (parsed by scripts — do not remove) -->\n```yaml\n{yaml_content}\n```\n"

        if dry_run:
            print(f"  WOULD CREATE  {os.path.relpath(dest_path, REPO_ROOT)}")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"  CREATED  {os.path.relpath(dest_path, REPO_ROOT)}")

        created += 1

    action = "would create" if dry_run else "created"
    print(f"\n{'='*50}")
    print(f"{action.capitalize()}: {created}  |  Skipped: {skipped}")


if __name__ == "__main__":
    main()
