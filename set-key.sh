#!/usr/bin/env bash
# Prompt for the OpenAI key, write it to .env, then verify it works.
#
# The key is typed at a hidden prompt, so it never appears as a command
# argument, never lands in shell history, and never passes through a chat
# transcript. .env is gitignored and written with owner-only permissions.

set -euo pipefail
cd "$(dirname "$0")"

ENV_FILE=".env"
GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; DIM=$'\033[2m'; OFF=$'\033[0m'

printf 'Paste your OpenAI API key (input hidden), then press Enter:\n> '
read -rs KEY
printf '\n\n'

if [ -z "${KEY:-}" ]; then
  printf '%sNo key entered. Nothing written.%s\n' "$RED" "$OFF"; exit 1
fi

case "$KEY" in
  sk-*) ;;
  *) printf '%sWarning: that does not start with "sk-". Writing it anyway.%s\n' \
       "$YELLOW" "$OFF" ;;
esac

# Preserve any other settings already in .env, replacing only the key line.
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
if [ -f "$ENV_FILE" ]; then
  grep -v '^OPENAI_API_KEY=' "$ENV_FILE" > "$TMP" || true
fi
printf 'OPENAI_API_KEY=%s\n' "$KEY" >> "$TMP"
mv "$TMP" "$ENV_FILE"
trap - EXIT
chmod 600 "$ENV_FILE"
unset KEY

printf '%sKey written to .env%s %s(permissions 600, gitignored)%s\n\n' \
  "$GREEN" "$OFF" "$DIM" "$OFF"

# --- verify against the live API -----------------------------------------
printf 'Checking which configured models your account can reach...\n\n'
.venv/bin/python - <<'PY'
import os, sys
from dotenv import load_dotenv

# Explicit path: find_dotenv() walks the call stack and cannot resolve one
# when this script is fed to python over stdin.
load_dotenv(".env")

key = os.environ.get("OPENAI_API_KEY")
if not key:
    print("  Key did not load from .env."); sys.exit(1)

from openai import OpenAI
from content_os.config import load_models_config

try:
    available = {m.id for m in OpenAI().models.list()}
except Exception as exc:
    print(f"  \033[31mCould not reach the API: {type(exc).__name__}: "
          f"{str(exc)[:200]}\033[0m")
    print("  The key may be invalid, or the account may have no credit.")
    sys.exit(1)

models = load_models_config()
missing = []
for agent in models.agents:
    name = models.resolved(agent).model
    ok = name in available
    mark = "\033[32mok  \033[0m" if ok else "\033[31mMISS\033[0m"
    print(f"  {mark}  {agent:<22} {name}")
    if not ok:
        missing.append((agent, name))

print()
if missing:
    print("\033[33m  Some configured models are not available on this account.\033[0m")
    print("  Edit config/models.yaml and pick from what you do have. Close matches:")
    wanted = {n for _, n in missing}
    for stem in sorted({w.split("-")[0] + "-" + w.split("-")[1]
                        for w in wanted if "-" in w}):
        near = sorted(m for m in available if m.startswith(stem))[:6]
        if near:
            print(f"    {stem}*: {', '.join(near)}")
    sys.exit(2)

print("\033[32m  All configured models are available. Ready to run.\033[0m")
PY
