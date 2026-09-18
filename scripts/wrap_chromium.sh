#!/bin/bash
# Wrap Playwright's Chromium binaries IN PLACE so they always get the fixlibs
# on LD_LIBRARY_PATH, regardless of how the caller resolves/launches them.
#
#   chrome              -> chrome.bin  (real ELF, backed up)
#   chrome-headless-shell -> chrome-headless-shell.bin
#
# Idempotent: re-running is safe. Restores are possible from the .bin backups.
set -uo pipefail

FIXLIBS=/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu

wrap() {
  local REAL_BIN="$1"
  local DIR; DIR=$(dirname "$REAL_BIN")
  local BASE; BASE=$(basename "$REAL_BIN")
  local BACKUP="$REAL_BIN.bin"

  if [ ! -f "$REAL_BIN" ]; then
    echo "  SKIP (not found): $REAL_BIN"
    return
  fi
  # already wrapped? (wrapper is a text script, real binary is ELF)
  if head -c 2 "$REAL_BIN" 2>/dev/null | grep -q '#!'; then
    echo "  ALREADY WRAPPED: $REAL_BIN"
    return
  fi
  cp -p "$REAL_BIN" "$BACKUP" || { echo "  FAILED backup: $REAL_BIN"; return; }

  cat > "$REAL_BIN" <<EOF
#!/bin/bash
# Auto-generated wrapper: inject fixlibs before launching the real Chromium.
# Real binary preserved at ${BASE}.bin
FIXLIBS=${FIXLIBS}
if [ -d "\$FIXLIBS" ]; then
  export LD_LIBRARY_PATH="\$FIXLIBS\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
fi
export DBUS_SESSION_BUS_ADDRESS="\${DBUS_SESSION_BUS_ADDRESS:-disabled:}"
exec "${DIR}/${BASE}.bin" "\$@"
EOF
  chmod +x "$REAL_BIN"
  echo "  WRAPPED: $REAL_BIN  (real -> ${BASE}.bin)"
}

echo "=== wrapping Chromium binaries ==="
wrap /data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome
wrap /data/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell

echo
echo "=== verify wrapper is a script, backup is ELF ==="
F=/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome
head -c 20 "$F"; echo "   <- wrapper head"
file "$F.bin" 2>/dev/null | head -1