from __future__ import annotations

from datetime import datetime, timezone

from computer_memory.models import AppState, BrowserTab, Evidence
from computer_memory.privacy import PrivacyFilter, PrivacyRules
from computer_memory.service import SnapshotService
from computer_memory.storage import SnapshotStore


class Collector:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def collect(self):
        if self.error:
            raise RuntimeError(self.error)
        return self.value


class Screenpipe:
    def search_recent(self, minutes: int):
        return [Evidence(source="screenpipe", observed_at=datetime.now(timezone.utc), text="hello", attributes={})]


def test_service_collects_filters_persists_and_records_nonfatal_errors(tmp_path):
    store = SnapshotStore(tmp_path / "memory.db")
    service = SnapshotService(
        store=store,
        privacy_filter=PrivacyFilter(PrivacyRules.defaults()),
        app_collector=Collector([AppState(name="Codex", pid=1), AppState(name="1Password", pid=2)]),
        browser_collector=Collector([BrowserTab(browser="Chrome", window_index=0, tab_index=0, active=True, title="Docs", url="https://example.com")]),
        git_collector=Collector(error="git unavailable"),
        screenpipe=Screenpipe(),
        now=lambda: datetime(2026, 8, 5, 23, tzinfo=timezone.utc),
    )
    snap = service.capture(screenpipe_minutes=60)
    assert [a.name for a in snap.apps] == ["Codex"]
    assert snap.collector_errors == {"git": "git unavailable"}
    assert store.latest() == snap
