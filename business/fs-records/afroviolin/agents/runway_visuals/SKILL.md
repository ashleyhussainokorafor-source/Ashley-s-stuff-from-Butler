---
name: runway-visuals-agent
category: mlops/inference
description: Isolated agent for Runway video generation using locked Visual DNA prompts
version: 1.0.0
---

# RunwayVisualsAgent

Autonomous worker that converts locked Afroviolin prompts into Runway clips.

## Features
- Auth via `.env` (RUNWAY_API_KEY, chmod 600, git-ignored)
- Support for `gen4_turbo` (lead singles) and `seedance2_fast` (default)
- Smart polling + backoff, credit tracking
- Organizes outputs into per-track folders
- Updates `afroviolin_state.json`

**Only spawned by the orchestrator** — never direct execution.
