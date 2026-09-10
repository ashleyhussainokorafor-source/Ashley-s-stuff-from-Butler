#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export $(grep -v '^#' .env | xargs -d '\n')

# Establishment tracks with provided seed images
TRACKS=(
  "1f0bf6bf-e398-4260-a339-408f71eaac45"
  "703f3018-efaa-4295-af07-3436e3ef07eb"
  "3d2d0bc4-adc4-400f-b592-b9a8f07cd29c"
)

for tid in "${TRACKS[@]}"; do
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
