# AGENTS.md — Afroviolin (FS Records)

This project lives under **FS Records**, an independent business (sister company of HCA Daily).

## Project-Specific Rules

- Visual DNA: `afroviolin_v1` (locked)
- Storage path: `fs-records/afroviolin/artifacts/afroviolin_tracks/{track_id}/`
- Re-encoding: `libx264 superfast crf18 + aac 320k`
- 18-track pipeline, automatic approval mode enabled
- Secrets live in `.env`, `artifacts/*token*.json`, `.gdrive/service-account.json` — all gitignored, never commit

Last updated: 2026-09-09
