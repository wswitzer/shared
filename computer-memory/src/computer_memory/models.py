from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from typing import Any


def _dt(value: str | datetime) -> datetime:
    return value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(eq=True)
class AppState:
    name: str
    pid: int | None = None
    frontmost: bool = False
    windows: list[str] = field(default_factory=list)


@dataclass(eq=True)
class BrowserTab:
    browser: str
    window_index: int
    tab_index: int
    active: bool
    title: str
    url: str


@dataclass(eq=True)
class RepoState:
    path: str
    branch: str | None
    head: str | None
    dirty: bool
    changed_files: list[str] = field(default_factory=list)


@dataclass(eq=True)
class Evidence:
    source: str
    observed_at: datetime
    text: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(eq=True)
class Snapshot:
    captured_at: datetime
    apps: list[AppState] = field(default_factory=list)
    tabs: list[BrowserTab] = field(default_factory=list)
    repos: list[RepoState] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    collector_errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["captured_at"] = self.captured_at.isoformat()
        for item in payload["evidence"]:
            item["observed_at"] = item["observed_at"].isoformat()
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Snapshot":
        return cls(
            captured_at=_dt(payload["captured_at"]),
            apps=[AppState(**x) for x in payload.get("apps", [])],
            tabs=[BrowserTab(**x) for x in payload.get("tabs", [])],
            repos=[RepoState(**x) for x in payload.get("repos", [])],
            evidence=[Evidence(source=x["source"], observed_at=_dt(x["observed_at"]), text=x.get("text", ""), attributes=x.get("attributes", {})) for x in payload.get("evidence", [])],
            collector_errors=dict(payload.get("collector_errors", {})),
        )

    @classmethod
    def from_json(cls, raw: str) -> "Snapshot":
        return cls.from_dict(json.loads(raw))
