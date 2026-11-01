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

## Local run (macOS with Python 3.11+)

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
