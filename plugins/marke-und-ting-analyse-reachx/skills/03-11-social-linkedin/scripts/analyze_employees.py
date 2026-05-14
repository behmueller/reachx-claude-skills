#!/usr/bin/env python3
"""
Helper-Script für Department-Klassifizierung und Tenure-Analyse.

Wird vom linkedin-competitor-research-Skill genutzt, um aus
Mitarbeiter-Daten die Aggregat-Statistiken für den Report zu berechnen.

Usage:
    python analyze_employees.py listing.csv [deep.csv] > stats.json

Input:
    listing.csv: Spalten name, profile_url, headline, current_position,
                 current_company, location
    deep.csv (optional): Zusätzliche Spalten aus Deep-Scrape mit
                         current_position_start_date, experience (JSON-String)

Output:
    JSON mit:
    - department_distribution: {bucket: count}
    - tenure_distribution: {bucket: count}
    - tenure_stats: {median, mean, coverage_pct}
"""

import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Department-Klassifizierung
# ---------------------------------------------------------------------------
# Reihenfolge ist signifikant: erste passende Kategorie gewinnt.
# Das ist wichtig, damit "CMO" als Leadership zählt, nicht als Marketing.

DEPARTMENT_PATTERNS = [
    # Leadership / C-Level zuerst – schlägt alle Funktionen
    ("Leadership", [
        r"\bCEO\b", r"\bCFO\b", r"\bCTO\b", r"\bCMO\b", r"\bCOO\b", r"\bCIO\b",
        r"\bCDO\b", r"\bCRO\b", r"\bCISO\b",
        r"\bGeschäftsführ", r"\bVorstand\b", r"\bPresident\b",
        r"\bManaging Director\b", r"\bMD\b(?!\w)",
        r"\bFounder\b", r"\bCo-?Founder\b", r"\bGründer\b",
    ]),
    ("HR/People", [
        r"\bHR\b", r"\bPeople\b", r"\bRecruit", r"\bTalent\b",
        r"\bPersonal\b(?!.*Sales)", r"\bHuman Resources\b",
        r"\bChief People\b", r"\bCHRO\b",
    ]),
    ("Marketing", [
        r"\bMarketing\b", r"\bCommunications?\b", r"\bKommunikation\b",
        r"\bContent\b", r"\bBrand\b", r"\bPR\b(?!\w)", r"\bPublic Relations\b",
        r"\bDemand Gen", r"\bGrowth\b", r"\bSEO\b", r"\bSEA\b",
        r"\bSocial Media\b", r"\bDigital Marketing\b", r"\bCampaign\b",
    ]),
    ("Sales", [
        r"\bSales\b", r"\bVertrieb\b", r"\bAccount Executive\b", r"\bAE\b(?!\w)",
        r"\bBDR\b", r"\bSDR\b", r"\bBusiness Development\b", r"\bNew Business\b",
        r"\bChannel Sales\b", r"\bKey Account\b", r"\bRevenue\b",
    ]),
    ("Engineering", [
        r"\bEngineer\b", r"\bDeveloper\b", r"\bEntwickler\b",
        r"\bSoftware\b", r"\bDevOps\b", r"\bSRE\b",
        r"\bData (Engineer|Scientist)\b", r"\bML Engineer\b", r"\bAI Engineer\b",
        r"\bQA\b", r"\bBackend\b", r"\bFrontend\b", r"\bFull[-\s]?Stack\b",
        r"\bArchitect\b",
    ]),
    ("Product", [
        r"\bProduct Manager\b", r"\bProduct Owner\b", r"\bPM\b(?!\w)", r"\bPO\b(?!\w)",
        r"\bUX\b", r"\bUI\b", r"\bDesigner?\b", r"\bProduct Design\b",
    ]),
    ("Finance", [
        r"\bFinance\b", r"\bFinanzen\b", r"\bControlling\b", r"\bAccounting\b",
        r"\bFP&A\b", r"\bTreasury\b", r"\bBuchhalt",
    ]),
    ("Operations", [
        r"\bOperations\b", r"\bOps\b(?!\w)", r"\bSupply Chain\b", r"\bLogistics\b",
        r"\bLogistik\b", r"\bPMO\b", r"\bProject Management\b",
    ]),
    ("Customer Success", [
        r"\bCustomer Success\b", r"\bCSM\b", r"\bOnboarding\b",
        r"\bCustomer Support\b", r"\bSupport Engineer\b",
    ]),
    ("Legal", [
        r"\bLegal\b", r"\bCounsel\b", r"\bCompliance\b",
        r"\bDatenschutz\b", r"\bPrivacy\b", r"\bGRC\b",
    ]),
]


def classify_department(headline: str, position: str = "") -> str:
    """Klassifiziere Mitarbeiter in Department-Bucket basierend auf Headline/Position."""
    text = f"{headline} {position}".strip()
    if not text:
        return "Other"
    for bucket, patterns in DEPARTMENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, text, flags=re.IGNORECASE):
                return bucket
    return "Other"


# ---------------------------------------------------------------------------
# Tenure-Berechnung
# ---------------------------------------------------------------------------

DATE_FORMATS = [
    "%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%m/%Y", "%Y",
    "%b %Y", "%B %Y",  # "Jan 2023", "January 2023"
]


def parse_date(s: Optional[str]) -> Optional[datetime]:
    """Parse einen Datums-String robust in unterschiedlichen Formaten."""
    if not s or not s.strip() or s.strip().lower() in ("present", "current", "now"):
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None


def tenure_months(start_date_str: Optional[str], reference_date: Optional[datetime] = None) -> Optional[int]:
    """Berechne Tenure in Monaten von start_date bis reference_date (default: heute)."""
    start = parse_date(start_date_str)
    if not start:
        return None
    ref = reference_date or datetime.utcnow()
    return (ref.year - start.year) * 12 + (ref.month - start.month)


def tenure_to_bucket(months: Optional[int]) -> str:
    """Mappe Tenure in Monaten auf einen Reporting-Bucket."""
    if months is None:
        return "unknown"
    years = months / 12
    if years < 1:
        return "<1 year"
    if years < 3:
        return "1-3 years"
    if years < 5:
        return "3-5 years"
    if years < 10:
        return "5-10 years"
    return ">10 years"


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def analyze(listing_path: str, deep_path: Optional[str] = None) -> dict:
    """Lade CSV(s), klassifiziere und aggregiere."""
    rows = []
    with open(listing_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Department-Verteilung über das gesamte Listing
    dept_counter = Counter()
    for row in rows:
        bucket = classify_department(row.get("headline", ""),
                                      row.get("current_position", ""))
        dept_counter[bucket] += 1
        row["department_inferred"] = bucket

    total_employees = len(rows)
    department_distribution = {
        bucket: {"count": count, "pct": round(count / total_employees * 100, 1)}
        for bucket, count in dept_counter.most_common()
    }

    # Tenure-Berechnung – nur, wenn Deep-Daten vorhanden
    tenure_stats = None
    tenure_distribution = {}

    if deep_path:
        deep_rows = []
        with open(deep_path, encoding="utf-8") as f:
            deep_rows = list(csv.DictReader(f))

        tenures = []
        for row in deep_rows:
            t = tenure_months(row.get("current_position_start_date"))
            if t is not None and t >= 0:
                tenures.append(t)

        coverage_pct = (
            round(len(tenures) / len(deep_rows) * 100, 1) if deep_rows else 0
        )

        if tenures:
            tenures_sorted = sorted(tenures)
            mid = len(tenures_sorted) // 2
            median = (
                tenures_sorted[mid] if len(tenures_sorted) % 2
                else (tenures_sorted[mid - 1] + tenures_sorted[mid]) / 2
            )
            mean = sum(tenures_sorted) / len(tenures_sorted)

            tenure_stats = {
                "median_months": round(median, 1),
                "median_years": round(median / 12, 1),
                "mean_months": round(mean, 1),
                "mean_years": round(mean / 12, 1),
                "sample_size": len(tenures),
                "coverage_pct": coverage_pct,
            }

            bucket_counter = Counter(tenure_to_bucket(t) for t in tenures)
            tenure_distribution = {
                bucket: {"count": count, "pct": round(count / len(tenures) * 100, 1)}
                for bucket, count in bucket_counter.most_common()
            }

    return {
        "total_employees_in_listing": total_employees,
        "department_distribution": department_distribution,
        "tenure_distribution": tenure_distribution,
        "tenure_stats": tenure_stats,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    listing = sys.argv[1]
    deep = sys.argv[2] if len(sys.argv) > 2 else None
    result = analyze(listing, deep)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
