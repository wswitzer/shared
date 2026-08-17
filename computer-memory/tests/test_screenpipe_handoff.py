from __future__ import annotations

from datetime import datetime, timezone

from computer_memory.handoff import render_handoff
from computer_memory.models import AppState, BrowserTab, Evidence, RepoState, Snapshot
from computer_memory.screenpipe import ScreenpipeClient


class FakeTransport:
    def __init__(self, payload):
        self.payload = payload
        self.last_url = None

    def get_json(self, url: str, timeout: float):
        self.last_url = url
        return self.payload


def test_screenpipe_search_normalizes_current_vision_payload():
    transport = FakeTransport({"data": [{"type": "Vision", "content": {"text": "pytest", "app_name": "Terminal", "window_name": "repo", "browser_url": None, "timestamp": "2026-08-05T22:00:00Z"}}]})
    client = ScreenpipeClient(transport=transport)
    evidence = client.search(start_time="2026-08-05T20:00:00Z", end_time="2026-08-05T23:00:00Z", limit=100)
    assert evidence[0].source == "screenpipe:vision"
    assert evidence[0].text == "pytest"
    assert evidence[0].attributes["app_name"] == "Terminal"
    assert "content_type=all" in transport.last_url
    assert "limit=100" in transport.last_url


def test_handoff_is_evidence_backed_and_labels_inference():
    t = datetime(2026, 8, 5, 23, tzinfo=timezone.utc)
    snap = Snapshot(
        captured_at=t,
        apps=[AppState(name="Codex", pid=10, frontmost=True, windows=["Pure-Linguistics-LMS"])],
        tabs=[BrowserTab(browser="Chrome", window_index=0, tab_index=0, active=True, title="PR #134", url="https://github.com/wswitzer/Pure-Linguistics-LMS/pull/134")],
        repos=[RepoState(path="/Users/me/Projects/Pure-Linguistics-LMS", branch="issue-126", head="a" * 40, dirty=True, changed_files=["src/admin.ts"])],
        evidence=[Evidence(source="screenpipe:vision", observed_at=t, text="Running tests", attributes={"app_name": "Codex", "window_name": "Pure-Linguistics-LMS"})],
    )
    text = render_handoff(snap)
    assert "## Observed state" in text
    assert "Pure-Linguistics-LMS" in text
    assert "src/admin.ts" in text
    assert "## Likely open loops (inferred)" in text
    assert "dirty" in text.lower()
    assert "Evidence:" in text
