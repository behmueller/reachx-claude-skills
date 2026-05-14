# Sampling-Strategie und Department-Klassifizierung

Wenn ein Unternehmen 100, 500 oder 2.000 Mitarbeiter auf LinkedIn hat, kannst (und solltest) du nicht alle Profile deep-scrapen. Dieser Guide regelt:

1. Wie wir Mitarbeiter in Departments klassifizieren (fuer Aggregat-Statistik)
2. Wie wir die ca. 10 Profile fuers Deep-Scrape auswaehlen (Smart Sampling)

---

## Department-Klassifizierung

Klassifiziere jeden Mitarbeiter aus dem Listing in genau **ein** Department. Basis: `headline` plus `current_position`. Bei Mehrdeutigkeit -> "Other".

### Standard-Buckets mit Trigger-Woertern

| Department | Trigger im Headline/Position (DE/EN, Auswahl) |
|---|---|
| **Leadership / C-Level** | CEO, CTO, CMO, CFO, COO, CIO, Geschaeftsfuehr, Founder, Co-Founder, Vorstand, President, Managing Director, MD |
| **Sales** | Sales, Vertrieb, Account Executive, AE, Account Manager (mit Sales-Kontext), BDR, SDR, Business Development, New Business, Channel Sales |
| **Marketing** | Marketing, Communications, Content, Brand, PR, Demand Gen, Growth, SEO, SEA, Social Media, Digital Marketing, CMO |
| **Engineering / Tech** | Engineer, Developer, Entwickler, Software, DevOps, SRE, Data Engineer, Data Scientist, ML, AI Engineer, QA, Backend, Frontend, Full-Stack, Architect (Tech) |
| **Product** | Product Manager, PM, Product Owner, PO, Product Designer, UX, UI, Product Marketing |
| **HR / People** | HR, People, Recruiting, Recruiter, Talent, Personal, People Ops |
| **Finance** | Finance, Finanzen, Controlling, Accounting, FP&A, Treasury, CFO |
| **Operations** | Operations, Ops, Supply Chain, Logistics, COO, Project Management Office, PMO |
| **Customer Success** | Customer Success, CS, CSM, Onboarding, Account Manager (mit CS-Kontext), Support, Customer Support |
| **Legal / Compliance** | Legal, Counsel, Compliance, Datenschutz, Privacy, GRC |
| **Other** | Alles, was nicht klar zuordbar ist (Consultant ohne Fach-Kontext, "Senior Specialist", etc.) |

### Klassifizierungs-Regeln

1. **C-Level schlaegt Funktion**: "CMO" -> Leadership, NICHT Marketing. Die strategische Lesart ist wichtiger als die Funktion.
2. **Englisch und Deutsch parallel pruefen**: "Vertriebsleiter" und "Sales Director" beide -> Sales.
3. **Bei Unsicherheit: Other**. Nicht raten. Better-safe-than-wrong, weil falsche Klassifizierungen das Aggregat verzerren.
4. **"Account Manager" ist mehrdeutig**: Kontext im Headline pruefen. "Key Account Manager" -> meist Sales. "Customer Account Manager" -> meist Customer Success. Wenn unklar: "Account Manager" -> Sales als Default.
5. **"Manager" ohne Funktion**: Nur "Manager" -> Other. "Marketing Manager" -> Marketing.

### Output-Format

Erweitere die `linkedin-employees.csv` um Spalte `department_inferred` mit dem entsprechenden Bucket-Namen.

---

## Smart Sampling fuer Deep-Scrape

Ziel: aus dem Listing **die N (Default 10) Profile auswaehlen**, die fuer die Marketing-Analyse den hoechsten Erkenntniswert liefern.

### Standard-Sampling: Marketing-relevante Mischung

Default-Verteilung fuer N=10:

| Anteil | Department-Bucket | Begruendung |
|---|---|---|
| 1-2 | Leadership / C-Level | Gibt Tonalitaet und Prioritaeten der Firma vor |
| 3-4 | Marketing / Sales / Comms | Direkter Indikator fuer LinkedIn-Aktivitaet in Marketing |
| 1-2 | Product | Posts haben oft hohe Substanz, gut fuer Themen-Cluster |
| 1-2 | HR / People | Recruiting-Aktivitaet auf LinkedIn ist sichtbarer Marker |
| 1-2 | Andere (Engineering, Finance, Ops) | Repraesentation des Unternehmens-Mix |

Wenn ein Bucket leer ist (z. B. keine eigenen Marketing-Mitarbeiter sichtbar), nimm aus dem naechst-relevanten Bucket auf.

### Auswahl innerhalb eines Buckets

Bevorzuge:

1. **Erkennbare LinkedIn-Aktivitaet** im Headline/Subheadline (z. B. "Speaker | Author", "Sharing thoughts on...") - wenn aus Listing erkennbar
2. **Senior-Levels** (Director, Head of, Lead, Senior) - posten typischerweise mehr und repraesentieren die Firma staerker
3. **Laengere Tenure** (falls aus Listing ersichtlich) - kennen die Firma gut, posten substanzieller
4. **Profil-Vollstaendigkeit** - Profile mit Headline + Position + Location sind oft auch beim Posts-Scrape ergiebiger

Vermeide:

- Profile ohne Headline (oft inaktive oder sehr neue Accounts)
- Praktikanten / Werkstudenten (zu transient)
- "Looking for new opportunities" / "Open to work" Headlines (oft kein aktives Posting mehr)

### Spezialfaelle

**Wenn der User explizit ein Department fokussiert** ("nur Marketing-Profile" oder "alle C-Levels"):

- Override die Default-Verteilung
- Wenn weniger als 10 Profile im Bucket: scrape alle, melde dem User die niedrigere Sample-Groesse
- Wenn deutlich mehr: nimm 10 nach den oben genannten Bevorzugungs-Kriterien

**Wenn der User mehr als 10 Profile will**:

- Bestaetige Volume-Auswirkung auf Kosten und Laufzeit
- Bei >50: warne vor Diminishing Returns fuer Statistik

**Wenn das Listing weniger als 10 Profile hat** (sehr kleine Firma):

- Scrape alle vorhandenen
- Vermerke im Report die kleine Sample-Groesse

### Reproducibility

Fuer nachvollziehbare Auswahl: Sortiere innerhalb jedes Buckets deterministisch (z. B. alphabetisch nach Name), bevor du auswaehlst. Sonst liefert ein zweiter Lauf andere Sample-Profile, was Tracking ueber Zeit erschwert.

---

## Tenure-Berechnung

Aus den Deep-Scrape-Daten berechnest du Tenure pro Person:

```
tenure_months = (heutiges Datum) - (current_position_start_date)
```

Wenn `current_position_start_date` nicht in der Firma war (Person hatte vorher andere Position innerhalb der gleichen Firma):

- Suche die fruehste Experience-Position bei der aktuellen `current_company`
- `tenure_months` = (heute) - (fruehste Start-Date in dieser Firma)
- Das ist die "Firmen-Tenure" (Loyalty-Indikator), nicht "Position-Tenure"

Bei der Aggregat-Statistik:

- **Median-Tenure** ist robuster als Mittelwert (Ausreisser daempfen)
- **Verteilungs-Buckets** fuer den Report: `<1 Jahr`, `1-3 Jahre`, `3-5 Jahre`, `5-10 Jahre`, `>10 Jahre`
- Coverage-Quote: "Tenure berechnet fuer 7 von 10 Deep-Profile-Scrapes (70%)"

Falls Tenure nur fuer sehr wenige Profile vorliegt (<3): keine Aggregat-Statistik im Report, sondern nur Einzelangaben mit Disclaimer "Sample zu klein fuer Median".
