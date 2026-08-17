from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from typing import Any, Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Evidence


class JsonTransport(Protocol):
    def get_json(self, url: str, timeout: float): ...


class UrllibTransport:
    def get_json(self, url: str, timeout: float):
        with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))


class ScreenpipeClient:
    def __init__(self, base_url: str = "http://localhost:3030", transport: JsonTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.transport = transport or UrllibTransport()

    def health(self) -> dict[str, Any]:
        return self.transport.get_json(f"{self.base_url}/health", timeout=3)

    def search(self, *, start_time: str, end_time: str, limit: int = 200) -> list[Evidence]:
        query = urlencode({"content_type": "all", "start_time": start_time, "end_time": end_time, "limit": limit})
        payload = self.transport.get_json(f"{self.base_url}/search?{query}", timeout=10)
        out: list[Evidence] = []
        for item in payload.get("data", []):
            content = item.get("content") or item
            kind = str(item.get("type") or content.get("type") or "unknown").lower()
            timestamp = content.get("timestamp") or item.get("timestamp")
            if not timestamp:
                continue
            text = content.get("text") or content.get("transcription") or ""
            attrs = {k: content.get(k) for k in ("app_name", "window_name", "browser_url", "speaker_id", "device_name", "device_type", "focused") if content.get(k) is not None}
            out.append(Evidence(source=f"screenpipe:{kind}", observed_at=datetime.fromisoformat(str(timestamp).replace("Z", "+00:00")), text=str(text), attributes=attrs))
        return out

    def search_recent(self, minutes: int) -> list[Evidence]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=minutes)
        return self.search(start_time=start.isoformat().replace("+00:00", "Z"), end_time=end.isoformat().replace("+00:00", "Z"))
