from __future__ import annotations

import json
from typing import Protocol
from urllib.request import Request, urlopen


class PostTransport(Protocol):
    def post_json(self, url: str, payload: dict, timeout: float): ...


class UrllibPostTransport:
    def post_json(self, url: str, payload: dict, timeout: float):
        req = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))


class OpenAICompatibleClient:
    def __init__(self, *, base_url: str, model: str, transport: PostTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.transport = transport or UrllibPostTransport()

    def summarize(self, evidence_text: str) -> str:
        system = (
            "You produce a morning computer-work handoff from local evidence. "
            "Do not invent facts. Clearly separate observations from inferences, cite the evidence in plain language, "
            "surface unfinished work, and prefer concise actionable next steps."
        )
        payload = {"model": self.model, "temperature": 0.1, "messages": [{"role": "system", "content": system}, {"role": "user", "content": evidence_text}]}
        result = self.transport.post_json(f"{self.base_url}/chat/completions", payload, timeout=120)
        return result["choices"][0]["message"]["content"].strip() + "\n"
