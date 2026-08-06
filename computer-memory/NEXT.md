# Continuation plan

The foundation is intentionally usable before the richer collectors exist. Continue in this order, using red → green → refactor for every item.

## 1. Calibrate on the target Mac
- Install editable package and run all tests.
- Run `doctor`, then `snapshot --json`.
- Capture real fixtures for Chrome/Safari JXA output and Screenpipe `/search` output (after removing sensitive content).
- Add regression tests for the real payloads before changing parsers.

## 2. Native Accessibility helper
Build a small Swift command-line helper that emits JSON for application/window/accessibility-tree state. Keep Python `Snapshot` types unchanged. Test Python adapter with fixture JSON; add Swift unit tests separately.

## 3. Browser extension for background-tab DOM context
Create an opt-in Chromium extension/native-messaging bridge. Store title/URL for all tabs by default; collect sanitized DOM text only for allowlisted domains or on explicit request. Add incognito exclusion tests.

## 4. Coding-agent and terminal state
- Add process collector (`ps`, `lsof`/cwd where safe).
- Correlate terminal processes with Git roots.
- Investigate Codex local session/log artifacts on the target machine; build an adapter only if a stable local source exists.
- Never infer "task complete" solely from window text.

## 5. Search/index layer
Normalize evidence into a searchable SQLite FTS5 table with source/time/app/window/url fields. Add MCP tools for time-range and project-scoped search.

## 6. Nightly handoff pipeline
After evidence quality is calibrated, extend the launchd job to capture then generate a handoff. Persist both the raw filtered snapshot and generated Markdown. Keep model output derivative/disposable.

## 7. Retention and encryption
Add configurable retention, database backup, and optional at-rest encryption strategy. Threat-model local malware, shared accounts, cloud backups, and accidental model exfiltration before enabling broader capture.

## Definition of a good next milestone
A local agent can ask: "Where did I leave project X?" and receive an answer whose claims can be traced back to Git state, open tabs/windows, and timestamped Screenpipe evidence.
