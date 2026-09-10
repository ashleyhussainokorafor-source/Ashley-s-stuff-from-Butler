# Afroviolin Storage Architecture

**Policy:** Local disk usage must never exceed 50%. All large assets live in Cloudflare R2.

## Core Principles

1. **Cloud-first** — Generated video/audio/metadata written directly to R2
2. **Local only for state** — Config, prompts, scripts, and small state files stay local
3. **One bucket per project** — Clean isolation and billing
4. **Least-privilege tokens** — Each project gets its own scoped API token
5. **Automated setup** — Use `storage_manager.py` for new projects

## Current Setup

| Item | Value |
|------|-------|
| Primary remote | `cloudflare-r2` |
| Bucket | `fs-records` |
| Base path | `Afroviolin/afroviolin_tracks` |
| Local limit | 50% |
| Current usage | ~18% |

## Creating Storage for a New Project

```bash
cd /data/workspace/afroviolin
python3 scripts/storage/storage_manager.py my-new-project
```

The script will:
1. Verify local storage is under 50%
2. Guide you through bucket + token creation in Cloudflare
3. Automatically write the rclone remote
4. Update the project `.env` with storage variables

## Manual Rclone Remote Template

```ini
[cloudflare-my-project]
type = s3
provider = Cloudflare
access_key_id = <key>
secret_access_key = <secret>
endpoint = https://7331f696a15eee3fe7bf94f41376f7b8.r2.cloudflarestorage.com
acl = private
bucket = fs-records-my-project-assets
```

## Storage Guard

Run before any heavy local operation:

```bash
python3 scripts/storage_guard.py
```

## Commands

```bash
# List all Cloudflare remotes
rclone listremotes | grep cloudflare

# Check bucket size
rclone size cloudflare-r2:fs-records

# Dry-run migration
rclone sync ./local cloudflare-r2:fs-records/path --dry-run
```

## Token Lifecycle

- Rotate every 6–12 months
- Create new token first, update rclone, then delete old token
- Never commit tokens to git

Last updated: 2026-08-26
