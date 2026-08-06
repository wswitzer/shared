from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import tomllib

from .privacy import PrivacyRules


@dataclass
class Config:
    data_dir: Path = Path("~/.local/share/computer-memory").expanduser()
    repo_roots: list[Path] = field(default_factory=lambda: [Path("~/Projects").expanduser()])
    git_max_depth: int = 3
    screenpipe_enabled: bool = True
    screenpipe_url: str = "http://localhost:3030"
    screenpipe_minutes: int = 120
    llm_base_url: str | None = None
    llm_model: str | None = None
    privacy: PrivacyRules = field(default_factory=PrivacyRules.defaults)


def load_config(path: str | Path | None = None) -> Config:
    if path is None:
        env = os.environ.get("COMPUTER_MEMORY_CONFIG")
        path = Path(env).expanduser() if env else Path("~/.config/computer-memory/config.toml").expanduser()
    else:
        path = Path(path).expanduser()
    cfg = Config()
    if not path.exists():
        return cfg
    data = tomllib.loads(path.read_text())
    cfg.data_dir = Path(data.get("data_dir", str(cfg.data_dir))).expanduser()
    git = data.get("git", {})
    cfg.repo_roots = [Path(x).expanduser() for x in git.get("roots", [str(x) for x in cfg.repo_roots])]
    cfg.git_max_depth = int(git.get("max_depth", cfg.git_max_depth))
    sp = data.get("screenpipe", {})
    cfg.screenpipe_enabled = bool(sp.get("enabled", cfg.screenpipe_enabled))
    cfg.screenpipe_url = str(sp.get("url", cfg.screenpipe_url))
    cfg.screenpipe_minutes = int(sp.get("minutes", cfg.screenpipe_minutes))
    llm = data.get("llm", {})
    cfg.llm_base_url = llm.get("base_url")
    cfg.llm_model = llm.get("model")
    p = data.get("privacy", {})
    defaults = PrivacyRules.defaults()
    cfg.privacy = PrivacyRules(
        excluded_app_patterns=list(p.get("excluded_app_patterns", defaults.excluded_app_patterns)),
        excluded_url_patterns=list(p.get("excluded_url_patterns", defaults.excluded_url_patterns)),
        redact_patterns=list(p.get("redact_patterns", defaults.redact_patterns)),
    )
    return cfg
