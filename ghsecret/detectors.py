"""Regelbasiertes Secret-Scanning mit konservativen Filtern."""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

from .models import Finding


@dataclass(frozen=True, slots=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    severity: str
    base_confidence: int


RULES = (
    Rule("GitHub Token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{20,255})\b"), "kritisch", 98),
    Rule("AWS Access Key", re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), "hoch", 97),
    Rule("Google API Key", re.compile(r"\b(AIza[0-9A-Za-z_-]{30,})\b"), "hoch", 94),
    Rule("Stripe Secret Key", re.compile(r"\b(sk_(?:live|test)_[0-9A-Za-z]{16,})\b"), "kritisch", 98),
    Rule("SendGrid API Key", re.compile(r"\b(SG\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,})\b"), "hoch", 96),
    Rule("Slack Token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"), "hoch", 96),
    Rule("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "mittel", 88),
    Rule("Privater Schlüssel", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "kritisch", 99),
)

GENERIC = re.compile(
    r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|client[_-]?secret)"
    r"\s*[:=]\s*[\"']?([A-Za-z0-9_./+=:-]{16,})[\"']?"
)
PLACEHOLDERS = {
    "changeme", "change-me", "example", "sample", "placeholder", "your_api_key",
    "your-api-key", "your_secret", "your-secret", "dummy", "test", "testing",
}


def entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def looks_like_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in PLACEHOLDERS:
        return True
    return any(token in normalized for token in ("<your", "replace_me", "replace-me", "example.com"))


def mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * min(24, len(value) - 8)}{value[-4:]}"


def _finding(rule_name: str, severity: str, confidence: int, path: str, line_no: int, source: str, value: str) -> Finding:
    fingerprint = hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()
    return Finding(rule_name, severity, max(0, min(100, confidence)), path, line_no, source, fingerprint, mask(value))


def scan_text(text: str, path: str = "<text>", source: str = "arbeitsbaum") -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        for rule in RULES:
            for match in rule.pattern.finditer(line):
                value = match.group(1) if match.lastindex else match.group(0)
                key = (rule.name, line_no, value)
                if key not in seen:
                    findings.append(_finding(rule.name, rule.severity, rule.base_confidence, path, line_no, source, value))
                    seen.add(key)
        for match in GENERIC.finditer(line):
            value = match.group(2)
            if looks_like_placeholder(value):
                continue
            confidence = 78 + min(15, int(max(0.0, entropy(value) - 2.5) * 4))
            key = (match.group(1).lower(), line_no, value)
            if key not in seen:
                findings.append(_finding(f"Generisches Secret ({match.group(1)})", "mittel", confidence, path, line_no, source, value))
                seen.add(key)
    return findings
