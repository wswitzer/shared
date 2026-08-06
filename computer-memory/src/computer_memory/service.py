from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from .models import Snapshot


class SnapshotService:
    def __init__(self, *, store, privacy_filter, app_collector, browser_collector, git_collector, screenpipe=None, now: Callable[[], datetime] | None = None):
        self.store = store
        self.privacy_filter = privacy_filter
        self.app_collector = app_collector
        self.browser_collector = browser_collector
        self.git_collector = git_collector
        self.screenpipe = screenpipe
        self.now = now or (lambda: datetime.now(timezone.utc))

    def capture(self, screenpipe_minutes: int = 120) -> Snapshot:
        snap = Snapshot(captured_at=self.now())
        for name, collector, attr in (
            ("apps", self.app_collector, "apps"),
            ("browser", self.browser_collector, "tabs"),
            ("git", self.git_collector, "repos"),
        ):
            try:
                setattr(snap, attr, collector.collect())
            except Exception as exc:
                snap.collector_errors[name] = str(exc)
        if self.screenpipe is not None:
            try:
                snap.evidence = self.screenpipe.search_recent(screenpipe_minutes)
            except Exception as exc:
                snap.collector_errors["screenpipe"] = str(exc)
        snap = self.privacy_filter.apply(snap)
        self.store.save(snap)
        return snap
