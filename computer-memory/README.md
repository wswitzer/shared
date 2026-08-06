# Computer Memory

Local-first, evidence-backed computer state memory for macOS. The goal is not to keep an LLM staring at the screen all day; it is to **capture cheaply, preserve evidence, and reason on demand**.

## What works in this first milestone

- Enumerates running foreground macOS apps and their window titles via System Events/JXA.
- Enumerates **all open tabs** (not only the visible tab) in Chrome, Brave, Edge, Chromium, and Safari via JXA.
- Discovers Git repositories under configured roots and records branch, HEAD, dirty state, and changed files.
- Queries a local Screenpipe instance (`http://localhost:3030`) for recent screen evidence.
- Applies privacy exclusions/redaction **before persistence**.
- Stores snapshots in local SQLite.
- Generates a deterministic Markdown handoff that separates observations from inferences.
- Can optionally pass the deterministic handoff to an OpenAI-compatible **local** model such as Ollama.
- Exposes latest state/history through an optional MCP server.
- Includes a `launchd` installer for nightly snapshot capture.

Screenpipe is optional: browser/Git/app state still works without it.

## Install

```bash
cd computer-memory
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
mkdir -p ~/.config/computer-memory
cp config.example.toml ~/.config/computer-memory/config.toml
```

macOS will likely ask for Automation/Accessibility permission the first time `osascript` inspects other applications. Grant only the permissions you are comfortable with in **System Settings → Privacy & Security**.

## First run

```bash
computer-memory doctor
computer-memory snapshot
computer-memory latest
computer-memory handoff
```

The SQLite database defaults to `~/.local/share/computer-memory/memory.db`; handoffs go to `~/.local/share/computer-memory/handoffs/YYYY-MM-DD.md`.

## Screenpipe

Run Screenpipe separately, then leave `[screenpipe].enabled = true`. If it is unavailable, snapshot capture continues and records the collector error instead of failing the entire snapshot.

## Local LLM

The example config targets an OpenAI-compatible local endpoint:

```toml
[llm]
base_url = "http://localhost:11434/v1"
model = "qwen3:14b"
```

Generate a model-written handoff with `computer-memory handoff --local-llm`. The model receives the deterministic evidence-backed handoff, not unrestricted access to your machine. The system prompt explicitly prohibits invented facts and asks it to separate observations from inferences.

## MCP

```bash
pip install -e '.[mcp]'
python -m computer_memory.mcp_server
```

Current MCP tools are `latest_state`, `latest_handoff`, and `recent_snapshots`.

## Nightly capture

After installing the package into the Python environment you intend to keep:

```bash
./scripts/install-launchd.sh 2
```

That schedules a snapshot at 02:00 local time. The script deliberately installs **capture only**; model summarization can be added once local permissions and the evidence quality are calibrated.

## Privacy model

The default rules exclude password-manager windows and several authentication/payment URL patterns. Token-like strings are redacted before persistence. Before continuous use, add your own financial, private-message, client, or other sensitive applications/domains to `config.toml`.

Important design invariant: **raw sensitive evidence should be rejected/redacted before it reaches SQLite or an LLM**.

## TDD workflow

This project started from failing tests. Continue with red → green → refactor:

```bash
pytest -q
```

Every new collector should have deterministic fixtures/fakes and tests for expected captured state, partial permission/failure behavior, privacy filtering, stable serialization, and evidence-backed inference.

## Architecture

```text
macOS apps ─┐
browser tabs├──── collectors ── privacy filter ── Snapshot ── SQLite
Git repos ──┤                                      │
Screenpipe ─┘                                      ├─ deterministic handoff
                                                   ├─ optional local LLM
                                                   └─ MCP tools
```

Collectors are intentionally thin adapters. The stable boundary is the `Snapshot` model. A future native Swift Accessibility helper can replace the JXA app/window collector without migrating stored data or changing downstream agents.

## Current limitations

- Browser collection uses macOS Automation/JXA. It does not yet capture hidden DOM text from every background tab. Screenpipe supplies visible/accessibility history; a browser extension is the logical next step for opt-in DOM capture.
- Codex/other coding-agent intent is inferred from window titles, repo state, and Screenpipe evidence; there is no Codex-specific session-log adapter yet.
- Terminal shell history/process-to-repo correlation is not yet collected.
- Screenpipe response formats should be calibrated against real local fixtures.
- MCP exposes stored snapshots but does not yet offer full-text search across normalized evidence.

See `NEXT.md` for the recommended continuation sequence.
