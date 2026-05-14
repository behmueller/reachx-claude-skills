# Aggregatoren-Blocklist

Bekannte Aggregator-Domains, Marktplätze und Verzeichnisse, die **nicht** als Wettbewerber im klassischen Sinn behandelt werden, auch wenn sie in Sistrix-Toplisten zu Branchen-Keywords ganz oben stehen.

Diese Liste ist **Standard** — jeder MTA-Lauf nutzt sie automatisch. Branchen-spezifische Zusatz-Blocklist wird im Schema (`identifikation-schema.md`, Feld `aggregatoren_blocklist_zusatz`) ergänzt.

## Warum diese Filterung wichtig ist

Wenn man bei Sistrix die Toplist für ein Branchen-Keyword zieht (z. B. "kabel messen tool"), stehen meist Amazon, eBay, Conrad, Idealo, ProvenExpert oben — weil diese Plattformen riesige Sichtbarkeit haben. Sie sind aber **keine direkten Wettbewerber**, sondern Vertriebs- oder Reputations-Kanäle, oft sogar **Partner**, in denen der Kunde seine Produkte selbst listet.

Ein Skill, der diese als "Wettbewerber" identifiziert, würde dem Strategen Zeit klauen, weil er sie manuell wieder rausnehmen müsste.

## Filter-Logik

Die Blocklist wird auf zwei Ebenen angewendet:

1. **Domain-Level**: Wenn die gefundene Wettbewerber-URL eine Domain aus der Blocklist hat, wird der Eintrag verworfen.
2. **Sub-Domain-Level**: Auch `shop.example.com`, wenn `example.com` in der Blocklist, wird gefiltert.

Branchen-spezifische Plattformen (z. B. Jameda für Ärzte) werden **nicht** als Wettbewerber, sondern als **Touchpoints** behandelt — siehe `branchenportale-mapping.md`. Sie sind in der Blocklist enthalten, damit sie nicht in der Wettbewerber-Liste landen, sondern in der Branchenportale-Analyse (eigener Skill `02-04-branchenportal-recherche`).

## Standard-Blocklist

### Generische Marktplätze

```
amazon.de
amazon.com
ebay.de
ebay-kleinanzeigen.de
otto.de
zalando.de
mediamarkt.de
saturn.de
kaufland.de
real.de
allyouneed.com
```

### Preisvergleichs- und Aggregator-Plattformen

```
idealo.de
billiger.de
geizhals.de
preisvergleich.de
guenstiger.de
shopping24.de
ladenzeile.de
shopalike.de
ebay.de
google.com  # shopping-spezifische Google-Subseiten
```

### Branchenportale (werden separat behandelt)

```
jameda.de
doctolib.de
sanego.de
arzt-auskunft.de
anwalt.de
anwalt24.de
juraforum.de
myhammer.de
houzz.de
booking.com
hrs.de
trivago.de
expedia.de
tripadvisor.de
holidaycheck.de
opentable.de
quandoo.de
thefork.de
yelp.de
provenexpert.de
trustpilot.com
trustedshops.de
ekomi.de
g2.com
capterra.de
omr.com
getapp.de
softwareadvice.de
trustradius.com
clutch.co
kununu.de
wlw.de
europages.de
immowelt.de
immoscout24.de
immonet.de
```

### Massen-Verzeichnisse

```
gelbeseiten.de
dasoertliche.de
11880.com
goyellow.de
branchenbuch.de
firmenfinden.de
yelp.de
foursquare.com
```

### Content-Aggregatoren (häufig in Toplisten)

```
wikipedia.org
de.wikipedia.org
youtube.com
pinterest.de
pinterest.com
reddit.com
quora.com
stackexchange.com
stackoverflow.com
medium.com
github.com
```

### Große B2B-Konzerne (Großhändler, oft Sichtbarkeits-Schwergewichte für Branchen-Keywords)

```
conrad.de
voelkner.de
reichelt.de
buerklin.com
schaefer-shop.de
wuerth.de
hagebau.de
hornbach.de
bauhaus.de
obi.de
```

### Stellenportale (bei B2B/Recruiting-Suchen aufdringlich)

```
xing.de
indeed.com
indeed.de
stepstone.de
monster.de
jobware.de
linkedin.com  # Achtung: LinkedIn-Company-Pages werden separat genutzt im LinkedIn-Audit
```

### News und Brancheninfos

```
focus.de
spiegel.de
welt.de
faz.net
handelsblatt.com
n-tv.de
zeit.de
manager-magazin.de
wirtschaftswoche.de
```

## Wann eine Ausnahme zulässig ist

Es gibt Edge Cases, in denen ein Aggregator **doch** als Wettbewerber zählt:

1. **Eigene Marken in einer Plattform** — wenn Amazon im konkreten Fall der Hauptvertriebs- und Marketingkanal des Kunden ist, kann es sinnvoll sein, große Konkurrenten im selben Amazon-Marketplace als "Wettbewerber" zu betrachten. Wird im Schema-Frontmatter über `aggregatoren_blocklist_zusatz` als negative Liste (Ausnahmen) gehandhabt.
2. **Plattform-Modelle, die zur Konkurrenz werden** — wenn Casafan z. B. einen direkten DC-Vertrieb aufbaut und Amazon der Hauptkonkurrent für die Sichtbarkeit ist, kann Amazon als "Wettbewerber" mit Hinweis-Flag aufgenommen werden.

In beiden Fällen: **explizit im Schema dokumentieren**, warum die Ausnahme gemacht wird.

## Wartung dieser Liste

Diese Liste ist statisch, aber wachsend. Empfehlung:

- Alle 6 Monate prüfen, ob neue große Aggregatoren dazu gekommen sind
- Bei jedem MTA-Lauf, in dem der Stratege manuell Aggregatoren aus der Sistrix-Toplist filtert, prüfen, ob diese Domain hier ergänzt werden sollte
- Wenn ein Aggregator nicht mehr aktiv ist (z. B. abgeschaltete Plattform), aus der Liste entfernen mit Kommentar
