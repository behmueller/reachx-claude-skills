# REACHX-Stundensaetze (zentral, agentur-weit)

**Versionierung:** Dieses Dokument ist die zentrale Stundensatz-Basis fuer **alle** MTA-Retainer-Kalkulationen bei REACHX. Es liegt zentral im Skill-`reference/`-Ordner — NICHT projektspezifisch. Bei Stundensatz-Aenderungen wird dieses Dokument aktualisiert (Versions-Inkrement im Frontmatter, Eintrag im Aenderungs-Log unten), und der Skill wird neu paketiert. Laufende MTA-Projekte rechnen mit der Stundensatz-Version, die zum Zeitpunkt der Kalkulation aktuell war.

```yaml
schema_version: "1.0"
version: "2026.05"
stand: 2026-05-14
zustaendig: REACHX Geschaeftsfuehrung
naechste_review: 2027-01-15
```

---

## 1. Rollen-Stundensaetze 2026 (Default)

Stundensaetze in **EUR netto pro Stunde**. Jede Rolle hat einen Default-Wert (Mittelwert) und eine Bandbreite. Die Bandbreite wird im Output verwendet, wenn der Kunde-Komplexitaet-Hinweis oben oder unten am Rand der Skala liegt.

| Rolle | Default | Bandbreite (min-max) | Beschreibung |
|---|---|---|---|
| `STRATEGIE_LEAD` | 195 | 175-220 | Hands-on-CMO-Vertretung, Strategie-Workshops, Quartals-Reviews, Eskalations-Calls |
| `STRATEGIE_MANAGER` | 165 | 145-185 | Strategie-Erarbeitung, Roadmap-Anpassung, Reporting-Lead, Steuerung der Kanal-Teams |
| `SEO_MANAGER` | 145 | 130-165 | SEO-Strategie, Keyword-Recherche, Content-Briefings, Site-Audits, Technische SEO |
| `SEA_MANAGER` | 145 | 130-165 | Google-Ads, Meta-Ads, LinkedIn-Ads Kampagnen-Management, Bid-Strategien, Conversion-Tracking |
| `CONTENT_MANAGER` | 125 | 110-140 | Redaktion, Briefing-Uebernahme, On-Page-Optimierung, Newsletter-Texte |
| `SOCIAL_MEDIA_MANAGER` | 115 | 100-130 | Social-Redaktionsplan, Community-Management, Reels/Shorts-Konzepte |
| `DESIGNER` | 125 | 110-145 | Banner-Designs, Landingpage-Layouts, Social-Visuals, Pitch-Decks |
| `DEVELOPER` | 145 | 130-165 | Tracking-Setup, GTM/GA4, Site-Speed-Optimierung, Schema-Markup, kleine Frontend-Tasks |
| `JUNIOR_HANDS` | 95 | 85-110 | Operative Umsetzung, Asset-Produktion, Daten-Pflege, GMB-Pflege, Listings |

**Pflicht-Bandbreite:** Im Output wird IMMER eine Preis-Bandbreite ausgewiesen. Die Bandbreite kommt primaer aus der **Stunden-Bandbreite** (siehe `aufwands-bandbreiten.md`), sekundaer ueber die **Rollen-Bandbreite** oben. Der Default-Wert wird fuer die Realistisch-Szenario-Berechnung verwendet.

---

## 2. Rabatte und Overrides

| Konstante | Default | Beschreibung |
|---|---|---|
| `REACHX_NEUKUNDEN_RABATT_PROZENT` | 10 | Rabatt fuer die ersten 6 Monate, wenn im Phase-A-Schema markiert |
| `REACHX_MENGEN_RABATT_PROZENT` | 8 | Rabatt fuer Retainer > 80 Stunden/Monat |
| `REACHX_NPO_RABATT_PROZENT` | 15 | Rabatt fuer Non-Profit-Organisationen, eingetragene Vereine, Stiftungen |
| `REACHX_LANGZEIT_RABATT_PROZENT` | 5 | Rabatt fuer Vertragslaufzeit 24 Monate |

Rabatte sind **nicht** automatisch — der Stratege markiert in Phase A im Feld `stundensatz_override`, welche Rabatte angewendet werden. Im Output wird der Rabatt **transparent ausgewiesen** (Originalpreis durchgestrichen, Rabattpreis daneben).

---

## 3. Spezialitaeten

- **Workshop-Tage** (Strategie-Workshop, Kick-off, Quartals-Review): Werden in Tagen abgerechnet, nicht in Stunden. Tagessatz = `STRATEGIE_LEAD` x 8. Bandbreite via Vorbereitung (Halb-Tag vs. Ganz-Tag plus Nachbereitung).
- **Reporting-Stunden**: Werden mit `STRATEGIE_MANAGER`-Satz angesetzt (Reporting ist Strategie-Naehe, nicht Operatives).
- **Ad-hoc-Calls / Eskalation**: Mit `STRATEGIE_LEAD`-Satz, in 15-Minuten-Schritten erfasst, monatlich abgerechnet.
- **Asset-Produktion (Bilder, kurze Videos)**: Mit `DESIGNER`-Satz; aufwendige Video-Produktion ist nicht Teil des Standard-Retainers, sondern separater Werkvertrag.

---

## 4. Anwendung im Skill

Im `04-06-retainer-kalkulator` werden die Konstanten oben als Slugs referenziert (z. B. `SEO_MANAGER`, `STRATEGIE_LEAD`). Pro Massnahme aus `aufwands-bandbreiten.md` ist eine Rolle hinterlegt. Pro Massnahme x Rolle x Stunden ergibt sich der Preis.

**Niemals hardcoded im Skill-Code** — alle Saetze kommen ueber Lookup aus diesem Dokument.

---

## 5. Aenderungs-Log

| Datum | Version | Aenderung | Verantwortlich |
|---|---|---|---|
| 2026-05-14 | 2026.05 | Initiale Erstellung zentrales Stundensatz-Dokument, 9 Rollen, 4 Rabatt-Konstanten | Sascha Behmueller |

Bei der naechsten Aenderung: neuen Eintrag mit Begruendung und Versionssprung.
