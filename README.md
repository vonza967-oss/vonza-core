# Vonza Core
A private, Jarvis-inspired personal AI assistant under active development.

**Decision (2026-11-01): OpenAI API first.** Vonza Core currently uses a hosted AI model through a server-side OpenAI API key. There is **no need to download Ollama or LM Studio** to use this branch. A local AI backend remains a possible future option, but is **not implemented**.

## Current feature-branch prototype

The `feat/working-mvp` branch contains:
- Single-owner password login with password hashing and expiring local sessions
- Conversational AI using OpenAI Chat Completions (server-side only)
- Stored conversations, approved long-term memories, and task management
- Responsive glass-style interface
- Browser-dependent push-to-talk dictation and optional device speech synthesis

**Development status:** source code and automated test cases exist; real OpenAI API responses, macOS/iPhone microphones, security penetration testing, and deployments have not been independently verified. The prototype is not a production-grade service.

## Recommended on M1 / M2 / M3 Mac: standalone application

The Apple Silicon build workflow compiles a **Vonza Core.app** that bundles its own Python runtime. You do **not** need Python 3.11, Terminal commands, Homebrew, Git, or an API key just to launch this desktop prototype.

1. From a successful [Build Mac app (Apple Silicon)](https://github.com/vonza967-oss/vonza-core/actions/workflows/build-mac.yml) workflow run, download the artifact **Vonza-Core-AppleSilicon** and unzip it to get `Vonza-Core-AppleSilicon.zip`.
2. Unzip that inner archive and move **Vonza Core.app** to Applications. Open it from Finder. It opens your default browser to a local address, where you can create your owner password.
3. Later, in the Vonza Core **Settings**, enter an OpenAI Platform API key to enable chat. Tasks and memories work without it.

**macOS security:** The build is ad-hoc signed, **not Apple Developer ID signed or notarized**. Gatekeeper may block the first launch. You may need to right-click the application and choose **Open**, or approve it under **System Settings → Privacy & Security → Open Anyway**, after verifying it came from your own GitHub build. Do not disable macOS security globally or run arbitrary scripts to bypass it. Signing/notarization is future work requiring Apple Developer credentials.

Application data, including a locally stored API key (if supplied), lives at `~/Library/Application Support/Vonza Core/`. Local API-key storage uses user-only filesystem permissions but is **not encrypted at rest**. The web interface is served only on `127.0.0.1`; the app itself is not a publicly hosted service.

**Status:** The build uses an arm64 macOS GitHub runner and performs a bundled-app startup smoke test. The real hardware, microphone, Apple Gatekeeper settings, and live OpenAI responses still require user-device verification.

## Alternative for developers: Python-based launcher

## Fast Mac setup (recommended)

Clone or download this branch, then open Terminal in the folder and run:

```sh
bash run-mac.sh
```

On the first run the script prompts for an **existing OpenAI Platform API key** without displaying what you type. It keeps it locally in `data/openai_api_key` (excluded from GitHub) with owner-only file permissions, then starts the app at **http://127.0.0.1:3000**. You can paste the key when asked, or press Enter to start without AI chat. If you have already set `OPENAI_API_KEY` in the environment, the script uses that instead. This is a **local development prototype**, not a hosted service.

An OpenAI API key requires Platform API access/billing; a ChatGPT subscription alone does not fund API usage. The script does not create API credentials or set billing limits. When you no longer want a locally saved key, delete `data/openai_api_key`. Never commit or share that file.

## Manual local run (macOS with Python 3.11+)

1. Install Python 3.11 or newer if not already installed.
2. Clone the repository and check out the prototype branch:
   ```sh
   git clone https://github.com/vonza967-oss/vonza-core.git
   cd vonza-core
   git switch feat/working-mvp
   ```
3. Keep your key out of shell history and the Git repo. In a terminal, enter:
   ```sh
   read -s OPENAI_API_KEY
   export OPENAI_API_KEY
   export OPENAI_MODEL=gpt-4.1-mini
   python3 server.py
   ```
   Paste the API key only at the invisible input after `read -s`, then press Enter.
4. Visit **http://127.0.0.1:3000** and create the single owner password (at least 12 characters).

No extra Python packages are needed. Local data defaults to `data/vonza.sqlite3`, which is excluded by `.gitignore`. You may change this path using `VONZA_DB`.

If no key is configured, tasks, memory and authentication should remain usable, while chat shows an actionable error instead of an AI answer.

Run unit/integration tests:
```sh
python3 -m unittest discover -s tests -v
```

## Billing and privacy

OpenAI API usage is **metered** and billed separately from a ChatGPT subscription. There is no monthly subscription for this app itself, but every AI request can incur a model-provider charge. Set and monitor spending controls in your OpenAI Platform account. The prototype does not yet implement its own usage cap.

Messages and the relevant saved memories are sent to OpenAI for model inference. The local database is **not encrypted at rest**. Keep the laptop, account, backups and local files secure. Never put API keys or personal conversations into this public GitHub repository.

## Security and current limitations

- Intended for a **single local owner on loopback**. Do not expose the development server directly to the internet.
- No email, calendar, computer-control integrations or autonomous actions yet.
- No always-on microphone. Dictation depends on browser support and may use the browser vendor's speech recognition service; it is **not guaranteed fully offline**.
- No local AI model integration today.
- AI calls are non-streaming; account recovery, hosted deployment hardening, encrypted storage, and audited security are not complete.
- For engineering priorities and acceptance criteria, read [AGENTS.md](AGENTS.md).

## Roadmap

1. Verify real API chat and automated tests; fix issues.
2. Add robust configuration, cost/usage telemetry, better task/memory UX.
3. Build low-latency, interruptible voice with explicit microphone controls.
4. Add permissioned real-world actions and integrations.
5. **Optional later:** a pluggable Ollama / LM Studio provider when hardware and user requirements justify it.
