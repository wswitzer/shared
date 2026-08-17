from __future__ import annotations

from pathlib import Path
from .models import Snapshot


def _short(text: str, n: int = 140) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= n else clean[: n - 1] + "…"


def render_handoff(snapshot: Snapshot) -> str:
    lines = [f"# Computer handoff — {snapshot.captured_at.astimezone().strftime('%Y-%m-%d %H:%M %Z')}", "", "## Observed state"]
    if snapshot.apps:
        lines += ["", "### Open applications"]
        for app in sorted(snapshot.apps, key=lambda a: (not a.frontmost, a.name.lower())):
            marker = " **(frontmost)**" if app.frontmost else ""
            wins = f" — windows: {', '.join(app.windows[:4])}" if app.windows else ""
            lines.append(f"- {app.name}{marker}{wins}")
    if snapshot.tabs:
        lines += ["", "### Browser tabs"]
        for tab in snapshot.tabs:
            marker = "active" if tab.active else "background"
            lines.append(f"- [{marker}] {tab.browser}: {tab.title} — {tab.url}")
    if snapshot.repos:
        lines += ["", "### Git repositories"]
        for repo in snapshot.repos:
            state = "dirty" if repo.dirty else "clean"
            lines.append(f"- {Path(repo.path).name}: `{repo.branch or 'detached'}` @ `{(repo.head or 'unknown')[:12]}` — **{state}**")
            for changed in repo.changed_files[:12]:
                lines.append(f"  - changed: `{changed}`")
    if snapshot.evidence:
        lines += ["", "### Recent Screenpipe evidence"]
        for item in snapshot.evidence[-20:]:
            app = item.attributes.get("app_name") or item.attributes.get("window_name") or item.source
            lines.append(f"- {item.observed_at.astimezone().strftime('%H:%M')} {app}: {_short(item.text)}")
    lines += ["", "## Likely open loops (inferred)"]
    inferred = []
    for repo in snapshot.repos:
        if repo.dirty:
            inferred.append(f"- `{Path(repo.path).name}` has uncommitted changes; review/commit/discard them before assuming that work is complete. Evidence: Git status reports {len(repo.changed_files)} changed file(s).")
    active_tabs = [t for t in snapshot.tabs if t.active]
    for tab in active_tabs[:5]:
        inferred.append(f"- You may have been actively using **{tab.title}**. Evidence: it was the active tab in {tab.browser} at snapshot time.")
    if not inferred:
        inferred.append("- No obvious unfinished work can be inferred from the snapshot alone.")
    lines += inferred
    if snapshot.collector_errors:
        lines += ["", "## Collector warnings"] + [f"- {name}: {error}" for name, error in sorted(snapshot.collector_errors.items())]
    lines += ["", "> Inferences are intentionally separated from observations. Treat the observed state as evidence and verify inferred next steps before acting."]
    return "\n".join(lines) + "\n"
