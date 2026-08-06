#!/usr/bin/env bash
set -euo pipefail
LABEL="com.local.computer-memory.nightly"
HOUR="${1:-2}"
PYTHON="$(command -v python3)"
CONFIG="${COMPUTER_MEMORY_CONFIG:-$HOME/.config/computer-memory/config.toml}"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$(dirname "$PLIST")"
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>$LABEL</string>
<key>ProgramArguments</key><array><string>$PYTHON</string><string>-m</string><string>computer_memory</string><string>--config</string><string>$CONFIG</string><string>snapshot</string></array>
<key>StartCalendarInterval</key><dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>0</integer></dict>
<key>StandardOutPath</key><string>$HOME/Library/Logs/computer-memory.log</string>
<key>StandardErrorPath</key><string>$HOME/Library/Logs/computer-memory.err.log</string>
</dict></plist>
PLIST
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed $LABEL for ${HOUR}:00."
