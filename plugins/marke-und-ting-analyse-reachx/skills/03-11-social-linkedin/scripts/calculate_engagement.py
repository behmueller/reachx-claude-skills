#!/usr/bin/env python3
"""
Helper-Script für Engagement-Rate-Berechnung und Post-Aggregation.

Wird vom linkedin-competitor-research-Skill genutzt, um aus
Posts-CSVs die Aggregat-Statistiken für den Report zu berechnen:
- Durchschnittliche Engagement-Rate
- Format-Verteilung mit Performance pro Format
- Cluster-Verteilung mit Performance pro Cluster
- Top/Bottom-Posts
- Posting-Frequenz

Usage:
    python calculate_engagement.py posts.csv --followers 8500 > stats.json

CSV-Spalten (erwartet):
    date, post_url, format, text, likes, reposts, comments,
    rating_total (optional), theme_cluster (optional), tonality (optional)
"""

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional


def parse_int(s) -> int:
    """Robust int parsing – LinkedIn liefert manchmal '1,234' oder '1.2K'."""
    if s is None or s == "":
        return 0
    s = str(s).strip()
    if s.endswith("K") or s.endswith("k"):
        try:
            return int(float(s[:-1].replace(",", ".")) * 1000)
        except ValueError:
            return 0
    if s.endswith("M") or s.endswith("m"):
        try:
            return int(float(s[:-1].replace(",", ".")) * 1_000_000)
        except ValueError:
            return 0
    s = s.replace(",", "").replace(".", "")
    try:
        return int(s)
    except ValueError:
        return 0


def parse_date(s: str) -> Optional[datetime]:
    """Erwartet YYYY-MM-DD, fällt auf andere Formate zurück."""
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%d.%m.%Y"):
        try:
            return datetime.strptime(s.strip()[:len(fmt)+5], fmt)
        except ValueError:
            continue
    return None


def engagement_rate(likes: int, reposts: int, comments: int, followers: int) -> Optional[float]:
    """ER in Prozent. None, wenn keine Followerzahl vorhanden."""
    if not followers or followers <= 0:
        return None
    return (likes + reposts + comments) / followers * 100


def aggregate(posts_csv: str, followers: int) -> dict:
    """Lade Posts und berechne Aggregat-Statistiken."""
    rows = []
    with open(posts_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["likes_n"] = parse_int(row.get("likes"))
            row["reposts_n"] = parse_int(row.get("reposts"))
            row["comments_n"] = parse_int(row.get("comments"))
            row["date_dt"] = parse_date(row.get("date"))
            row["er"] = engagement_rate(
                row["likes_n"], row["reposts_n"], row["comments_n"], followers
            )
            rows.append(row)

    if not rows:
        return {"error": "Keine Posts in der CSV gefunden."}

    # Zeitraum bestimmen
    valid_dates = [r["date_dt"] for r in rows if r["date_dt"]]
    date_range = None
    weeks_covered = None
    if valid_dates:
        oldest, newest = min(valid_dates), max(valid_dates)
        date_range = {
            "oldest": oldest.strftime("%Y-%m-%d"),
            "newest": newest.strftime("%Y-%m-%d"),
            "days": (newest - oldest).days,
        }
        weeks_covered = max(date_range["days"] / 7, 1)

    # Engagement-Stats
    ers = [r["er"] for r in rows if r["er"] is not None]
    er_stats = None
    if ers:
        er_stats = {
            "mean": round(statistics.mean(ers), 3),
            "median": round(statistics.median(ers), 3),
            "min": round(min(ers), 3),
            "max": round(max(ers), 3),
        }

    # Format-Verteilung mit Per-Format-ER
    format_groups = defaultdict(list)
    for r in rows:
        fmt = (r.get("format") or "unknown").strip().lower()
        format_groups[fmt].append(r)

    format_stats = {}
    for fmt, group in format_groups.items():
        group_ers = [r["er"] for r in group if r["er"] is not None]
        format_stats[fmt] = {
            "count": len(group),
            "pct": round(len(group) / len(rows) * 100, 1),
            "avg_er": round(statistics.mean(group_ers), 3) if group_ers else None,
            "avg_likes": round(statistics.mean([r["likes_n"] for r in group]), 1),
        }

    # Cluster-Verteilung (falls Spalte existiert)
    cluster_stats = {}
    if rows[0].get("theme_cluster") is not None:
        cluster_groups = defaultdict(list)
        for r in rows:
            cluster = (r.get("theme_cluster") or "Uncategorized").strip()
            # bei Mehrfach-Clustern (z.B. "Thought Leadership, Recruiting")
            for c in [c.strip() for c in cluster.split(",") if c.strip()]:
                cluster_groups[c].append(r)
        for cluster, group in cluster_groups.items():
            group_ers = [r["er"] for r in group if r["er"] is not None]
            cluster_stats[cluster] = {
                "count": len(group),
                "avg_er": round(statistics.mean(group_ers), 3) if group_ers else None,
            }

    # Posting-Frequenz
    posts_per_week = None
    if weeks_covered:
        posts_per_week = round(len(rows) / weeks_covered, 2)

    # Top 3 / Bottom 3 nach ER
    rows_with_er = [r for r in rows if r["er"] is not None]
    top_3 = sorted(rows_with_er, key=lambda r: r["er"], reverse=True)[:3]
    bottom_3 = sorted(rows_with_er, key=lambda r: r["er"])[:3]

    def post_summary(r):
        return {
            "date": r["date_dt"].strftime("%Y-%m-%d") if r["date_dt"] else None,
            "format": r.get("format"),
            "url": r.get("post_url"),
            "text_preview": (r.get("text") or "")[:150],
            "likes": r["likes_n"],
            "reposts": r["reposts_n"],
            "comments": r["comments_n"],
            "er": round(r["er"], 3) if r["er"] is not None else None,
            "rating_total": r.get("rating_total"),
            "cluster": r.get("theme_cluster"),
        }

    # Quality-Score-Aggregation, falls Bewertungs-Spalten vorhanden
    quality_stats = None
    rating_dims = ["rating_hook", "rating_substance", "rating_format_fit",
                   "rating_engagement_mechanic", "rating_performance_ratio", "rating_total"]
    if any(rows[0].get(dim) is not None for dim in rating_dims):
        quality_stats = {}
        for dim in rating_dims:
            scores = []
            for r in rows:
                val = r.get(dim)
                if val and str(val).strip() not in ("", "n/v", "n/a", "None"):
                    try:
                        scores.append(float(val))
                    except ValueError:
                        pass
            if scores:
                quality_stats[dim] = round(statistics.mean(scores), 2)

    return {
        "post_count": len(rows),
        "followers": followers,
        "date_range": date_range,
        "posts_per_week": posts_per_week,
        "engagement_rate": er_stats,
        "format_distribution": format_stats,
        "cluster_distribution": cluster_stats,
        "top_3_posts": [post_summary(r) for r in top_3],
        "bottom_3_posts": [post_summary(r) for r in bottom_3],
        "quality_stats": quality_stats,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("posts_csv", help="Pfad zur Posts-CSV")
    parser.add_argument("--followers", type=int, required=True,
                        help="Followerzahl des Accounts (für ER-Berechnung)")
    args = parser.parse_args()

    result = aggregate(args.posts_csv, args.followers)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
