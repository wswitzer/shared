from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Protocol

from .models import AppState, BrowserTab, RepoState


class Runner(Protocol):
    def run(self, args: list[str], timeout: float = 10) -> str: ...


class SubprocessRunner:
    def run(self, args: list[str], timeout: float = 10) -> str:
        cp = subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout)
        return cp.stdout


APP_JXA = r'''
const se = Application('System Events');
const procs = se.applicationProcesses.whose({backgroundOnly: false})();
const result = [];
for (const p of procs) {
  let windows = [];
  try { windows = p.windows().map(w => String(w.name())); } catch (e) {}
  let pid = null; try { pid = Number(p.unixId()); } catch (e) {}
  let frontmost = false; try { frontmost = Boolean(p.frontmost()); } catch (e) {}
  result.push({name: String(p.name()), pid, frontmost, windows});
}
JSON.stringify(result);
'''


BROWSER_JXA = r'''
const out = [];
function chromeLike(name) {
  try {
    const app = Application(name);
    if (!app.running()) return;
    const wins = app.windows();
    for (let wi = 0; wi < wins.length; wi++) {
      const tabs = wins[wi].tabs();
      let activeIndex = -1;
      try { activeIndex = Number(wins[wi].activeTabIndex()) - 1; } catch (e) {}
      for (let ti = 0; ti < tabs.length; ti++) {
        out.push({browser:name, window_index:wi, tab_index:ti, active:ti===activeIndex, title:String(tabs[ti].title()), url:String(tabs[ti].url())});
      }
    }
  } catch (e) {}
}
function safari() {
  const name = 'Safari';
  try {
    const app = Application(name);
    if (!app.running()) return;
    const wins = app.windows();
    for (let wi = 0; wi < wins.length; wi++) {
      const tabs = wins[wi].tabs();
      let current = null; try { current = wins[wi].currentTab(); } catch (e) {}
      for (let ti = 0; ti < tabs.length; ti++) {
        const tab = tabs[ti];
        let active = false; try { active = current && String(tab.url()) === String(current.url()); } catch (e) {}
        out.push({browser:name, window_index:wi, tab_index:ti, active, title:String(tab.name()), url:String(tab.url())});
      }
    }
  } catch (e) {}
}
['Google Chrome','Brave Browser','Microsoft Edge','Chromium'].forEach(chromeLike);
safari();
JSON.stringify(out);
'''


class MacOSAppCollector:
    def __init__(self, runner: Runner | None = None):
        self.runner = runner or SubprocessRunner()

    def collect(self) -> list[AppState]:
        raw = self.runner.run(["osascript", "-l", "JavaScript", "-e", APP_JXA])
        return [AppState(**x) for x in json.loads(raw or "[]")]


class BrowserCollector:
    def __init__(self, runner: Runner | None = None):
        self.runner = runner or SubprocessRunner()

    def collect(self) -> list[BrowserTab]:
        raw = self.runner.run(["osascript", "-l", "JavaScript", "-e", BROWSER_JXA])
        return [BrowserTab(**x) for x in json.loads(raw or "[]")]


class GitCollector:
    SKIP = {".git", "node_modules", ".venv", "venv", "Library", ".Trash"}

    def __init__(self, roots: list[Path], max_depth: int = 3, runner: Runner | None = None):
        self.roots = [Path(x).expanduser() for x in roots]
        self.max_depth = max_depth
        self.runner = runner or SubprocessRunner()

    def _discover(self) -> list[Path]:
        found: set[Path] = set()
        for root in self.roots:
            if not root.exists() or not root.is_dir():
                continue
            if (root / ".git").exists():
                found.add(root.resolve())
            root_depth = len(root.parts)
            for path in root.rglob(".git"):
                if any(part in self.SKIP for part in path.parent.relative_to(root).parts[:-1]):
                    continue
                if len(path.parent.parts) - root_depth <= self.max_depth:
                    found.add(path.parent.resolve())
        return sorted(found)

    def _git(self, repo: Path, *args: str) -> str:
        return self.runner.run(["git", "-C", str(repo), *args], timeout=5).strip()

    def collect(self) -> list[RepoState]:
        states: list[RepoState] = []
        for repo in self._discover():
            try:
                branch = self._git(repo, "branch", "--show-current") or None
                head = self._git(repo, "rev-parse", "HEAD") or None
                status = self.runner.run(["git", "-C", str(repo), "status", "--porcelain=v1"], timeout=5)
                changed = []
                for line in status.splitlines():
                    name = line[3:] if len(line) >= 4 else line
                    if " -> " in name:
                        name = name.split(" -> ", 1)[1]
                    if name:
                        changed.append(name)
                states.append(RepoState(path=str(repo), branch=branch, head=head, dirty=bool(changed), changed_files=changed))
            except Exception:
                continue
        return states
