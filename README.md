# ghsecret

**Cross-Platform Security-Scanner zur Erkennung potenziell veröffentlichter Secrets in Git-Repositories.**

`ghsecret` untersucht lokale Git-Repositories oder öffentliche GitHub-Repositories auf API-Keys, Tokens, Zugangsdaten, private Schlüssel und andere verdächtige Geheimnisse. Optional kann auch die erreichbare Git-Historie untersucht werden.

## Funktionen

- Scannen lokaler Verzeichnisse und Git-Repositories
- Scannen öffentlicher GitHub-Repositories per URL
- optionaler Scan der Git-Historie
- Erkennung typischer API-Keys und Tokens
- Erkennung privater Schlüssel und JWTs
- generische Secret-Erkennung mit Kontextanalyse
- Entropieprüfung zur Reduzierung von Fehlalarmen
- Confidence Score und Schweregrad
- Secrets werden in der Ausgabe niemals im Klartext angezeigt
- Fingerprints statt echter Secret-Werte
- Text- und JSON-Ausgabe
- geeignete Exit-Codes für CI/CD
- keine Credentials im Quellcode erforderlich
- Windows, macOS und Linux

## Installation

Voraussetzungen:

- Python 3.10 oder neuer
- Git für Remote- und History-Scans

Repository klonen und Paket installieren:

```bash
git clone https://github.com/linuxaaron/ghsecret.git
cd ghsecret
python -m pip install -e .
```

## Verwendung

Lokales Verzeichnis scannen:

```bash
ghsecret scan ./mein-projekt
```

Öffentliches GitHub-Repository scannen:

```bash
ghsecret scan https://github.com/owner/repository
```

Zusätzlich die Git-Historie untersuchen:

```bash
ghsecret scan https://github.com/owner/repository --history
```

JSON für Automatisierung oder CI:

```bash
ghsecret scan ./mein-projekt --format json
```

Hilfe:

```bash
ghsecret --help
ghsecret scan --help
```

## Exit-Codes

| Code | Bedeutung |
|---:|---|
| `0` | Scan erfolgreich, keine Treffer |
| `1` | Scan erfolgreich, mindestens ein potenzielles Secret gefunden |
| `2` | Fehler bei Eingabe, Repository oder Ausführung |

## Sicherheit

`ghsecret` ist für defensive Sicherheitsprüfungen und Responsible Disclosure vorgesehen. Das Tool versucht keine gefundenen Zugangsdaten zu verwenden, meldet sich nicht mit ihnen bei Diensten an und führt keine Exploitation durch.

Die Ausgabe maskiert erkannte Werte. Trotzdem sollte das Tool nicht auf Systemen oder Dateien ausgeführt werden, deren Inhalte nicht verarbeitet werden dürfen.

Ein Fund bedeutet nicht automatisch, dass ein Credential gültig oder aktiv ist. Gefundene Zugangsdaten sollten vom jeweiligen Betreiber geprüft, widerrufen bzw. rotiert und gegebenenfalls aus der Git-Historie entfernt werden.

## Entwicklung

Tests ausführen:

```bash
python -m unittest discover -s tests -v
```

Die GitHub-Actions prüfen das Projekt automatisiert auf mehreren Python-Versionen unter Linux, Windows und macOS.

## Verantwortungsvolle Meldung

Wenn bei einem fremden öffentlichen Repository ein potenzielles Secret gefunden wird, sollte der Betreiber über einen geeigneten privaten oder offiziellen Security-Kanal informiert werden. Keine Zugangsdaten verwenden oder verifizieren, sofern dafür keine ausdrückliche Berechtigung besteht.

## Lizenz

MIT
