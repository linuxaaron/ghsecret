"""Dateisystemscanner."""

from __future__ import annotations

import os
from pathlib import Path

from .detectors import scan_text
from .models import Finding

DEFAULT_IGNORES = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__"}
DEFAULT_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".7z", ".rar", ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".mov",
    ".avi", ".sqlite", ".db", ".exe", ".dll", ".so", ".dylib",
}


def _is_probably_binary(data: bytes) -> bool:
    return b"\x00" in data[:8192]


def scan_directory(root: str | os.PathLike[str], include_git_dir: bool = False) -> list[Finding]:
    base = Path(root).expanduser().resolve()
    if not base.is_dir():
        raise ValueError(f"Kein Verzeichnis: {base}")

    findings: list[Finding] = []
    ignored = set(DEFAULT_IGNORES)
    if include_git_dir:
        ignored.discard(".git")

    for current, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ignored]
        for filename in files:
            path = Path(current) / filename
            if path.suffix.lower() in DEFAULT_BINARY_EXTENSIONS:
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if _is_probably_binary(data):
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            relative = path.relative_to(base).as_posix()
            findings.extend(scan_text(text, relative, "arbeitsbaum"))
    return findings
