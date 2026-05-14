#!/bin/bash
# REACHX MTA-Plugin — SessionStart Update-Check
#
# Vergleicht die installierte Plugin-Version (aus plugin.json) mit dem
# neuesten Git-Tag im Marketplace-Repo auf GitHub. Wenn neuer: Hinweis
# als additionalContext an Claude, damit Claude den User beim Session-
# Start proaktiv informieren kann.
#
# Design-Prinzipien:
#  - Schnell: max 3 Sekunden Netzwerk-Timeout
#  - Gecached: max 1x pro 6 Stunden gegen GitHub prüfen
#  - Robust: bei jedem Fehler lautlos exit 0, niemals den Session-Start blockieren
#  - Offline-tauglich: ohne Netzwerk kein Crash

set -u
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$0")")}"
CACHE_DIR="${HOME}/.cache/reachx-skills"
CACHE_FILE="${CACHE_DIR}/last-check"
CACHE_TTL_SECONDS=21600  # 6 Stunden

# GitHub-Repo, das den Marketplace hostet. Wird beim ersten Push gesetzt.
GITHUB_REPO="behmueller/reachx-claude-skills"

# Stille Defaults — bei jedem Problem lautlos raus
emit_silent() { exit 0; }

# Cache-Verzeichnis sicherstellen
mkdir -p "$CACHE_DIR" 2>/dev/null || emit_silent

# Cache-Check: Wenn letzter Lauf < TTL, nichts tun
if [ -f "$CACHE_FILE" ]; then
  last_check=$(cat "$CACHE_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  age=$((now - last_check))
  if [ "$age" -lt "$CACHE_TTL_SECONDS" ]; then
    emit_silent
  fi
fi

# Installierte Version lesen
PLUGIN_JSON="${PLUGIN_ROOT}/.claude-plugin/plugin.json"
if [ ! -f "$PLUGIN_JSON" ]; then
  emit_silent
fi

if command -v jq >/dev/null 2>&1; then
  INSTALLED=$(jq -r '.version' "$PLUGIN_JSON" 2>/dev/null)
else
  INSTALLED=$(grep -E '"version"' "$PLUGIN_JSON" | head -1 | sed -E 's/.*"version"[^"]*"([^"]+)".*/\1/')
fi

if [ -z "$INSTALLED" ] || [ "$INSTALLED" = "null" ]; then
  emit_silent
fi

# Neueste Version von GitHub holen — bevorzugt via gh CLI, sonst curl
LATEST=""
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  LATEST=$(timeout 3 gh api "repos/${GITHUB_REPO}/releases/latest" --jq '.tag_name' 2>/dev/null | sed 's/^v//')
fi

if [ -z "$LATEST" ] && command -v curl >/dev/null 2>&1; then
  RESP=$(timeout 3 curl -sf -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_REPO}/releases/latest" 2>/dev/null)
  if [ -n "$RESP" ]; then
    if command -v jq >/dev/null 2>&1; then
      LATEST=$(echo "$RESP" | jq -r '.tag_name' 2>/dev/null | sed 's/^v//')
    else
      LATEST=$(echo "$RESP" | grep -E '"tag_name"' | head -1 | sed -E 's/.*"tag_name"[^"]*"v?([^"]+)".*/\1/')
    fi
  fi
fi

# Cache-Zeitstempel auch bei nicht-erreichbarem GitHub aktualisieren,
# damit wir nicht jeden Session-Start neu in Timeout laufen
date +%s > "$CACHE_FILE" 2>/dev/null

if [ -z "$LATEST" ] || [ "$LATEST" = "null" ]; then
  emit_silent
fi

# Versionsvergleich (semver, vereinfacht)
if [ "$INSTALLED" = "$LATEST" ]; then
  emit_silent
fi

# sort -V macht semver-aware sort. Wenn LATEST > INSTALLED, ist Update verfügbar.
NEWEST=$(printf '%s\n%s\n' "$INSTALLED" "$LATEST" | sort -V | tail -1)
if [ "$NEWEST" != "$LATEST" ]; then
  emit_silent
fi

# Update verfügbar — JSON mit additionalContext für Claude ausgeben
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "REACHX MTA-Plugin: Update verfügbar (installiert: ${INSTALLED} → neu: ${LATEST}). Den User bei Gelegenheit informieren — Update-Befehl: /plugin update marke-und-ting-analyse-reachx@reachx-skills. Was sich geändert hat, steht im CHANGELOG.md des Plugins (Pfad: \${CLAUDE_PLUGIN_ROOT}/../../CHANGELOG.md oder im GitHub-Repo: https://github.com/${GITHUB_REPO}/blob/main/CHANGELOG.md)."
  }
}
EOF
exit 0
