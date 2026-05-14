# {{COMPANY_NAME}} – LinkedIn Wettbewerbs-Analyse

**Erstellt:** {{ANALYSIS_DATE}}  
**Quelle:** {{LINKEDIN_URL}}  
**Backend:** {{BACKEND_NAME}}  

---

## Executive Summary

{{EXEC_SUMMARY_3_TO_5_BULLETS}}

**Kanal-Eignungs-Indikatoren auf einen Blick:**
- Posting-Frequenz: {{POSTS_PER_WEEK}} Posts/Woche (Company)
- Durchschnittliche Engagement-Rate (Company): {{AVG_ER_COMPANY}}%
- Durchschnittliche Engagement-Rate (Mitarbeiter): {{AVG_ER_PEOPLE}}%
- Branchen-Benchmark ER (für Kontext): {{INDUSTRY_BENCHMARK_ER}}%

---

## Datenqualität & Coverage

| Datenpunkt | Erfolgreich | Anteil | Hinweis |
|---|---|---|---|
| Company Page | {{COMPANY_OK}} / 1 | {{COMPANY_PCT}}% | |
| Mitarbeiter-Listing | {{EMP_LIST_COUNT}} | – | LinkedIn zeigt nicht alle |
| Deep-Profile-Scrape | {{DEEP_OK}} / {{DEEP_TOTAL}} | {{DEEP_PCT}}% | |
| Tenure-Daten verfügbar | {{TENURE_OK}} / {{DEEP_TOTAL}} | {{TENURE_PCT}}% | |
| Company-Posts | {{COMPANY_POSTS_COUNT}} | – | Zeitraum: {{COMPANY_POSTS_RANGE}} |
| Personen-Posts | {{PEOPLE_POSTS_COUNT}} | – | Zeitraum: {{PEOPLE_POSTS_RANGE}} |

**Disclaimer:** Cookie-frei zugängliche LinkedIn-Daten sind eingeschränkt. Insbesondere die Posts-Historie umfasst typischerweise nur die letzten 4–8 Wochen, nicht 12 Monate. Engagement-Zahlen können bei sehr hohen Werten von LinkedIn gerundet sein.

---

## 1. Company-Profil-Snapshot

| | |
|---|---|
| Name | {{COMPANY_NAME}} |
| Branche | {{INDUSTRY}} |
| Größe (LinkedIn) | {{COMPANY_SIZE}} |
| Hauptsitz | {{HEADQUARTERS}} |
| Gegründet | {{FOUNDED}} |
| Follower | **{{FOLLOWER_COUNT}}** |
| Mitarbeiter (LinkedIn-Schätzung) | {{EMPLOYEES_COUNT}} |
| Website | {{WEBSITE}} |

**Kurz-Beschreibung:**  
{{COMPANY_DESCRIPTION_2_3_SENTENCES}}

---

## 2. Mitarbeiter-Struktur

### Department-Verteilung

| Department | Anzahl | Anteil |
|---|---|---|
{{DEPARTMENT_TABLE}}

**Beobachtung:** {{DEPARTMENT_OBSERVATION_1_2_SENTENCES}}

### Tenure-Verteilung *(falls Daten verfügbar)*

| Tenure-Bucket | Anzahl | Anteil |
|---|---|---|
| < 1 Jahr | {{T1}} | {{T1_PCT}}% |
| 1–3 Jahre | {{T2}} | {{T2_PCT}}% |
| 3–5 Jahre | {{T3}} | {{T3_PCT}}% |
| 5–10 Jahre | {{T4}} | {{T4_PCT}}% |
| > 10 Jahre | {{T5}} | {{T5_PCT}}% |

- **Median-Tenure**: {{MEDIAN_TENURE}} Jahre
- **Mittelwert-Tenure**: {{MEAN_TENURE}} Jahre

**Beobachtung:** {{TENURE_OBSERVATION_1_2_SENTENCES}}

---

## 3. Content-Analyse

### Posting-Frequenz

| Kanal | Posts in Zeitraum | Pro Woche |
|---|---|---|
| Company Page | {{COMPANY_POSTS_COUNT}} | {{COMPANY_PPW}} |
| Mitarbeiter (Sample) | {{PEOPLE_POSTS_COUNT}} | {{PEOPLE_PPW}} |

### Format-Verteilung (Company)

| Format | Anzahl | Anteil | Ø ER pro Format |
|---|---|---|---|
{{FORMAT_TABLE_COMPANY}}

### Themen-Cluster (Company)

| Cluster | Anzahl Posts | Ø ER |
|---|---|---|
{{CLUSTER_TABLE_COMPANY}}

**Beobachtung Content-Strategie:**  
{{CONTENT_OBSERVATION_2_3_SENTENCES}}

---

## 4. Post-Performance

### Engagement-Übersicht

| Metrik | Company | Mitarbeiter (Ø) |
|---|---|---|
| Ø Likes/Post | {{AVG_LIKES_C}} | {{AVG_LIKES_P}} |
| Ø Reposts/Post | {{AVG_REPOSTS_C}} | {{AVG_REPOSTS_P}} |
| Ø Kommentare/Post | {{AVG_COMMENTS_C}} | {{AVG_COMMENTS_P}} |
| **Ø Engagement-Rate** | **{{AVG_ER_C}}%** | **{{AVG_ER_P}}%** |

### Top 3 Posts (nach Engagement-Rate)

{{TOP_3_POSTS_DETAIL}}

### Bottom 3 Posts (nach Engagement-Rate)

{{BOTTOM_3_POSTS_DETAIL}}

### Post-Qualität (gemäß Rating-Framework)

| Dimension | Ø Score Company | Ø Score Mitarbeiter |
|---|---|---|
| Hook-Qualität | {{HOOK_C}} | {{HOOK_P}} |
| Inhaltlicher Mehrwert | {{SUBSTANCE_C}} | {{SUBSTANCE_P}} |
| Format-Fit | {{FORMAT_FIT_C}} | {{FORMAT_FIT_P}} |
| Engagement-Mechanik | {{MECHANIC_C}} | {{MECHANIC_P}} |
| Performance-Ratio | {{PERF_C}} | {{PERF_P}} |
| **Gesamt** | **{{TOTAL_C}}** | **{{TOTAL_P}}** |

**Patterns Top-Performer:** {{TOP_PATTERN_OBSERVATION}}  
**Patterns Underperformer:** {{BOTTOM_PATTERN_OBSERVATION}}

---

## 5. Strategische Implikationen

*(Diese Sektion ist die wichtigste für Marketing-Entscheidungen. Schreibe konkret und entscheidungs-orientiert.)*

### Was das für die Kanal-Eignung LinkedIn organic bedeutet

{{IMPLICATION_CHANNEL_FIT_3_5_SENTENCES}}

### Was wir vom Wettbewerber lernen können

{{LEARNINGS_3_BULLETS}}

### Was wir besser machen können

{{OPPORTUNITIES_3_BULLETS}}

### Risiken / Caveats

{{RISKS_OR_CAVEATS_2_3_BULLETS}}

---

## Anhang: Daten-Files

- `company.json` – Roh-Daten Company Page
- `employees_listing.csv` – Mitarbeiter-Übersicht ({{EMP_LIST_COUNT}} Einträge)
- `employees_deep.csv` – Tiefgescrapte Profile ({{DEEP_OK}} Einträge)
- `company_posts.csv` – Company-Posts mit Bewertung ({{COMPANY_POSTS_COUNT}} Einträge)
- `people_posts.csv` – Personen-Posts mit Bewertung ({{PEOPLE_POSTS_COUNT}} Einträge)
