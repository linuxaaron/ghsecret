"""Git-History-Unterstützung ohne Ausführung gefundener Credentials."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .detectors import scan_text
from .models import Finding


def _run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def is_git_repository(path: str | Path) -> bool:
    repo = Path(path).expanduser().resolve()
    try:
        _run_git(repo, "rev-parse", "--git-dir")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def scan_git_history(path: str | Path) -> list[Finding]:
    repo = Path(path).expanduser().resolve()
    if not is_git_repository(repo):
        raise ValueError(f"Kein Git-Repository: {repo}")

    commits = _run_git(repo, "rev-list", "--all").splitlines()
    findings: list[Finding] = []
    seen: set[tuple[str, str, int, str]] = set()

    for commit in commits:
        try:
            changed = _run_git(repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        except subprocess.CalledProcessError:
            continue
        for rel in changed:
            if not rel:
                continue
            try:
                text = _run_git(repo, "show", f"{commit}:{rel}")
            except subprocess.CalledProcessError:
                continue
            for finding in scan_text(text, rel, f"commit:{commit[:12]}"):
                key = (commit, rel, finding.line, finding.fingerprint)
                if key not in seen:
                    findings.append(finding)
                    seen.add(key)
    return findings
