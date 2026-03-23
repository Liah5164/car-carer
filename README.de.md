# Car Carer

> [English](README.md) | [Francais](README.fr.md) | **Deutsch** | [Espanol](README.es.md)

**Ihr KI-gestuetzter Begleiter fuer die Fahrzeugwartung**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-willkommen-brightgreen.svg)](https://github.com/Greal-dev/car-carer/pulls)

---

## Was ist Car Carer?

Car Carer ist eine selbst gehostete Webanwendung zur Verfolgung der Fahrzeugwartung. Laden Sie Rechnungen, Kostenvoranschlaege und TUEV-Berichte hoch (PDF oder Foto) -- die KI extrahiert automatisch strukturierte Daten daraus. Ein intelligenter Chat-Assistent hilft Ihnen anschliessend, die vollstaendige Wartungshistorie Ihres Fahrzeugs zu verstehen, Kosten zu analysieren und anstehende Wartungen im Blick zu behalten.

---

## Funktionen

- :page_facing_up: **KI-Dokumentenextraktion** -- Gemini Flash 2.0 ueber OpenRouter erkennt Rechnungen, Kostenvoranschlaege und TUEV-Berichte automatisch und extrahiert strukturierte Daten (Datum, Kilometerstand, Einzelposten, Maengel, Kosten)
- :robot: **Intelligenter Chat-Assistent** -- Claude Sonnet 4 mit 6 spezialisierten Werkzeugen: Fahrzeuginfo, Wartungssuche, TUEV-Berichte, TUEV-Vergleich, Kilometerchronologie und Ausgabenuebersicht
- :car: **Multi-Fahrzeug-Verwaltung** -- Verwalten Sie beliebig viele Fahrzeuge mit berechneten Statistiken (Gesamtausgaben, letzter Kilometerstand, Dokumentenanzahl)
- :zap: **Batch-Upload** -- Laden Sie 50+ Dokumente gleichzeitig hoch mit Echtzeit-Fortschrittsanzeige via Server-Sent Events (8 parallele Extraktionen)
- :sparkles: **Automatische Fahrzeuganreicherung** -- Marke, Modell, Kennzeichen, Baujahr, FIN und Kraftstoffart werden automatisch aus hochgeladenen Dokumenten befuellt
- :bell: **Wartungserinnerungen und Warnungen** -- Der Chat-Assistent erkennt ueberfaellige Wartungen und auffaellige Muster in Ihren TUEV-Berichten
- :iphone: **PWA: auf Mobilgeraeten installierbar** -- Funktioniert als Progressive Web App mit Kameraaufnahme (Rueckkamera) fuer schnelles Abfotografieren von Belegen
- :hammer_and_wrench: **Kein Build-Schritt** -- Das Frontend basiert auf Alpine.js und Tailwind CSS via CDN -- einfach starten und loslegen

---

## Screenshots

| Dashboard | Dokumenten-Upload |
|:---------:|:-----------------:|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Upload](docs/screenshots/upload.png) |

| KI-Chat | Kraftstoffverbrauch |
|:-------:|:-------------------:|
| ![Chat](docs/screenshots/chat.png) | ![Kraftstoff](docs/screenshots/fuel.png) |

| Steuern & Versicherung | Fahrzeug teilen |
|:-----------------------:|:---------------:|
| ![Steuern](docs/screenshots/taxes.png) | ![Teilen](docs/screenshots/sharing.png) |

---

## Schnellstart

### 1. Repository klonen

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd care-of-your-car
```

### 2. Python-Abhaengigkeiten installieren

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# oder: venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Oeffnen Sie `.env` und tragen Sie Ihre API-Schluessel ein:

```env
ANTHROPIC_API_KEY=sk-ant-ihr-schluessel-hier
OPENROUTER_API_KEY=sk-or-v1-ihr-schluessel-hier
```

### 4. Anwendung starten

```bash
python run.py
```

Die Anwendung ist nun unter **http://localhost:8200** erreichbar.

> Die SQLite-Datenbank (`care.db`) und das Upload-Verzeichnis (`uploads/`) werden beim ersten Start automatisch erstellt.

### 5. Loslegen

1. Oeffnen Sie http://localhost:8200 im Browser
2. Legen Sie ein Fahrzeug an (nur der Name ist erforderlich)
3. Laden Sie Ihre erste Rechnung oder Ihren TUEV-Bericht hoch
4. Die KI extrahiert automatisch alle relevanten Daten
5. Nutzen Sie den Chat, um Fragen zu Ihrem Fahrzeug zu stellen

---

## Konfiguration

Alle Einstellungen werden ueber die Datei `.env` gesteuert (siehe `.env.example`):

| Variable | Erforderlich | Standardwert | Beschreibung |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Ja | -- | API-Schluessel fuer Anthropic (Claude Chat-Assistent) |
| `OPENROUTER_API_KEY` | Ja | -- | API-Schluessel fuer OpenRouter (Gemini Dokumentenextraktion) |
| `DATABASE_URL` | Nein | `sqlite:///./care.db` | Datenbankverbindungs-URL |
| `UPLOAD_DIR` | Nein | `./uploads` | Verzeichnis fuer hochgeladene Dateien |
| `JWT_EXPIRE_HOURS` | Nein | `72` | Gueltigkeitsdauer der JWT-Tokens in Stunden |
| `BATCH_MAX_CONCURRENT` | Nein | `3` | Maximale gleichzeitige Batch-Extraktionen |
| `BATCH_MAX_FILES` | Nein | `100` | Maximale Anzahl Dateien pro Batch-Upload |
| `EXTRACTION_TIMEOUT` | Nein | `60` | Timeout fuer die Dokumentenextraktion in Sekunden |
| `EXTRACTION_MODEL` | Nein | `google/gemini-2.5-flash` | Modell fuer die Dokumentenextraktion |
| `MAX_PHOTO_SIZE_MB` | Nein | `10` | Maximale Fotodateigroesse in MB |

---

## Tech-Stack

| Schicht | Technologie | Version |
|---|---|---|
| Backend | FastAPI + Uvicorn | 0.115.6 / 0.34.0 |
| Datenbank | SQLite + SQLAlchemy (synchron) | 2.0.36 |
| LLM Chat | Claude Sonnet 4 (Anthropic SDK) | anthropic 0.44.0 |
| LLM Extraktion | Gemini Flash 2.0 (OpenRouter) | httpx 0.28+ |
| PDF-Verarbeitung | PyMuPDF (fitz) | 1.25.3 |
| Bildverarbeitung | Pillow | 11.1.0 |
| Frontend | Alpine.js 3 + Tailwind CSS (CDN) | kein Build-Schritt |
| Runtime | Python | 3.12+ |

---

## Projektstruktur

```
care-of-your-car/
├── run.py                    # Einstiegspunkt (Uvicorn-Server)
├── .env                      # API-Schluessel (gitignored)
├── .env.example              # Vorlage fuer Umgebungsvariablen
├── requirements.txt          # Python-Abhaengigkeiten
├── care.db                   # SQLite-Datenbank (automatisch erstellt)
├── uploads/                  # Hochgeladene Dateien (automatisch erstellt)
├── tests/                    # Testdateien
├── app/
│   ├── main.py               # FastAPI-App, Routenmontage
│   ├── config.py             # Einstellungen aus .env (pydantic-settings)
│   ├── database.py           # SQLAlchemy Engine und Session
│   ├── models/               # Datenbankmodelle (8 Tabellen)
│   │   ├── vehicle.py        # Fahrzeug
│   │   ├── document.py       # Dokument
│   │   ├── maintenance.py    # Wartungsereignis + Einzelposten
│   │   ├── ct_report.py      # TUEV-Bericht + Maengel
│   │   └── conversation.py   # Konversation + Nachrichten
│   ├── schemas/              # Pydantic-Validierungsschemas
│   ├── routers/              # API-Endpunkte
│   │   ├── vehicles.py       # CRUD Fahrzeuge + berechnete Statistiken
│   │   ├── documents.py      # Upload, Batch, SSE, Extraktion
│   │   └── chat.py           # Chat-Nachrichten und Konversationen
│   ├── services/             # Geschaeftslogik
│   │   ├── extraction.py     # Gemini-Pipeline: PDF/Bild -> Daten
│   │   └── agent.py          # Claude Agentic Loop mit Werkzeugen
│   ├── agent/                # Chat-Agent-Konfiguration
│   │   ├── prompts.py        # System-Prompt
│   │   └── tools.py          # 6 Werkzeuge + Dispatcher
│   └── static/               # Frontend (SPA)
│       ├── index.html        # Alpine.js Single-Page-App
│       ├── manifest.json     # PWA-Manifest
│       ├── sw.js             # Service Worker
│       ├── css/style.css     # Zusaetzliche Styles
│       ├── js/app.js         # Alpine.js Anwendungslogik
│       └── icons/            # PWA-Icons (192x192, 512x512)
```

---

## API-Dokumentation

Die interaktive API-Dokumentation ist nach dem Start der Anwendung verfuegbar unter:

- **Swagger UI**: http://localhost:8200/docs
- **ReDoc**: http://localhost:8200/redoc

### Wichtige Endpunkte

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/api/vehicles` | Alle Fahrzeuge mit Statistiken auflisten |
| `POST` | `/api/vehicles` | Neues Fahrzeug anlegen |
| `POST` | `/api/documents/upload` | Einzelnes Dokument hochladen und extrahieren |
| `POST` | `/api/documents/batch-upload` | Batch-Upload (mehrere Dateien) |
| `GET` | `/api/documents/batch-status/{id}` | Batch-Fortschritt via SSE |
| `POST` | `/api/chat` | Nachricht an den Chat-Assistenten senden |
| `GET` | `/api/chat/conversations` | Konversationen auflisten |

---

## Mitwirken

Beitraege sind herzlich willkommen! So koennen Sie mitmachen:

1. **Fork** erstellen
2. **Feature-Branch** anlegen (`git checkout -b feature/meine-funktion`)
3. **Aenderungen committen** (`git commit -m 'Neue Funktion hinzufuegen'`)
4. **Branch pushen** (`git push origin feature/meine-funktion`)
5. **Pull Request** oeffnen

### Richtlinien

- Halten Sie den Code sauber und gut dokumentiert
- Schreiben Sie Tests fuer neue Funktionen
- Folgen Sie dem bestehenden Code-Stil
- Aktualisieren Sie die Dokumentation bei Bedarf

### Fehler melden

Haben Sie einen Fehler gefunden oder eine Idee fuer eine Verbesserung? Eroeffnen Sie gerne ein [Issue](https://github.com/Greal-dev/car-carer/issues).

---

## Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

---

## Danksagungen

Dieses Projekt wurde entwickelt mit:

- **[Claude](https://www.anthropic.com/)** (Anthropic) -- Intelligenter Chat-Assistent und Entwicklungsunterstuetzung
- **[Gemini](https://deepmind.google/technologies/gemini/)** (Google) ueber [OpenRouter](https://openrouter.ai/) -- KI-gestuetzte Dokumentenextraktion
- **[FastAPI](https://fastapi.tiangolo.com/)** -- Modernes, schnelles Python-Web-Framework
- **[Alpine.js](https://alpinejs.dev/)** + **[Tailwind CSS](https://tailwindcss.com/)** -- Leichtgewichtiges Frontend ohne Build-Schritt
