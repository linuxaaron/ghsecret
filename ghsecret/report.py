"""Berichtsformatierung für CLI und JSON."""

from __future__ import annotations

import json
from dataclasses import asdict

from .models import Finding


def render_text(findings: list[Finding], target: str) -> str:
    lines = [f"ghsecret – Scan: {target}", "=" * 72, f"Treffer: {len(findings)}", ""]
    if not findings:
        lines.append("Keine potenziellen Secrets gefunden.")
        return "\n".join(lines)
    for idx, finding in enumerate(findings, 1):
        lines.extend(
            [
                f"[{finding.severity.upper()}] {finding.secret_type}",
                f"  Datei:         {finding.path}",
                f"  Zeile:         {finding.line}",
                f"  Quelle:        {finding.source}",
                f"  Vertrauen:     {finding.confidence}%",
                f"  Vorschau:      {finding.preview}",
                f"  Fingerabdruck: {finding.fingerprint}",
            ]
        )
        if idx != len(findings):
            lines.append("")
    return "\n".join(lines)


def render_json(findings: list[Finding], target: str) -> str:
    payload = {
        "tool": "ghsecret",
        "version": "0.1.0",
        "ziel": target,
        "treffer": len(findings),
        "fundstellen": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
