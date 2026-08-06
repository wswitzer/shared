from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from .collectors import BrowserCollector, GitCollector, MacOSAppCollector
from .config import load_config
from .handoff import render_handoff
from .llm import OpenAICompatibleClient
from .privacy import PrivacyFilter
from .screenpipe import ScreenpipeClient
from .service import SnapshotService
from .storage import SnapshotStore


def build_service(config):
    store = SnapshotStore(config.data_dir / "memory.db")
    screenpipe = ScreenpipeClient(config.screenpipe_url) if config.screenpipe_enabled else None
    return SnapshotService(
        store=store,
        privacy_filter=PrivacyFilter(config.privacy),
        app_collector=MacOSAppCollector(),
        browser_collector=BrowserCollector(),
        git_collector=GitCollector(config.repo_roots, max_depth=config.git_max_depth),
        screenpipe=screenpipe,
    )


def _write_handoff(config, text: str, captured_at) -> Path:
    out_dir = config.data_dir / "handoffs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{captured_at.astimezone().strftime('%Y-%m-%d')}.md"
    path.write_text(text)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="computer-memory")
    parser.add_argument("--config", help="TOML config path")
    sub = parser.add_subparsers(dest="command", required=True)
    snap_p = sub.add_parser("snapshot", help="Capture and persist current computer state")
    snap_p.add_argument("--json", action="store_true")
    sub.add_parser("latest", help="Print the latest snapshot JSON")
    hand_p = sub.add_parser("handoff", help="Generate a morning handoff from the latest snapshot")
    hand_p.add_argument("--local-llm", action="store_true", help="Use configured OpenAI-compatible local model")
    sub.add_parser("doctor", help="Check local prerequisites")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    store = SnapshotStore(config.data_dir / "memory.db")

    if args.command == "doctor":
        checks = {"macOS osascript": shutil.which("osascript") is not None, "git": shutil.which("git") is not None}
        if config.screenpipe_enabled:
            try:
                ScreenpipeClient(config.screenpipe_url).health()
                checks["screenpipe"] = True
            except Exception:
                checks["screenpipe"] = False
        for name, ok in checks.items():
            print(f"{'OK' if ok else 'MISSING'}  {name}")
        return 0 if all(checks.values()) else 1

    if args.command == "snapshot":
        snap = build_service(config).capture(screenpipe_minutes=config.screenpipe_minutes)
        print(snap.to_json() if args.json else f"Captured {snap.captured_at.isoformat()} — {len(snap.apps)} apps, {len(snap.tabs)} tabs, {len(snap.repos)} repos, {len(snap.evidence)} evidence items")
        return 0

    latest = store.latest()
    if latest is None:
        print("No snapshots yet. Run: computer-memory snapshot", file=sys.stderr)
        return 2
    if args.command == "latest":
        print(json.dumps(latest.to_dict(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "handoff":
        deterministic = render_handoff(latest)
        text = deterministic
        if args.local_llm:
            if not config.llm_base_url or not config.llm_model:
                print("Configure [llm] base_url and model first.", file=sys.stderr)
                return 2
            text = OpenAICompatibleClient(base_url=config.llm_base_url, model=config.llm_model).summarize(deterministic)
        path = _write_handoff(config, text, latest.captured_at)
        print(path)
        return 0
    return 1
