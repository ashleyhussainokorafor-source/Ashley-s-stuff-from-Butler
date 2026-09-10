#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Load guard via Python helper (respects AFROVIOLIN_SKIP_LOAD_GUARD)
python3 -c "
try:
    from agents.load_guard import check_load_or_exit
    check_load_or_exit(max_load=45, check_mem=True, min_free_gb=8)
except Exception as e:
    print(f'[load_guard] Warning: {e}')
" || true

echo "=============================================================="
echo "STAGING ROBUST RE-ENCODED VIDEOS AND RE-UPLOADING TO YOUTUBE"
echo "=============================================================="

# Step 1: Re-assemble videos with libx264 re-encoding (prevents freeze/corruption)
python3 agents/assemble_videos.py

# Step 2: Upload robust videos to YouTube
python3 agents/upload_to_youtube.py

echo "=============================================================="
echo "PIPELINE BATCH COMPLETE!"
echo "=============================================================="
