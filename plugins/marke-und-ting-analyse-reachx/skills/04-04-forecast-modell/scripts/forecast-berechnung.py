#!/usr/bin/env python3
"""
forecast-berechnung.py — Phase-B-Berechner fuer den MTA-Skill `forecast-modell`.

Liest synthese/forecast-annahmen-schema.md (mit status: bestaetigt) und schreibt
- synthese/forecast.csv (flach, Kanal x Monat x Szenario x KPI)
- synthese/forecast.xlsx (3 Sheets: roh, pivot, annahmen)

Implementiert die Formeln aus reference/berechnungs-formeln.md.

Dependencies: pandas >= 2.0, openpyxl >= 3.1, python-dateutil >= 2.8, PyYAML >= 6.0.

Aufruf:
    python3 scripts/forecast-berechnung.py <projekt_pfad> [--datenstand 2026-05-14]

Beispiel:
    python3 scripts/forecast-berechnung.py /Users/x/mta-projekte/mta-mueller-2026-05/
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    sys.stderr.write("Fehler: PyYAML nicht installiert. Bitte `pip install pyyaml` ausfuehren.\n")
    sys.exit(2)

try:
    import pandas as pd
except ImportError:
    sys.stderr.write("Fehler: pandas nicht installiert. Bitte `pip install pandas` ausfuehren.\n")
    sys.exit(2)

try:
    import openpyxl  # noqa: F401  (used by pandas .to_excel)
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.stderr.write("Fehler: openpyxl nicht installiert. Bitte `pip install openpyxl` ausfuehren.\n")
    sys.exit(2)

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    sys.stderr.write("Fehler: python-dateutil nicht installiert. Bitte `pip install python-dateutil` ausfuehren.\n")
    sys.exit(2)


# =========================================================================
# Saisonalitaets-Defaults pro Branchen-Typ (siehe berechnungs-formeln.md)
# =========================================================================

SAISONALITAET_DEFAULTS: dict[str, dict[str, float]] = {
    "b2c_ecommerce":             {"jan": 0.85, "feb": 0.80, "mar": 0.95, "apr": 1.00, "mai": 1.05, "jun": 1.00, "jul": 0.90, "aug": 0.90, "sep": 1.05, "okt": 1.10, "nov": 1.30, "dez": 1.40},
    "b2c_lokal_dienstleister":   {"jan": 0.85, "feb": 0.95, "mar": 1.10, "apr": 1.15, "mai": 1.10, "jun": 0.95, "jul": 0.80, "aug": 0.80, "sep": 1.05, "okt": 1.10, "nov": 1.05, "dez": 0.85},
    "b2b_saas":                  {"jan": 1.10, "feb": 1.15, "mar": 1.10, "apr": 1.00, "mai": 0.95, "jun": 0.90, "jul": 0.80, "aug": 0.85, "sep": 1.05, "okt": 1.15, "nov": 1.20, "dez": 0.90},
    "b2b_industrie":             {"jan": 1.10, "feb": 1.15, "mar": 1.20, "apr": 1.10, "mai": 1.00, "jun": 0.85, "jul": 0.75, "aug": 0.85, "sep": 1.10, "okt": 1.15, "nov": 1.05, "dez": 0.80},
    "b2b_mittelstand_dienstleister": {"jan": 1.00, "feb": 1.05, "mar": 1.05, "apr": 1.00, "mai": 0.95, "jun": 0.95, "jul": 0.85, "aug": 0.90, "sep": 1.05, "okt": 1.10, "nov": 1.05, "dez": 0.95},
    "content_publisher":         {"jan": 1.10, "feb": 1.05, "mar": 1.05, "apr": 1.00, "mai": 0.95, "jun": 0.85, "jul": 0.75, "aug": 0.80, "sep": 1.15, "okt": 1.20, "nov": 1.10, "dez": 1.00},
    "marktplatz_plattform":      {"jan": 0.80, "feb": 0.85, "mar": 1.00, "apr": 1.00, "mai": 1.05, "jun": 1.00, "jul": 0.95, "aug": 0.95, "sep": 1.05, "okt": 1.10, "nov": 1.25, "dez": 1.40},
    "sonstige":                  {m: 1.0 for m in ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez"]},
}

MONAT_NAMEN_KURZ = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez"]

BRANCHEN_SPEND_OBERGRENZEN: dict[str, dict[str, float]] = {
    "b2c_ecommerce":             {"sea": 8000, "meta-ads": 6000, "linkedin-ads": 2000},
    "b2c_lokal_dienstleister":   {"sea": 3000, "meta-ads": 2000, "linkedin-ads": 1000},
    "b2b_saas":                  {"sea": 6000, "meta-ads": 4000, "linkedin-ads": 8000},
    "b2b_industrie":             {"sea": 5000, "meta-ads": 2500, "linkedin-ads": 7000},
    "b2b_mittelstand_dienstleister": {"sea": 4000, "meta-ads": 3000, "linkedin-ads": 5000},
    "content_publisher":         {"sea": 5000, "meta-ads": 6000, "linkedin-ads": 1500},
    "marktplatz_plattform":      {"sea": 10000, "meta-ads": 8000, "linkedin-ads": 3000},
    "sonstige":                  {"sea": 5000, "meta-ads": 4000, "linkedin-ads": 4000},
}

SZENARIEN = ["worst", "real", "best"]


# =========================================================================
# Ramp-up-Funktionen
# =========================================================================

def ramp_up_linear(m: int, T: int, start_anteil: float) -> float:
    if m >= T:
        return 1.0
    if T <= 1:
        return 1.0
    return min(start_anteil + (1.0 - start_anteil) * (m - 1) / (T - 1), 1.0)


def ramp_up_s_curve(m: int, T: int, start_anteil: float) -> float:
    if m >= T:
        return 1.0
    if T <= 1:
        return 1.0
    m0 = T / 2.0
    k = 4.0 / T
    raw = 1.0 / (1.0 + math.exp(-k * (m - m0)))
    raw1 = 1.0 / (1.0 + math.exp(-k * (1 - m0)))
    rawT = 1.0 / (1.0 + math.exp(-k * (T - m0)))
    if rawT - raw1 == 0:
        return start_anteil
    normalized = start_anteil + (1.0 - start_anteil) * (raw - raw1) / (rawT - raw1)
    return min(max(normalized, start_anteil), 1.0)


def ramp_up_sofort(m: int, T: int, start_anteil: float) -> float:
    if m == 1:
        return start_anteil
    if m >= T:
        return 1.0
    if T <= 1:
        return 1.0
    return start_anteil + (1.0 - start_anteil) * (m - 1) / (T - 1)


RAMP_UP_FUNKTIONEN = {
    "linear": ramp_up_linear,
    "s_curve": ramp_up_s_curve,
    "sofort": ramp_up_sofort,
}


# =========================================================================
# Schema-Parser
# =========================================================================

def parse_frontmatter(md_path: Path) -> dict[str, Any]:
    """Liest YAML-Frontmatter aus einer Markdown-Datei."""
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{md_path}: kein YAML-Frontmatter gefunden")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{md_path}: kein Frontmatter-Ende gefunden")
    fm_text = text[4:end]
    return yaml.safe_load(fm_text) or {}


@dataclass
class ForecastErgebnis:
    df_roh: pd.DataFrame
    df_annahmen: pd.DataFrame
    aggregat_jahr: dict[str, dict[str, float]]
    kanal_jahr_anteile: dict[str, float]
    top_kanal_slug: Optional[str]
    top_kanal_anteil_prozent: float
    steady_state_monat_real: int
    auffaelligkeiten_trigger: dict[str, list[dict[str, Any]]]
    monats_labels: list[str]


# =========================================================================
# Haupt-Berechnung
# =========================================================================

def baue_monats_labels(kickoff_datum: Optional[str]) -> list[str]:
    if kickoff_datum:
        try:
            kickoff = date.fromisoformat(kickoff_datum)
            return [(kickoff + relativedelta(months=i)).strftime("%Y-%m") for i in range(1, 13)]
        except ValueError:
            pass
    return [f"M{i}" for i in range(1, 13)]


def monat_index_zu_saison_key(monat_index: int, kickoff_datum: Optional[str]) -> str:
    """Mappt einen Forecast-Monat-Index (1..12) auf den Saison-Multiplikator-Key (jan..dez)."""
    if kickoff_datum:
        try:
            kickoff = date.fromisoformat(kickoff_datum)
            real_monat = (kickoff + relativedelta(months=monat_index)).month
            return MONAT_NAMEN_KURZ[real_monat - 1]
        except ValueError:
            pass
    # Fallback: Index direkt auf jan..dez
    return MONAT_NAMEN_KURZ[(monat_index - 1) % 12]


def rechne_forecast(schema: dict[str, Any], datenstand: str) -> ForecastErgebnis:
    branchen_typ = schema.get("branchen_typ", "sonstige")
    kickoff_datum = schema.get("kickoff_datum")
    monats_labels = baue_monats_labels(kickoff_datum)

    saison_block = schema.get("saisonalitaet", {})
    saison_global = saison_block.get("multiplikatoren") or SAISONALITAET_DEFAULTS.get(branchen_typ, SAISONALITAET_DEFAULTS["sonstige"])

    aov = schema.get("aov", {})
    aov_konf = aov.get("konfidenz", "mittel")
    aov_werte = {"worst": float(aov.get("worst", 0)), "real": float(aov.get("real", 0)), "best": float(aov.get("best", 0))}

    lead_funnel = schema.get("lead_funnel", {})
    lead_funnel_aktiv = bool(lead_funnel.get("aktiv", False))
    funnel_stufen = lead_funnel.get("stufen", []) if lead_funnel_aktiv else []

    doppelzaehlung_faktor = float(schema.get("doppelzaehlung_faktor", 0.85))

    kanaele = schema.get("kanaele", [])
    if not kanaele:
        raise ValueError("Schema enthaelt keine Kanaele")

    zeilen: list[dict[str, Any]] = []
    annahmen_zeilen: list[dict[str, Any]] = []

    # AOV in Annahmen-Sheet
    for s in SZENARIEN:
        annahmen_zeilen.append({
            "achse": "aov", "kanal_slug": "(alle)", "szenario": s,
            "wert": aov_werte[s], "einheit": aov.get("einheit", "EUR"),
            "quelle": aov.get("quelle", "schaetzung_skill"),
            "konfidenz": aov_konf,
        })

    # Saisonalitaet in Annahmen-Sheet
    for monat_key, multiplikator in saison_global.items():
        annahmen_zeilen.append({
            "achse": "saisonalitaet", "kanal_slug": "(alle)", "szenario": monat_key,
            "wert": float(multiplikator), "einheit": "multiplikator",
            "quelle": saison_block.get("quelle", "branchen_benchmark"),
            "konfidenz": saison_block.get("konfidenz", "mittel"),
        })

    # Doppelzaehlung in Annahmen-Sheet
    annahmen_zeilen.append({
        "achse": "doppelzaehlung_faktor", "kanal_slug": "(alle)", "szenario": "(alle)",
        "wert": doppelzaehlung_faktor, "einheit": "faktor",
        "quelle": schema.get("doppelzaehlung_quelle", "aggregat_default"),
        "konfidenz": "mittel",
    })

    for kanal in kanaele:
        kanal_slug = kanal["kanal_slug"]
        kanal_anzeige = kanal.get("kanal_anzeigename", kanal_slug)
        kanal_typ = kanal.get("kanal_typ", "organisch")

        if kanal_typ == "hebel":
            # Website-CRO ist kein eigener Kanal - wird in einer Erweiterung als CR-Uplift modelliert
            continue

        volumen = kanal.get("volumen_basis_monat", {})
        volumen_werte = {s: float(volumen.get(s, 0)) for s in SZENARIEN}
        volumen_konf = volumen.get("konfidenz", "mittel")
        volumen_quelle = volumen.get("quelle", "schaetzung_skill")

        klick_anteil_block = kanal.get("klick_anteil", {})
        klick_werte = {s: float(klick_anteil_block.get(s, 1.0)) for s in SZENARIEN}

        cr_block = kanal.get("cr_bandbreite", {})
        cr_werte = {s: float(cr_block.get(s, 0)) for s in SZENARIEN}
        cr_konf = cr_block.get("konfidenz", "mittel")
        cr_quelle = cr_block.get("quelle", "branchen_benchmark")

        ramp_up = kanal.get("ramp_up", {})
        ramp_funktion = ramp_up.get("funktion", "linear")
        if ramp_funktion not in RAMP_UP_FUNKTIONEN:
            raise ValueError(f"Kanal {kanal_slug}: unbekannte ramp_up.funktion '{ramp_funktion}'")
        ramp_fn = RAMP_UP_FUNKTIONEN[ramp_funktion]
        ramp_T = {
            "worst": int(ramp_up.get("monate_bis_steady_state_max", 12)),
            "real":  int(ramp_up.get("monate_bis_steady_state_real", 6)),
            "best":  int(ramp_up.get("monate_bis_steady_state_min", 3)),
        }
        ramp_start = float(ramp_up.get("start_anteil", 0.1))

        spend = kanal.get("spend_monat", {})
        spend_werte = {s: float(spend.get(s, 0)) for s in SZENARIEN}
        spend_quelle = spend.get("quelle", "branchen_benchmark")
        spend_aligned = bool(spend.get("ramp_up_aligned", False))

        # Kanal-spezifische Saisonalitaet
        saison_override = kanal.get("saisonalitaet_override")
        saison_fuer_kanal = saison_override or saison_global

        # Annahmen-Sheet pro Kanal
        for s in SZENARIEN:
            annahmen_zeilen.append({"achse": "volumen_basis", "kanal_slug": kanal_slug, "szenario": s,
                                    "wert": volumen_werte[s], "einheit": volumen.get("einheit", "suchanfragen"),
                                    "quelle": volumen_quelle, "konfidenz": volumen_konf})
            annahmen_zeilen.append({"achse": "klick_anteil", "kanal_slug": kanal_slug, "szenario": s,
                                    "wert": klick_werte[s], "einheit": "anteil",
                                    "quelle": "branchen_benchmark", "konfidenz": "mittel"})
            annahmen_zeilen.append({"achse": "cr", "kanal_slug": kanal_slug, "szenario": s,
                                    "wert": cr_werte[s], "einheit": "anteil",
                                    "quelle": cr_quelle, "konfidenz": cr_konf})
            annahmen_zeilen.append({"achse": "spend_monat", "kanal_slug": kanal_slug, "szenario": s,
                                    "wert": spend_werte[s], "einheit": "EUR",
                                    "quelle": spend_quelle, "konfidenz": spend.get("konfidenz", "mittel")})
        annahmen_zeilen.append({"achse": "ramp_up_funktion", "kanal_slug": kanal_slug, "szenario": "(alle)",
                                "wert": ramp_funktion, "einheit": "typ",
                                "quelle": ramp_up.get("quelle", "branchen_benchmark"), "konfidenz": "mittel"})
        annahmen_zeilen.append({"achse": "ramp_up_monate_real", "kanal_slug": kanal_slug, "szenario": "real",
                                "wert": ramp_T["real"], "einheit": "monate",
                                "quelle": ramp_up.get("quelle", "branchen_benchmark"), "konfidenz": "mittel"})

        # Pro Szenario und Monat die Forecast-Zeilen
        for monat_index in range(1, 13):
            saison_key = monat_index_zu_saison_key(monat_index, kickoff_datum)
            saison_mult = float(saison_fuer_kanal.get(saison_key, 1.0))
            for s in SZENARIEN:
                ramp_faktor = ramp_fn(monat_index, ramp_T[s], ramp_start)
                sessions = volumen_werte[s] * ramp_faktor * saison_mult * klick_werte[s]
                leads = sessions * cr_werte[s]
                if lead_funnel_aktiv and funnel_stufen:
                    qualifiziert = leads
                    for stufe in funnel_stufen:
                        cr_stufe_key = f"cr_{s}"
                        cr_stufe = float(stufe.get(cr_stufe_key, stufe.get("cr_real", 0.5)))
                        qualifiziert = qualifiziert * cr_stufe
                    orders = qualifiziert
                    # qualifizierte_leads = Stufe nach erster Funnel-Stufe
                    cr_stufe1 = float(funnel_stufen[0].get(f"cr_{s}", funnel_stufen[0].get("cr_real", 0.5)))
                    qualifizierte_leads = leads * cr_stufe1
                else:
                    qualifizierte_leads = None
                    orders = leads
                umsatz = orders * aov_werte[s]
                spend_dieser_monat = spend_werte[s] * (ramp_faktor if spend_aligned else 1.0)

                cr_effektiv = (orders / sessions) if sessions > 0 else 0.0

                zeilen.append({
                    "kanal_slug": kanal_slug,
                    "kanal_anzeigename": kanal_anzeige,
                    "monat_index": monat_index,
                    "monat_label": monats_labels[monat_index - 1],
                    "szenario": s,
                    "sessions": round(sessions, 2),
                    "leads": round(leads, 2),
                    "qualifizierte_leads": round(qualifizierte_leads, 2) if qualifizierte_leads is not None else None,
                    "orders": round(orders, 2),
                    "umsatz_eur": round(umsatz, 2),
                    "spend_eur": round(spend_dieser_monat, 2),
                    "cr_angewandt": round(cr_effektiv, 5),
                    "aov_angewandt": aov_werte[s],
                    "ramp_up_faktor": round(ramp_faktor, 4),
                    "saisonalitaet_multiplikator": saison_mult,
                    "quelle_volumen": volumen_quelle,
                    "quelle_cr": cr_quelle,
                    "quelle_aov": aov.get("quelle", "schaetzung_skill"),
                    "quelle_spend": spend_quelle,
                    "quelle_ziel_overlay": "abgeleitete_ziele",
                    "konfidenz": _aggr_konfidenz(volumen_konf, cr_konf, aov_konf),
                    "zugehoerige_auffaelligkeiten": "",
                    "datenstand_iso": datenstand,
                })

    df_roh = pd.DataFrame(zeilen)

    # Aggregat-Zeilen ueber alle Kanaele pro Monat x Szenario, mit Doppelzaehlungs-Korrektur
    agg_rows = []
    for monat_index in range(1, 13):
        for s in SZENARIEN:
            subset = df_roh[(df_roh["monat_index"] == monat_index) & (df_roh["szenario"] == s)]
            sessions = subset["sessions"].sum()
            leads_korr = subset["leads"].sum() * doppelzaehlung_faktor
            ql = subset["qualifizierte_leads"].sum() * doppelzaehlung_faktor if subset["qualifizierte_leads"].notna().any() else None
            orders_korr = subset["orders"].sum() * doppelzaehlung_faktor
            umsatz_korr = subset["umsatz_eur"].sum() * doppelzaehlung_faktor
            spend_summe = subset["spend_eur"].sum()  # NICHT doppelt zaehlen
            agg_rows.append({
                "kanal_slug": "aggregat",
                "kanal_anzeigename": "Aggregat",
                "monat_index": monat_index,
                "monat_label": monats_labels[monat_index - 1],
                "szenario": s,
                "sessions": round(sessions, 2),
                "leads": round(leads_korr, 2),
                "qualifizierte_leads": round(ql, 2) if ql is not None else None,
                "orders": round(orders_korr, 2),
                "umsatz_eur": round(umsatz_korr, 2),
                "spend_eur": round(spend_summe, 2),
                "cr_angewandt": None, "aov_angewandt": None,
                "ramp_up_faktor": None, "saisonalitaet_multiplikator": None,
                "quelle_volumen": "aggregat", "quelle_cr": "aggregat",
                "quelle_aov": "aggregat", "quelle_spend": "aggregat",
                "quelle_ziel_overlay": "aggregat",
                "konfidenz": "mittel", "zugehoerige_auffaelligkeiten": "",
                "datenstand_iso": datenstand,
            })

    df_roh = pd.concat([df_roh, pd.DataFrame(agg_rows)], ignore_index=True)
    df_annahmen = pd.DataFrame(annahmen_zeilen)

    # Aggregat Jahr pro Szenario
    aggregat_jahr: dict[str, dict[str, float]] = {}
    for s in SZENARIEN:
        agg = df_roh[(df_roh["kanal_slug"] == "aggregat") & (df_roh["szenario"] == s)]
        aggregat_jahr[s] = {
            "umsatz_eur": float(agg["umsatz_eur"].sum()),
            "leads": float(agg["leads"].sum()),
            "orders": float(agg["orders"].sum()),
            "spend_eur": float(agg["spend_eur"].sum()),
        }

    # Kanal-Anteile am Real-Szenario
    kanal_jahr_anteile: dict[str, float] = {}
    real_aggregat_umsatz = aggregat_jahr["real"]["umsatz_eur"]
    if real_aggregat_umsatz > 0:
        for kanal in kanaele:
            slug = kanal["kanal_slug"]
            kanal_real_umsatz = df_roh[(df_roh["kanal_slug"] == slug) & (df_roh["szenario"] == "real")]["umsatz_eur"].sum()
            # Anteil VOR Doppelzaehlung -- nutzen Roh-Summe (alle Kanal-Zeilen, kein aggregat) als Bezugsgroesse
            kanal_jahr_anteile[slug] = float(kanal_real_umsatz) / float(real_aggregat_umsatz / max(0.001, _doppelzaehlung_korrekturwert(doppelzaehlung_faktor)))

    if kanal_jahr_anteile:
        top_slug = max(kanal_jahr_anteile, key=kanal_jahr_anteile.get)
        top_anteil = kanal_jahr_anteile[top_slug]
    else:
        top_slug = None
        top_anteil = 0.0

    # Steady-State-Monat: erster Monat im Real, in dem >= 90% des Dezember-Aggregats erreicht ist
    steady_state_monat_real = 12
    real_zeilen = df_roh[(df_roh["kanal_slug"] == "aggregat") & (df_roh["szenario"] == "real")].sort_values("monat_index")
    if not real_zeilen.empty:
        max_monat_umsatz = real_zeilen["umsatz_eur"].max()
        for _, row in real_zeilen.iterrows():
            if row["umsatz_eur"] >= 0.9 * max_monat_umsatz:
                steady_state_monat_real = int(row["monat_index"])
                break

    # Auffaelligkeits-Trigger berechnen
    trigger = schema.get("auffaelligkeits_trigger", {})
    auff_results = _berechne_auffaelligkeiten(
        schema=schema,
        df_roh=df_roh,
        aggregat_jahr=aggregat_jahr,
        kanal_jahr_anteile=kanal_jahr_anteile,
        trigger_thresholds=trigger,
        branchen_typ=branchen_typ,
        saison_global=saison_global,
    )

    return ForecastErgebnis(
        df_roh=df_roh,
        df_annahmen=df_annahmen,
        aggregat_jahr=aggregat_jahr,
        kanal_jahr_anteile=kanal_jahr_anteile,
        top_kanal_slug=top_slug,
        top_kanal_anteil_prozent=round(top_anteil * 100, 2),
        steady_state_monat_real=steady_state_monat_real,
        auffaelligkeiten_trigger=auff_results,
        monats_labels=monats_labels,
    )


def _doppelzaehlung_korrekturwert(faktor: float) -> float:
    # Hilfsfunktion: wenn doppelzaehlung_faktor 0.85 ist, dann ist die Bezugsgroesse fuer Anteile die Roh-Summe
    return faktor


def _aggr_konfidenz(v_konf: str, c_konf: str, a_konf: str) -> str:
    werte = {"hoch": 3, "mittel": 2, "niedrig": 1}
    summe = werte.get(v_konf, 2) + werte.get(c_konf, 2) + werte.get(a_konf, 2)
    if summe >= 8:
        return "hoch"
    if summe >= 5:
        return "mittel"
    return "niedrig"


def _berechne_auffaelligkeiten(
    schema: dict[str, Any],
    df_roh: pd.DataFrame,
    aggregat_jahr: dict[str, dict[str, float]],
    kanal_jahr_anteile: dict[str, float],
    trigger_thresholds: dict[str, Any],
    branchen_typ: str,
    saison_global: dict[str, float],
) -> dict[str, list[dict[str, Any]]]:
    """Berechnet welche Auffaelligkeits-Trigger angeschlagen sind. Gibt Listen mit Details zurueck."""
    out: dict[str, list[dict[str, Any]]] = {
        "ziele_briefing_vs_abgeleitet_diskrepanz": [],
        "kanal_dominanz_im_forecast": [],
        "ramp_up_engpass": [],
        "worst_case_nicht_break_even": [],
        "saisonalitaet_kollidiert_kampagnen_start": [],
        "spend_zu_hoch_fuer_geforderte_ziele": [],
        "briefing_kpi_passt": [],
        "konfidenz_niedrig_basis": [],
    }

    # ziele_briefing_vs_abgeleitet_diskrepanz
    diskrepanz_schwelle = float(trigger_thresholds.get("ziele_briefing_vs_abgeleitet_diskrepanz_prozent", 30)) / 100.0
    ziel_inventur = schema.get("ziel_inventur", {})
    for ziel in ziel_inventur.get("ziel_quellen", []):
        briefing_wert = ziel.get("briefing_wert")
        real_wert = ziel.get("abgeleitet_real")
        if briefing_wert is None or real_wert is None or real_wert == 0:
            continue
        abweichung = abs(briefing_wert - real_wert) / real_wert
        if abweichung > diskrepanz_schwelle:
            out["ziele_briefing_vs_abgeleitet_diskrepanz"].append({
                "kpi": ziel.get("kpi"),
                "briefing": briefing_wert,
                "abgeleitet_real": real_wert,
                "abweichung_prozent": round(abweichung * 100, 1),
            })
        else:
            out["briefing_kpi_passt"].append({"kpi": ziel.get("kpi"), "briefing": briefing_wert})

    # kanal_dominanz_im_forecast
    dom_schwelle = float(trigger_thresholds.get("kanal_dominanz_im_forecast_prozent", 60)) / 100.0
    for slug, anteil in kanal_jahr_anteile.items():
        if anteil > dom_schwelle:
            out["kanal_dominanz_im_forecast"].append({"kanal_slug": slug, "anteil_prozent": round(anteil * 100, 1)})

    # ramp_up_engpass
    briefing_timeline = trigger_thresholds.get("ramp_up_engpass_briefing_timeline_monate")
    if briefing_timeline:
        agg_real = df_roh[(df_roh["kanal_slug"] == "aggregat") & (df_roh["szenario"] == "real")].sort_values("monat_index")
        if not agg_real.empty:
            max_umsatz = agg_real["umsatz_eur"].max()
            ergebnis_monat = None
            for _, row in agg_real.iterrows():
                if row["umsatz_eur"] >= 0.5 * max_umsatz:
                    ergebnis_monat = int(row["monat_index"])
                    break
            if ergebnis_monat and ergebnis_monat > int(briefing_timeline):
                out["ramp_up_engpass"].append({
                    "briefing_erwartet_monat": int(briefing_timeline),
                    "ergebnis_real_ab_monat": ergebnis_monat,
                })

    # worst_case_nicht_break_even
    retainer_default = 60000
    jahres_umsatz_best = aggregat_jahr["best"]["umsatz_eur"]
    jahres_spend_real = aggregat_jahr["real"]["spend_eur"]
    break_even = jahres_spend_real + retainer_default
    if jahres_umsatz_best < break_even:
        out["worst_case_nicht_break_even"].append({
            "jahres_umsatz_best": jahres_umsatz_best,
            "break_even_schwelle": break_even,
        })

    # saisonalitaet_kollidiert_kampagnen_start
    schwelle = float(trigger_thresholds.get("saisonalitaet_kollision_multiplikator_schwelle", 0.85))
    start_saison_key = monat_index_zu_saison_key(1, schema.get("kickoff_datum"))
    start_mult = float(saison_global.get(start_saison_key, 1.0))
    if start_mult < schwelle:
        out["saisonalitaet_kollidiert_kampagnen_start"].append({
            "start_monat_key": start_saison_key,
            "multiplikator": start_mult,
        })

    # spend_zu_hoch_fuer_geforderte_ziele
    obergrenzen = BRANCHEN_SPEND_OBERGRENZEN.get(branchen_typ, BRANCHEN_SPEND_OBERGRENZEN["sonstige"])
    faktor = float(trigger_thresholds.get("spend_zu_hoch_faktor", 1.5))
    for kanal in schema.get("kanaele", []):
        if kanal.get("kanal_typ") != "paid":
            continue
        slug = kanal["kanal_slug"]
        spend_real = float(kanal.get("spend_monat", {}).get("real", 0))
        obergrenze = float(obergrenzen.get(slug, 5000))
        if spend_real > faktor * obergrenze:
            out["spend_zu_hoch_fuer_geforderte_ziele"].append({
                "kanal_slug": slug, "spend_real": spend_real, "branchen_obergrenze": obergrenze,
            })

    # konfidenz_niedrig_basis
    konf_inv = schema.get("konfidenz_inventur", {})
    branchen_anteil = float(konf_inv.get("branchen_benchmark_anteil_prozent", 0))
    if branchen_anteil > 50:
        out["konfidenz_niedrig_basis"].append({
            "branchen_benchmark_anteil_prozent": branchen_anteil,
        })

    return out


# =========================================================================
# Excel-Export
# =========================================================================

def schreibe_excel(xlsx_path: Path, df_roh: pd.DataFrame, df_annahmen: pd.DataFrame) -> None:
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_roh.to_excel(writer, sheet_name="roh", index=False)

        # Pivot ueber Kanal x Monat x Szenario
        pivot = pd.pivot_table(
            df_roh[df_roh["kanal_slug"] != "aggregat"],
            index=["kanal_slug", "kanal_anzeigename"],
            columns=["szenario", "monat_index"],
            values=["umsatz_eur", "leads", "orders", "spend_eur"],
            aggfunc="sum",
            fill_value=0,
        )
        pivot.to_excel(writer, sheet_name="pivot")

        df_annahmen.to_excel(writer, sheet_name="annahmen", index=False)

    # Header bold und Spaltenbreite einfach
    wb = openpyxl.load_workbook(xlsx_path)
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for col_idx, column in enumerate(ws.columns, start=1):
            max_len = 0
            for cell in column:
                try:
                    val = str(cell.value) if cell.value is not None else ""
                    if len(val) > max_len:
                        max_len = len(val)
                except Exception:
                    pass
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 2, 8), 40)
    wb.save(xlsx_path)


# =========================================================================
# CLI
# =========================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Forecast-Berechnung fuer MTA-Skill forecast-modell")
    parser.add_argument("projekt_pfad", type=str, help="Absoluter Pfad zum MTA-Projektordner")
    parser.add_argument("--datenstand", type=str, default=date.today().isoformat(), help="ISO-Datum des Skill-Laufs")
    parser.add_argument("--json-result", action="store_true", help="JSON-Zusammenfassung auf stdout ausgeben")
    args = parser.parse_args()

    projekt = Path(args.projekt_pfad)
    if not projekt.exists():
        sys.stderr.write(f"Projekt-Pfad existiert nicht: {projekt}\n")
        return 1

    schema_path = projekt / "synthese" / "forecast-annahmen-schema.md"
    if not schema_path.exists():
        sys.stderr.write(f"Schema-Datei nicht gefunden: {schema_path}\n")
        return 1

    schema = parse_frontmatter(schema_path)
    if schema.get("status") != "bestaetigt":
        sys.stderr.write(f"Schema-Status ist '{schema.get('status')}' - Phase B erfordert 'bestaetigt'\n")
        return 1

    try:
        ergebnis = rechne_forecast(schema, args.datenstand)
    except Exception as e:
        sys.stderr.write(f"Berechnung fehlgeschlagen: {e}\n")
        return 2

    # CSV schreiben
    csv_path = projekt / "synthese" / "forecast.csv"
    ergebnis.df_roh.to_csv(csv_path, index=False, encoding="utf-8")

    # Excel schreiben
    xlsx_path = projekt / "synthese" / "forecast.xlsx"
    schreibe_excel(xlsx_path, ergebnis.df_roh, ergebnis.df_annahmen)

    result = {
        "ok": True,
        "csv_pfad": str(csv_path.relative_to(projekt)),
        "xlsx_pfad": str(xlsx_path.relative_to(projekt)),
        "aggregat_jahr": ergebnis.aggregat_jahr,
        "top_kanal_slug": ergebnis.top_kanal_slug,
        "top_kanal_anteil_prozent": ergebnis.top_kanal_anteil_prozent,
        "steady_state_monat_real": ergebnis.steady_state_monat_real,
        "kanal_jahr_anteile": ergebnis.kanal_jahr_anteile,
        "monats_labels": ergebnis.monats_labels,
        "auffaelligkeiten_trigger": ergebnis.auffaelligkeiten_trigger,
        "datenstand_iso": args.datenstand,
    }

    if args.json_result:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"OK: Forecast geschrieben nach {csv_path.name} und {xlsx_path.name}")
        print(f"   Aggregat Real Umsatz: {ergebnis.aggregat_jahr['real']['umsatz_eur']:.0f} EUR/Jahr")
        print(f"   Top-Kanal: {ergebnis.top_kanal_slug} ({ergebnis.top_kanal_anteil_prozent}%)")
        print(f"   Steady-State (Real): Monat {ergebnis.steady_state_monat_real}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
