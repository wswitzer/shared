# Agent instructions — Computer Memory

Scope: everything under this `computer-memory/` folder.

## Mission
Build a local-first, privacy-conscious, evidence-backed memory layer that lets AI agents reconstruct the user's computer work state without continuously running a large model.

## Non-negotiable invariants
1. TDD: add/adjust a failing test before changing behavior.
2. Capture is evidence; interpretation is inference. Never collapse those two concepts.
3. Privacy filtering/redaction happens before persistence and before model calls.
4. Collector failure is isolated; one unavailable source must not prevent the rest of a snapshot.
5. No secret/API key should be required for baseline operation.
6. Prefer local APIs and standard library dependencies. Add dependencies only with a concrete justification.
7. Preserve backward compatibility of the `Snapshot` JSON shape or provide an explicit migration.
8. Do not add continuous high-frequency LLM calls. Capture cheaply; reason on demand.

## Validation
Run `python3 -m pytest -q` from this folder. For macOS manual validation, run `computer-memory doctor`, then `computer-memory snapshot --json` after granting only the necessary Automation/Accessibility permissions.

## Coding style
Small typed Python modules; dependency injection around OS/network calls; deterministic tests with fakes; no tests that require Screenpipe, a browser, or macOS GUI state.
