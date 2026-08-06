from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import re
from typing import Iterable

from .models import Snapshot


@dataclass
class PrivacyRules:
    excluded_app_patterns: list[str] = field(default_factory=list)
    excluded_url_patterns: list[str] = field(default_factory=list)
    redact_patterns: list[str] = field(default_factory=list)

    @classmethod
    def defaults(cls) -> "PrivacyRules":
        return cls(
            excluded_app_patterns=[r"(?i)^1password$", r"(?i)^passwords$", r"(?i)^keychain access$"],
            excluded_url_patterns=[r"(?i)paypal\.com", r"(?i)(^|\.)bank", r"(?i)accounts\.google\.com/signin", r"(?i)/oauth/", r"(?i)/2fa"],
            redact_patterns=[
                r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]{8,}",
                r"\bsk-[A-Za-z0-9_-]{10,}\b",
                r"(?i)([?&](?:token|access_token|api_key|apikey|key)=)[^&#\s]+",
                r"(?i)(token\s*[=:]\s*)[A-Za-z0-9._~+/=-]{8,}",
            ],
        )


class PrivacyFilter:
    def __init__(self, rules: PrivacyRules):
        self.rules = rules
        self._apps = [re.compile(x) for x in rules.excluded_app_patterns]
        self._urls = [re.compile(x) for x in rules.excluded_url_patterns]
        self._redact = [re.compile(x) for x in rules.redact_patterns]

    def _matches(self, value: str, patterns: Iterable[re.Pattern[str]]) -> bool:
        return any(p.search(value or "") for p in patterns)

    def _redact_text(self, value: str) -> str:
        out = value
        for pattern in self._redact:
            if pattern.groups:
                out = pattern.sub(lambda m: (m.group(1) if m.lastindex else "") + "[REDACTED]", out)
            else:
                out = pattern.sub("[REDACTED]", out)
        return out

    def _redact_obj(self, value):
        if isinstance(value, str):
            return self._redact_text(value)
        if isinstance(value, list):
            return [self._redact_obj(v) for v in value]
        if isinstance(value, dict):
            return {k: self._redact_obj(v) for k, v in value.items()}
        return value

    def apply(self, snapshot: Snapshot) -> Snapshot:
        snap = deepcopy(snapshot)
        snap.apps = [a for a in snap.apps if not self._matches(a.name, self._apps)]
        snap.tabs = [t for t in snap.tabs if not self._matches(t.url, self._urls)]
        snap.apps = [type(a)(name=a.name, pid=a.pid, frontmost=a.frontmost, windows=[self._redact_text(w) for w in a.windows]) for a in snap.apps]
        snap.tabs = [type(t)(browser=t.browser, window_index=t.window_index, tab_index=t.tab_index, active=t.active, title=self._redact_text(t.title), url=self._redact_text(t.url)) for t in snap.tabs]
        for item in snap.evidence:
            app_name = str(item.attributes.get("app_name", ""))
            browser_url = str(item.attributes.get("browser_url", ""))
            if self._matches(app_name, self._apps) or self._matches(browser_url, self._urls):
                item.text = "[EXCLUDED BY PRIVACY RULE]"
                item.attributes = {"excluded": True}
            else:
                item.text = self._redact_text(item.text)
                item.attributes = self._redact_obj(item.attributes)
        return snap
