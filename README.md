# ghsecret 🔐

**Cross-Platform Security-Scanner zur Erkennung potenziell veröffentlichter Secrets in Git-Repositories.**

`ghsecret` ist ein schlanker CLI-Scanner für Entwickler, Security-Teams und Researcher. Das Tool untersucht lokale Git-Repositories sowie öffentliche GitHub-Repositories auf versehentlich veröffentlichte API-Keys, Tokens, Zugangsdaten, private Schlüssel und andere verdächtige Geheimnisse.

Der Fokus liegt auf **Erkennung, sicherer Ausgabe und Responsible Disclosure** – nicht auf der Verwendung oder Ausnutzung gefundener Zugangsdaten.

## ✨ Funktionen

- 🔎 Lokale Verzeichnisse und Git-Repositories scannen
- 🌐 Öffentliche GitHub-Repositories direkt per URL untersuchen
- 🕘 Optional die Git-Historie nach entfernten Secrets durchsuchen
- 🔑 Typische API-Keys und Tokens erkennen
- 🔐 Private Schlüssel und JWTs erkennen
- 🧩 Generische Secrets anhand von Schlüsselwörtern und Kontext erkennen
- 📊 Entropieprüfung zur Reduzierung von Fehlalarmen
- 🎯 Confidence Score und Schweregrad für Treffer
- 🛡️ Erkannte Secrets niemals im Klartext ausgeben
- #️⃣ Fingerprints statt tatsächlicher Secret-Werte verwenden
- 📄 Text- und JSON-Ausgabe für Menschen und Automatisierung
- ⚙️ Geeignete Exit-Codes für CI/CD
- 💻 Windows, macOS und Linux
- 🐍 Python 3.10+
- 🚫 Keine Credentials im Quellcode erforderlich

## 🚀 Installation

### Voraussetzungen

- Python **3.10 oder neuer**
- Git für Remote- und History-Scans

Repository klonen und installieren:

```bash
git clone https://github.com/linuxaaron/ghsecret.git
cd ghsecret
python -m pip install -e .
```

Optional für die Entwicklung inklusive Tests:

```bash
python -m pip install -e ".[dev]"
```

## 🧪 Verwendung

### Lokales Projekt scannen

```bash
ghsecret scan ./mein-projekt
```

### Öffentliches GitHub-Repository scannen

```bash
ghsecret scan https://github.com/owner/repository
```

### Git-Historie untersuchen

Mit `--history` werden auch ältere Commits berücksichtigt. Dadurch können Secrets gefunden werden, die zwar aus aktuellen Dateien entfernt wurden, aber noch in der Git-Historie vorhanden sind.

```bash
ghsecret scan https://github.com/owner/repository --history
```

### JSON-Ausgabe

Für Skripte, CI/CD-Pipelines oder weitere automatisierte Verarbeitung:

```bash
ghsecret scan ./mein-projekt --format json
```

### Hilfe anzeigen

```bash
ghsecret --help
ghsecret scan --help
```

## 📋 Beispielausgabe

Ein Treffer wird bewusst maskiert dargestellt:

```text
[CRITICAL] GitHub Token
Datei: config/settings.py
Zeile: 42
Commit: 91ac7f...
Confidence: 98%
Fingerprint: sha256:7c2e...

Empfehlung:
Credential widerrufen/rotieren und aus der Git-Historie entfernen.
```

Das tatsächliche Secret wird **nicht ausgegeben**.

## 📊 Schweregrade

| Schweregrad | Bedeutung |
|---|---|
| `CRITICAL` | Sehr wahrscheinlich ein aktiv nutzbares Credential oder besonders sensibles Secret |
| `HIGH` | Stark verdächtiger Schlüssel, Token oder Zugangsdatenfund |
| `MEDIUM` | Potenzielles Secret mit mittlerer Erkennungssicherheit |
| `LOW` | Verdächtiger Wert mit niedrigerer Confidence |

Ein Treffer ist grundsätzlich ein **Verdacht**, keine automatische Bestätigung eines gültigen Credentials.

## 🔢 Exit-Codes

| Code | Bedeutung |
|---:|---|
| `0` | Scan erfolgreich, keine Treffer |
| `1` | Scan erfolgreich, mindestens ein potenzielles Secret gefunden |
| `2` | Fehler bei Eingabe, Repository oder Ausführung |

Damit kann `ghsecret` beispielsweise direkt in CI/CD verwendet werden:

```bash
ghsecret scan .
```

Ein gefundener Treffer führt zu Exit-Code `1`.

## 🛡️ Sicherheitskonzept

`ghsecret` wurde für defensive Sicherheitsprüfungen entwickelt.

Das Tool:

- verwendet gefundene Credentials **nicht**
- versucht keine Anmeldung bei externen Diensten
- führt keine Exploitation durch
- gibt erkannte Secrets nicht im Klartext aus
- benötigt keine fremden Zugangsdaten für öffentliche Repository-Scans

Die Untersuchung eines fremden öffentlichen Repositorys sollte ausschließlich im Rahmen geltender Gesetze, Plattformregeln und verantwortungsvoller Security-Praxis erfolgen.

## 📜 Responsible Disclosure

Wenn ein potenzielles Secret in einem fremden Repository gefunden wird:

1. **Credential nicht verwenden oder testen.**
2. Den Fund dokumentieren, ohne den geheimen Wert weiterzugeben.
3. Einen offiziellen Security-Kanal oder privaten Kontakt des Betreibers verwenden.
4. Repository, Datei, Commit und ungefähre Fundstelle nennen.
5. Dem Betreiber empfehlen, das Credential zu widerrufen bzw. zu rotieren.
6. Bei Bedarf die Entfernung aus der Git-Historie empfehlen.

Ein möglicher Meldungstext:

> Bei einer automatisierten Sicherheitsprüfung wurde in Ihrem öffentlichen Repository ein potenziell exponiertes Credential gefunden. Der geheime Wert wurde nicht verwendet oder verifiziert. Bitte prüfen Sie den Fund, widerrufen bzw. rotieren Sie das Credential und entfernen Sie es gegebenenfalls aus der Git-Historie.

## 🧪 Entwicklung und Tests

Tests ausführen:

```bash
python -m unittest discover -s tests -v
```

Die GitHub-Actions prüfen das Projekt automatisiert auf mehreren Python-Versionen sowie unter Linux, Windows und macOS.

Vor einem Release sollte mindestens Folgendes geprüft werden:

```bash
python -m unittest discover -s tests -v
ghsecret --help
ghsecret scan .
```

## 🏗️ Projektstruktur

```text
ghsecret/
├── ghsecret/          # Scanner und CLI
├── rules/              # Erkennungsregeln
├── tests/              # Automatisierte Tests
├── .github/workflows/  # CI/CD
├── SECURITY.md         # Sicherheitsrichtlinie
├── LICENSE             # MIT-Lizenz
└── README.md
```

## ⚠️ Grenzen der Erkennung

Kein Secret-Scanner kann eine vollständige Erkennung garantieren. `ghsecret` kann sowohl Fehlalarme als auch übersehene Secrets produzieren.

Besonders wichtig:

- Ein gefundener Wert muss nicht gültig oder aktiv sein.
- Ein entferntes Secret kann weiterhin in Git-Objekten vorhanden sein.
- Individuelle Secret-Formate können zusätzliche Regeln benötigen.
- Binärdateien und ungewöhnlich gespeicherte Daten können außerhalb des Erkennungsumfangs liegen.

Für produktive Umgebungen sollte `ghsecret` daher als **zusätzliche Schutzschicht** und nicht als alleinige Secret-Management-Lösung eingesetzt werden.

## 📄 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**.

## 👤 Autor

**Joscha Aaron Schmidt**

Security Research · IT · Datenanalyse

GitHub: https://github.com/linuxaaron

---

> **Ziel von ghsecret:** Secrets erkennen, bevor sie zum Sicherheitsproblem werden – und Security-Funde verantwortungsvoll behandeln.