"""Kommandozeilenschnittstelle von ghsecret."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from .git import scan_git_history
from .report import render_json, render_text
from .scanner import scan_directory

GITHUB_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")


def _clone(url: str) -> Path:
    match = GITHUB_RE.fullmatch(url)
    if not match:
        raise ValueError("Nur öffentliche GitHub-Repository-URLs im Format https://github.com/owner/repo werden akzeptiert.")
    tmp = Path(tempfile.mkdtemp(prefix="ghsecret-"))
    target = tmp / "repo"
    result = subprocess.run(
        ["git", "clone", "--quiet", "--filter=blob:none", "--no-tags", "--depth", "1", url, str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(result.stderr.strip() or "Git-Clone fehlgeschlagen.")
    return target


def _scan_target(target: str, history: bool) -> tuple[str, list]:
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        repo = _clone(target)
        try:
            findings = scan_git_history(repo) if history else scan_directory(repo)
            return target, findings
        finally:
            shutil.rmtree(repo.parent, ignore_errors=True)
    path = Path(target).expanduser().resolve()
    findings = scan_git_history(path) if history else scan_directory(path)
    return str(path), findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ghsecret", description="Deutscher Security-Scanner für potenziell veröffentlichte Secrets in Git-Repositories.")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Repository oder lokalen Ordner untersuchen")
    scan.add_argument("ziel", help="GitHub-URL oder lokaler Repository-/Ordnerpfad")
    scan.add_argument("--history", action="store_true", help="Zusätzlich die erreichbare Git-Historie untersuchen")
    scan.add_argument("--format", choices=("text", "json"), default="text", help="Ausgabeformat")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        try:
            target, findings = _scan_target(args.ziel, args.history)
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 2
        print(render_json(findings, target) if args.format == "json" else render_text(findings, target))
        return 1 if findings else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
