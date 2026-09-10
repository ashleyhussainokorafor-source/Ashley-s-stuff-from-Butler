#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../.."
export $(grep -v '^#' .env | xargs -d '\n')

STATE_FILE="artifacts/afroviolin_state.json"

# Get all tracks that are NOT yet visuals_ready_for_approval
REMAINING=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
for tid, meta in state['tracks'].items():
    if meta.get('status') != 'visuals_ready_for_approval':
        print(tid)
")

for tid in $REMAINING; do
  echo "══════════════════════════════════════════════════════════════════"
  echo "Processing track: $tid"
  python3 agents/runway_visuals/runway_visuals_agent.py \
    --track_id "$tid" \
    --prompt_file "artifacts/afroviolin_tracks/$tid/runway_prompt.txt" \
    --output_dir "artifacts/afroviolin_tracks/$tid" \
    --image_file "artifacts/afroviolin_tracks/$tid/seed_image.png" || echo "FAILED: $tid"
  echo ""
done

echo "✅ Batch complete."
