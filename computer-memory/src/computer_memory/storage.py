from __future__ import annotations

from pathlib import Path
import sqlite3

from .models import Snapshot


class SnapshotStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init(self):
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS snapshots (captured_at TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_time ON snapshots(captured_at DESC)")

    def save(self, snapshot: Snapshot) -> None:
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO snapshots(captured_at, payload) VALUES (?, ?)", (snapshot.captured_at.isoformat(), snapshot.to_json()))

    def latest(self) -> Snapshot | None:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM snapshots ORDER BY captured_at DESC LIMIT 1").fetchone()
        return Snapshot.from_json(row[0]) if row else None

    def list(self, limit: int = 20) -> list[Snapshot]:
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM snapshots ORDER BY captured_at DESC LIMIT ?", (limit,)).fetchall()
        return [Snapshot.from_json(r[0]) for r in rows]
