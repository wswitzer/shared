"""Optional MCP facade. Install with: pip install -e '.[mcp]'"""
from __future__ import annotations

from .config import load_config
from .handoff import render_handoff
from .storage import SnapshotStore


def create_server(config_path: str | None = None):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("MCP support is optional. Install computer-memory[mcp].") from exc

    config = load_config(config_path)
    store = SnapshotStore(config.data_dir / "memory.db")
    mcp = FastMCP("computer-memory")

    @mcp.tool()
    def latest_state() -> str:
        """Return the most recent evidence-backed computer snapshot as JSON."""
        snap = store.latest()
        return snap.to_json() if snap else '{"error":"no snapshots"}'

    @mcp.tool()
    def latest_handoff() -> str:
        """Return a human-readable handoff derived from the latest snapshot."""
        snap = store.latest()
        return render_handoff(snap) if snap else "No snapshots yet."

    @mcp.tool()
    def recent_snapshots(limit: int = 5) -> str:
        """Return recent snapshots as newline-delimited JSON."""
        return "\n".join(s.to_json() for s in store.list(limit=max(1, min(limit, 50))))

    return mcp


def main():
    create_server().run()


if __name__ == "__main__":
    main()
