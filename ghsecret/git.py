"""Git-History-Unterstützung für defensive Secret-Scans."""

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


def _history_patches(repo: Path) -> list[tuple[str, str]]:
    """Liefert nur hinzugefügte Zeilen aus der erreichbaren Git-Historie."""
    output = _run_git(
        repo,
        "log",
        "--all",
        "--format=__GHSECRET_COMMIT__%H",
        "--patch",
        "--no-ext-diff",
        "--unified=0",
    )
    current_commit = "unbekannt"
    current_path = "<patch>"
    result: list[tuple[str, str]] = []
    for line in output.splitlines():
        if line.startswith("__GHSECRET_COMMIT__"):
            current_commit = line.removeprefix("__GHSECRET_COMMIT__")[:40]
            current_path = "<patch>"
        elif line.startswith("+++ b/"):
            current_path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            result.append((current_commit, f"{current_path}: {line[1:]}"))
    return result


def scan_git_history(path: str | Path) -> list[Finding]:
    repo = Path(path).expanduser().resolve()
    if not is_git_repository(repo):
        raise ValueError(f"Kein Git-Repository: {repo}")

    findings: list[Finding] = []
    seen: set[tuple[str, str, int, str]] = set()
    for commit, item in _history_patches(repo):
        relative, line = item.split(": ", 1)
        for finding in scan_text(line, relative, f"commit:{commit[:12]}"):
            key = (commit, relative, finding.line, finding.fingerprint)
            if key not in seen:
                findings.append(finding)
                seen.add(key)
    return findings
