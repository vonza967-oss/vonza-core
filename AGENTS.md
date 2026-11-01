# AGENTS.md: Vonza Core engineering brief

## Mission
Build Vonza Core from scratch as a private, dependable personal AI assistant with a Jarvis-like experience. This is a NEW independent product. Do not import code, data, or configuration from older Vonza, Vonza Assistant, or Lovable projects. The goal is a functioning assistant, not a static demo or marketing site.

## Working style
- Work autonomously on sensible implementation decisions; do not stop at planning or ask the owner to copy files, write code, or run commands that an agent can do.
- Implement small, testable increments; run checks and fix failures before reporting completion.
- Inspect the repository and read this file first. Continue from current source; never overwrite work in progress without inspection.
- Keep changes understandable, maintainable, and production-minded. Document setup and any blockers clearly.
- Do not claim real-world integrations or tests work unless verified.
- Commit and/or open a PR with implemented changes when the environment permits. Do not force push or rewrite history.

## Experience and design
- Hungarian and English, with clear language selection and reliable language consistency.
- Premium, fast, desktop-first and mobile-responsive interface: bright translucent/glass appearance by default, dark mode optional. Functional accessibility and readability take priority over visual effects.
- Primary modes: Chat, Tasks, Memory, Settings. Keep navigation compact and simple.
- Chat should stream responses when possible; provide conversation history, cancellation, error handling, and clear connected/offline states.
- A useful assistant should perform explicitly approved actions, not only answer questions.

## MVP acceptance criteria (priority order)
1. **Runnable application:** working local development instructions, reproducible setup, sensible stack, environment variable template, health endpoint, and basic test suite.
2. **Authentication and ownership:** secure single-owner authentication. Keep private user content segregated and inaccessible before login. Do not hardcode passwords or secrets.
3. **AI chat:** server-side OpenAI integration with configurable model, streamed or responsive replies, proper system instructions, request timeouts, rate limits, and user-visible error states. Never expose the API key to client-side code.
4. **Conversations:** create, list, reopen, rename and delete conversations. Persist securely. Support interruption/cancel behavior where possible.
5. **Memory:** explicit opt-in long-term memory only. User can inspect, edit, and delete every stored memory. Do not silently promote chat content into durable memory. Clearly distinguish chat history from saved memories.
6. **Tasks:** create, view, complete, edit, delete tasks, with deadlines and simple local reminders when reliable and consented.
7. **Voice v1:** push-to-talk or tap-to-record with transcribed text review, spoken responses, and visible mute/stop controls. Handle microphone permission gracefully. No always-on listening by default.
8. **Verification:** unit/integration tests for auth boundaries, chat failures, task CRUD, memory consent/deletion, and safe secret handling; build/lint/test pass.
9. **Documentation:** README with tested start steps for macOS and Windows, configuration, limitations, and next milestones.

## Architecture
- Favor a pragmatic TypeScript stack (e.g., Next.js App Router + React with a server-side API) if starting fresh in Codex; a similarly simple stack is acceptable when justified.
- Favor server-side persistence with a migration path to hosted Postgres. Local SQLite is acceptable for a single-user development prototype. Do not silently mix production and demo databases.
- Organize code around services/modules for auth, chat, memory, tasks, voice; keep provider APIs behind interfaces to allow replacement.
- Use structured validation for all untrusted inputs. Keep external action tools permissioned, scoped, logged, and revocable.
- Avoid implementing calendar, email, computer control, web browsing, or background automations as working features until an actual integration and approval UX exists.

## Security and privacy (non-negotiable)
- This GitHub repository is currently **PUBLIC**. Never commit .env, secrets, API keys, tokens, cookies, real personal data, conversation transcripts or private uploads.
- Protect and ignore local DB files, .env variants, logs, and generated content.
- AI API keys must be stored only as server-side environment variables. Never print keys in logs or errors.
- Use secure session cookies, CSRF protection as appropriate, rate limits, password hashing, and restrictive CORS. Avoid creating an unauthenticated publicly reachable assistant.
- Confirm before any consequential external action (sending, deleting, spending, publishing, modifying external services); show outcome and errors honestly.
- Default voice recording and transcript retention to minimal/transparent behavior; no hidden always-on microphone.

## Definition of done for the FIRST milestone
- A developer can clone, install, configure and start the application from a clean checkout.
- A single owner can sign in, converse with a configured model, save/edit/delete an approved memory, and manage tasks in a coherent UI.
- Application stays usable and explains failure when the OpenAI key is missing or invalid.
- All tests and build pass, or failures are explicitly reported with exact reproduction steps.
- README documents which voice and external integrations are real vs. not yet implemented.

## Next milestone after MVP
Implement low-latency, natural, interruptible voice conversation using supported realtime interfaces; then add safe action integrations (calendar, email, external tasks) with explicit owner approvals and activity logs. Measure round-trip latency and test on desktop and iPhone Safari. Do not describe it as ChatGPT-equivalent until verified in realistic usage.
