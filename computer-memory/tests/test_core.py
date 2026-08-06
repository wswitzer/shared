from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import subprocess

from computer_memory.collectors import BrowserCollector, GitCollector
from computer_memory.models import AppState, BrowserTab, Evidence, RepoState, Snapshot
from computer_memory.privacy import PrivacyFilter, PrivacyRules
from computer_memory.storage import SnapshotStore


class FakeRunner:
    def __init__(self, output: str):
        self.output = output
        self.calls: list[list[str]] = []

    def run(self, args: list[str], timeout: float = 10) -> str:
        self.calls.append(args)
        return self.output


def now() -> datetime:
    return datetime(2026, 8, 5, 23, 0, tzinfo=timezone.utc)


def test_snapshot_json_round_trip_preserves_nested_state():
    snap = Snapshot(
        captured_at=now(),
        apps=[AppState(name="Codex", pid=42, frontmost=True, windows=["Pure-Linguistics-LMS"])],
        tabs=[BrowserTab(browser="Google Chrome", window_index=1, tab_index=2, active=True, title="GitHub", url="https://github.com/wswitzer/shared")],
        repos=[RepoState(path="/tmp/repo", branch="main", head="abc", dirty=True, changed_files=["a.py"])],
        evidence=[Evidence(source="screenpipe", observed_at=now(), text="Running tests", attributes={"app_name": "Codex"})],
        collector_errors={"audio": "disabled"},
    )
    restored = Snapshot.from_json(snap.to_json())
    assert restored == snap


def test_privacy_filter_excludes_sensitive_apps_and_urls_and_redacts_secrets():
    snap = Snapshot(
        captured_at=now(),
        apps=[AppState(name="1Password", pid=1), AppState(name="Codex", pid=2, windows=["token=sk-abcdef1234567890"])],
        tabs=[
            BrowserTab(browser="Chrome", window_index=0, tab_index=0, active=True, title="PayPal", url="https://paypal.com/activity"),
            BrowserTab(browser="Chrome", window_index=0, tab_index=1, active=False, title="Docs", url="https://example.com/?token=secret-value"),
        ],
        evidence=[Evidence(source="screenpipe", observed_at=now(), text="Authorization: Bearer abcdefghijklmnop", attributes={})],
    )
    filtered = PrivacyFilter(PrivacyRules.defaults()).apply(snap)
    assert [a.name for a in filtered.apps] == ["Codex"]
    assert [t.title for t in filtered.tabs] == ["Docs"]
    assert "sk-abcdef" not in filtered.apps[0].windows[0]
    assert "secret-value" not in filtered.tabs[0].url
    assert "abcdefghijklmnop" not in filtered.evidence[0].text


def test_browser_collector_parses_all_tabs_from_jxa_json():
    runner = FakeRunner('[{"browser":"Google Chrome","window_index":0,"tab_index":0,"active":true,"title":"Codex","url":"https://chatgpt.com/codex"},{"browser":"Google Chrome","window_index":0,"tab_index":1,"active":false,"title":"GitHub","url":"https://github.com"}]')
    tabs = BrowserCollector(runner=runner).collect()
    assert len(tabs) == 2
    assert tabs[0].active is True
    assert tabs[1].title == "GitHub"
    assert runner.calls[0][0:2] == ["osascript", "-l"]


def test_git_collector_reports_branch_head_dirty_and_changed_files(tmp_path: Path):
    repo = tmp_path / "project"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    (repo / "a.txt").write_text("one\n")
    subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "initial"], check=True)
    (repo / "a.txt").write_text("two\n")
    states = GitCollector(roots=[repo], max_depth=0).collect()
    assert len(states) == 1
    assert states[0].branch == "main"
    assert states[0].dirty is True
    assert states[0].changed_files == ["a.txt"]
    assert len(states[0].head) == 40


def test_sqlite_store_round_trip_and_latest(tmp_path: Path):
    store = SnapshotStore(tmp_path / "memory.db")
    first = Snapshot(captured_at=datetime(2026, 8, 5, 20, tzinfo=timezone.utc))
    second = Snapshot(captured_at=datetime(2026, 8, 5, 21, tzinfo=timezone.utc), apps=[AppState(name="Codex", pid=4)])
    store.save(first)
    store.save(second)
    assert store.latest() == second
    assert store.list(limit=2) == [second, first]
