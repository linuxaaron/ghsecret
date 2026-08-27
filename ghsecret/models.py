"""Datenmodelle für Scanner-Funde."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Finding:
    """Ein potenzieller Secret-Fund ohne Klartextwert."""

    secret_type: str
    severity: str
    confidence: int
    path: str
    line: int
    source: str
    fingerprint: str
    preview: str

    def to_dict(self) -> dict[str, object]:
        return {
            "typ": self.secret_type,
            "schweregrad": self.severity,
            "vertrauen": self.confidence,
            "datei": self.path,
            "zeile": self.line,
            "quelle": self.source,
            "fingerabdruck": self.fingerprint,
            "vorschau": self.preview,
        }
