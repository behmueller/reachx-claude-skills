#!/bin/bash
# REACHX MTA-Plugin — Token-Tracking nach jedem Prompt
#
# Wird vom Stop-Hook aufgerufen (nach jeder Claude-Antwort). Aggregiert die neuen
# Token-Daten in den lokalen Cache und pusht periodisch (alle 5 Min) nach Drive.
#
# Wichtig:
#   - **Non-blocking**: Läuft in Hintergrund, blockiert nie den Session-Flow.
#   - **Silent**: Bei jedem Fehler lautlos exit 0. Stop-Hook darf Session nicht crashen.
#   - **Throttled Drive-Sync**: Lokal nach jedem Prompt, Drive nur alle 5 Min.

set -u
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$0")")}"
TRACKER="${PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
DRIVE="${PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
CACHE_DIR="${HOME}/.cache/reachx-mta"
DRIVE_SYNC_THROTTLE=300  # Sekunden zwischen Drive-Pushes
LOCK_FILE="${CACHE_DIR}/token-sync.lock"

emit_silent() { exit 0; }

# Falls Tracker fehlt (Plugin defekt): silent raus
[ -f "$TRACKER" ] || emit_silent

# Anti-concurrent-Lock: wenn schon ein anderer Sync läuft, skip
if [ -f "$LOCK_FILE" ]; then
  pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    emit_silent
  fi
fi
echo $$ > "$LOCK_FILE" 2>/dev/null || true

# 1. Lokale Aggregation (immer, nach jedem Prompt — schnell, lokal)
SLUG=$(python3 "$TRACKER" tick-and-print-slug 2>/dev/null || echo "")

if [ -z "$SLUG" ]; then
  rm -f "$LOCK_FILE" 2>/dev/null
  emit_silent
fi

# 2. Drive-Sync: nur wenn letzter Push älter als DRIVE_SYNC_THROTTLE
STAMP_FILE="${CACHE_DIR}/${SLUG}/last-drive-push.stamp"
should_push=1
if [ -f "$STAMP_FILE" ]; then
  last=$(cat "$STAMP_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  age=$((now - last))
  [ "$age" -lt "$DRIVE_SYNC_THROTTLE" ] && should_push=0
fi

if [ "$should_push" = "1" ] && [ -f "$DRIVE" ]; then
  AGG_FILE="${CACHE_DIR}/${SLUG}/token-usage.json"
  if [ -f "$AGG_FILE" ]; then
    # MTA-Folder-ID aus active-mtas.json holen
    FOLDER_ID=$(python3 -c "
import json, sys
try:
    with open('${HOME}/.cache/reachx-mta/active-mtas.json') as f:
        d = json.load(f)
    print(d.get('${SLUG}', {}).get('folder_id', ''))
except Exception:
    pass
" 2>/dev/null)

    if [ -n "$FOLDER_ID" ]; then
      # meta/-Sub-Folder finden oder anlegen, dann hochladen
      META_FOLDER_ID=$(python3 "$DRIVE" find-or-create-folder "$FOLDER_ID" "meta" 2>/dev/null)
      if [ -n "$META_FOLDER_ID" ]; then
        python3 "$DRIVE" upsert-text "$META_FOLDER_ID" "token-usage.json" "$AGG_FILE" "application/json" >/dev/null 2>&1
        echo "$(date +%s)" > "$STAMP_FILE" 2>/dev/null
      fi
    fi
  fi
fi

rm -f "$LOCK_FILE" 2>/dev/null
emit_silent
