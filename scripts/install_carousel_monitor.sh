#!/bin/zsh
# Installs a launchd job that runs the Codex carousel monitor every 2 days (172800 s) and at login.
# Report + Claude review land in ~/Movies/ContentOS/_monitor/ with a macOS notification.
# Evaluation backend: ANTHROPIC_API_KEY is NOT copied into the plist (no secrets on disk); the job uses the local
# `claude` login (cli backend). Uninstall: launchctl unload ~/Library/LaunchAgents/com.contentos.carousel-monitor.plist
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.contentos.carousel-monitor.plist"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Movies/ContentOS/_monitor"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.contentos.carousel-monitor</string>
  <key>ProgramArguments</key><array>
    <string>$REPO/.venv/bin/python</string><string>-m</string><string>content_os.carousel_eval</string>
    <string>monitor</string><string>--scheduled</string></array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>CAROUSEL_EVAL_BACKEND</key><string>cli</string></dict>
  <key>StartInterval</key><integer>172800</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$HOME/Movies/ContentOS/_monitor/launchd.log</string>
  <key>StandardErrorPath</key><string>$HOME/Movies/ContentOS/_monitor/launchd.log</string>
</dict></plist>
PL
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "installed: $PLIST (every 2 days)"
