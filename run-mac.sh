#!/usr/bin/env bash
# Mac launcher for the Vonza Core single-owner, local development prototype.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is missing. Install Python 3.11+ before running Vonza Core."
  exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "Vonza Core requires Python 3.11 or newer."
  exit 1
fi

# Prefer an already-configured environment variable. Never print or echo a key.
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  umask 077
  mkdir -p data
  chmod 700 data
  key_path="data/openai_api_key"
  if [[ -s "$key_path" ]]; then
    export OPENAI_API_KEY
    OPENAI_API_KEY="$(cat "$key_path")"
  else
    echo "First-time setup: paste your OpenAI Platform API key."
    echo "The key is not displayed and stays only on this Mac in data/openai_api_key."
    echo "Do not paste your API key into GitHub or ChatGPT."
    printf "API key (hidden): "
    IFS= read -r -s key
    printf '\n'
    if [[ -z "$key" ]]; then
      echo "No key entered. The app can still start, but AI chat will be unavailable."
    else
      printf '%s' "$key" > "$key_path"
      chmod 600 "$key_path"
      export OPENAI_API_KEY="$key"
    fi
    unset key
  fi
fi

export OPENAI_MODEL="${OPENAI_MODEL:-gpt-4.1-mini}"
export VONZA_HOST="127.0.0.1"
export VONZA_PORT="${VONZA_PORT:-3000}"
echo "Vonza Core starting locally: http://127.0.0.1:${VONZA_PORT}"
echo "To stop: press Control+C in this Terminal window."
exec python3 server.py
