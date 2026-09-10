#!/usr/bin/env bash
# setup_gdrive_backup.sh
# Interactive setup for Google Drive rclone remote for Afroviolin backups.
#
# This script:
# 1. Checks/installs rclone
# 2. Guides you through creating a 'gdrive' remote via OAuth
# 3. Creates the target folder (afroviolin-backups) if needed
# 4. Tests the connection with a dry-run

set -e

echo "=== Afroviolin Google Drive Backup Setup ==="
echo

# 1. Ensure rclone is installed
if ! command -v rclone &> /dev/null; then
    echo "rclone not found. Installing..."
    curl https://rclone.org/install.sh | sudo bash
else
    echo "rclone already installed: $(rclone version | head -1)"
fi

echo
echo "=== Step 1: Create 'gdrive' remote ==="
echo "This will open your browser for Google OAuth authorization."
echo "Choose 'n' for new remote, name it 'gdrive', and select 'drive' as the type."
echo "Use default client_id/client_secret (or your own if you have a GCP project)."
echo "Choose 'desktop' as the type and complete the browser login."
echo
read -p "Press Enter to start rclone config..."

rclone config

echo
echo "=== Step 2: Verify remote and create backup folder ==="
if rclone listremotes | grep -q "^gdrive:"; then
    echo "Remote 'gdrive' found."
    echo "Creating afroviolin-backups folder (if it doesn't exist)..."
    rclone mkdir gdrive:afroviolin-backups || true
    echo "Folder ready: gdrive:afroviolin-backups"
else
    echo "ERROR: 'gdrive' remote not found. Please re-run and create it."
    exit 1
fi

echo
echo "=== Step 3: Test connection (dry-run) ==="
echo "This will list the first few files/folders without uploading anything."
rclone ls gdrive:afroviolin-backups --max-depth 1 | head -10 || echo "(empty folder is normal)"

echo
echo "=== Setup complete ==="
echo "Your Google Drive remote is ready."
echo "Default backup path: gdrive:afroviolin-backups"
echo
echo "You can now run:"
echo "  PYTHONPATH=/data/workspace python agents/backup_to_cloud.py --dry-run"
echo "  PYTHONPATH=/data/workspace python agents/backup_to_cloud.py"
echo
echo "The storage_guard.py will automatically use this remote when disk usage >= 50%."
