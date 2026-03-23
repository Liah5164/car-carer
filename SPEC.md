# Car Carer — Specifications fonctionnelles et techniques

**Version** : 0.1.0
**Derniere mise a jour** : 2026-03-06
**Port** : 8200
**Point d'entree** : [`run.py:9`](run.py#L9) → `uvicorn app.main:app`

---

## Table des matieres

- [1. Vue d'ensemble](#1-vue-densemble)
- [2. Architecture](#2-architecture)
- [3. Modele de donnees](#3-modele-de-donnees)
- [4. API REST](#4-api-rest)
- [5. Services metier](#5-services-metier)
- [6. Agent conversationnel](#6-agent-conversationnel)
- [7. Frontend](#7-frontend)
- [8. PWA et mobile](#8-pwa-et-mobile)
- [9. Configuration et deploiement](#9-configuration-et-deploiement)
- [10. Flux utilisateur](#10-flux-utilisateur)
- [11. Carte des fichiers](#11-carte-des-fichiers)

---

## 1. Vue d'ensemble

Application locale de suivi d'entretien automobile. Importe des factures, devis et PV de controle technique (PDF ou photo), extrait automatiquement les donnees structurees, et met a disposition un chat intelligent pour interroger l'historique.

### Fonctionnalites principales

| Fonctionnalite | Description | Fichiers cles |
|---|---|---|
| Import de documents | Upload unique ou par lot (50+), PDF et images | [`app/routers/documents.py`](app/routers/documents.py) |
| Extraction IA | Gemini Flash 2.0 via OpenRouter, vision multimodale | [`app/services/extraction.py`](app/services/extraction.py) |
| Auto-enrichissement vehicule | Marque, modele, plaque, VIN extraits des documents | [`app/routers/documents.py:276`](app/routers/documents.py#L276) `_enrich_vehicle()` |
| Chat intelligent | Claude Sonnet 4 avec boucle d'outils agentic | [`app/services/agent.py`](app/services/agent.py) |
| PWA mobile | Camera capture, installation Android/iOS | [`app/static/manifest.json`](app/static/manifest.json), [`app/static/sw.js`](app/static/sw.js) |
| Multi-vehicule | Gestion N vehicules, stats par vehicule | [`app/routers/vehicles.py`](app/routers/vehicles.py) |

### Stack technique

| Couche | Technologie | Version |
|---|---|---|
| Backend | FastAPI + Uvicorn | 0.115.6 / 0.34.0 |
| BDD | SQLite + SQLAlchemy (sync) | 2.0.36 |
| LLM Chat | Claude Sonnet 4 (Anthropic SDK) | anthropic 0.44.0 |
| LLM Extraction | Gemini Flash 2.0 (OpenRouter) | httpx 0.28+ |
| PDF | PyMuPDF (fitz) | 1.25.3 |
| Image | Pillow | 11.1.0 |
| Frontend | Alpine.js 3 + Tailwind CSS (CDN) | CDN, pas de build |
| Runtime | Python 3.12+ | `python` or `python3` |

---

## 2. Architecture

### Arborescence

```
care-of-your-car/
├── run.py                          # Point d'entree uvicorn
├── .env                            # Cles API (gitignored)
├── .env.example                    # Template de configuration
├── requirements.txt                # Dependances Python
├── care.db                         # Base SQLite (auto-creee)
├── uploads/                        # Fichiers uploades (auto-cree)
├── app/
│   ├── __init__.py
│   ├── main.py                     # Application FastAPI, montage des routes
│   ├── config.py                   # Settings pydantic-settings depuis .env
│   ├── database.py                 # Engine SQLAlchemy, SessionLocal, Base
│   ├── models/
│   │   ├── __init__.py             # Re-exports de tous les modeles
│   │   ├── vehicle.py              # Vehicle
│   │   ├── document.py             # Document
│   │   ├── maintenance.py          # MaintenanceEvent + MaintenanceItem
│   │   ├── ct_report.py            # CTReport + CTDefect
│   │   └── conversation.py         # Conversation + Message
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── vehicle.py              # VehicleCreate/Update/Out/Summary
│   │   ├── document.py             # DocumentOut, ExtractionResult
│   │   ├── maintenance.py          # MaintenanceEventOut, MaintenanceItemOut
│   │   ├── ct_report.py            # CTReportOut, CTDefectOut
│   │   └── chat.py                 # ChatRequest/Response, ConversationOut, MessageOut
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── vehicles.py             # CRUD vehicules + stats calculees
│   │   ├── documents.py            # Upload, batch, SSE, extraction, enrichissement
│   │   └── chat.py                 # Envoi message, historique conversations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── extraction.py           # Pipeline Gemini : PDF→image, preprocess, prompt, parse
│   │   └── agent.py                # Boucle agentic Claude avec outils
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── prompts.py              # System prompt de l'assistant
│   │   └── tools.py                # 6 outils + dispatcher execute_tool()
│   └── static/
│       ├── index.html              # SPA Alpine.js
│       ├── manifest.json           # Manifest PWA
│       ├── sw.js                   # Service Worker (cache-first static, network-only API)
│       ├── css/style.css           # Styles additionnels (scrollbar, chat markdown)
│       ├── js/app.js               # Logique Alpine.js (state, API calls, upload, chat)
│       └── icons/                  # Icones PWA 192x192 et 512x512
```

### Diagramme de flux

```
                    ┌─────────────┐
                    │   Frontend   │  Alpine.js + Tailwind
                    │  index.html  │  app.js
                    └──────┬──────┘
                           │ HTTP / SSE
                    ┌──────┴──────┐
                    │   FastAPI    │  main.py
                    └──────┬──────┘
              ┌────────────┼────────────┐
              │            │            │
    ┌─────────┴──┐  ┌──────┴─────┐  ┌──┴──────────┐
    │  vehicles   │  │  documents  │  │    chat      │
    │  router     │  │  router     │  │    router    │
    └─────────┬──┘  └──────┬─────┘  └──┬──────────┘
              │            │            │
              │     ┌──────┴─────┐  ┌──┴──────────┐
              │     │ extraction  │  │    agent     │
              │     │  service    │  │   service    │
              │     └──────┬─────┘  └──┬──────────┘
              │            │            │
              │     ┌──────┴─────┐  ┌──┴──────────┐
              │     │ OpenRouter  │  │  Claude API  │
              │     │ (Gemini)    │  │  + tools.py  │
              │     └────────────┘  └─────────────┘
              │
       ┌──────┴──────┐
       │   SQLite     │  care.db
       │  (SQLAlchemy)│
       └─────────────┘
```

---

## 3. Modele de donnees

### Schema relationnel

```
vehicles (1) ──────< documents (N)
    │                     │ (0..1)
    │                     ├────── maintenance_events (0..1)
    │                     └────── ct_reports (0..1)
    │
    ├──────< maintenance_events (N)
    │              └──────< maintenance_items (N)
    │
    ├──────< ct_reports (N)
    │              └──────< ct_defects (N)
    │
    └──────< conversations (N)
                   └──────< messages (N)
```

### Table `vehicles` — [`app/models/vehicle.py:11`](app/models/vehicle.py#L11)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | Auto-increment |
| `name` | VARCHAR(100) | non | Nom convivial ("Ma Clio") |
| `brand` | VARCHAR(50) | oui | Marque — rempli par extraction |
| `model` | VARCHAR(50) | oui | Modele — rempli par extraction |
| `year` | INTEGER | oui | Annee — rempli par extraction |
| `plate_number` | VARCHAR(20) | oui | Immatriculation — rempli par extraction |
| `vin` | VARCHAR(50) | oui | Numero VIN — rempli par extraction |
| `fuel_type` | VARCHAR(20) | oui | Essence/Diesel/Electrique/Hybride/GPL |
| `owner_count` | INTEGER | oui | Nombre de proprietaires — rempli par CT |
| `initial_mileage` | INTEGER | oui | Km a l'achat |
| `purchase_date` | DATE | oui | Date d'achat |
| `created_at` | DATETIME | non | server_default=now() |

**Relations** : `documents`, `maintenance_events`, `ct_reports`, `conversations` (cascade delete-orphan)

**Schema creation** : [`app/schemas/vehicle.py:6`](app/schemas/vehicle.py#L6) — seul `name` est requis
**Schema summary** : [`app/schemas/vehicle.py:46`](app/schemas/vehicle.py#L46) — inclut `last_mileage`, `total_spent`, `document_count`, `ct_count` (calcules)
**Auto-enrichissement** : [`app/routers/documents.py:276`](app/routers/documents.py#L276) — `_enrich_vehicle()` ne remplit que les champs vides

### Table `documents` — [`app/models/document.py:11`](app/models/document.py#L11)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `vehicle_id` | INTEGER FK→vehicles | non | |
| `doc_type` | VARCHAR(20) | non | `invoice`, `ct_report`, `quote`, `unknown` |
| `file_path` | VARCHAR(500) | non | Chemin sur disque (uploads/) |
| `original_filename` | VARCHAR(255) | non | Nom original du fichier |
| `mime_type` | VARCHAR(50) | non | application/pdf, image/png, image/jpeg, image/webp |
| `uploaded_at` | DATETIME | non | server_default=now() |
| `extracted` | BOOLEAN | non | default=False, True apres extraction reussie |
| `extraction_raw` | TEXT | oui | JSON brut de l'extraction Gemini |

**Relations** : `vehicle`, `maintenance_event` (uselist=False), `ct_report` (uselist=False)
**Schema** : [`app/schemas/document.py`](app/schemas/document.py)
**MIME autorises** : `application/pdf`, `image/png`, `image/jpeg`, `image/webp` — [`app/routers/documents.py:22`](app/routers/documents.py#L22)

### Table `maintenance_events` — [`app/models/maintenance.py:11`](app/models/maintenance.py#L11)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `vehicle_id` | INTEGER FK→vehicles | non | |
| `document_id` | INTEGER FK→documents | oui | |
| `date` | DATE | non | Date de l'intervention |
| `mileage` | INTEGER | oui | Km au moment de l'intervention |
| `garage_name` | VARCHAR(200) | oui | |
| `total_cost` | FLOAT | oui | Montant total en euros |
| `notes` | TEXT | oui | |
| `event_type` | VARCHAR(20) | non | `invoice` ou `quote` |
| `created_at` | DATETIME | non | |

**Relations** : `vehicle`, `document`, `items` (cascade delete-orphan)
**Creation** : [`app/routers/documents.py:295`](app/routers/documents.py#L295) `_create_maintenance_event()`
**Schema** : [`app/schemas/maintenance.py`](app/schemas/maintenance.py)

### Table `maintenance_items` — [`app/models/maintenance.py:30`](app/models/maintenance.py#L30)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `event_id` | INTEGER FK→maintenance_events | non | |
| `description` | VARCHAR(500) | non | Description du travail |
| `category` | VARCHAR(50) | oui | Voir categories ci-dessous |
| `part_name` | VARCHAR(200) | oui | |
| `quantity` | FLOAT | oui | |
| `unit_price` | FLOAT | oui | |
| `labor_cost` | FLOAT | oui | |
| `total_price` | FLOAT | oui | |

**Categories** : `moteur`, `freinage`, `direction`, `suspension`, `transmission`, `echappement`, `electricite`, `carrosserie`, `climatisation`, `pneus`, `vidange`, `filtres`, `distribution`, `embrayage`, `autre`
(definies dans le prompt d'extraction — [`app/services/extraction.py:38`](app/services/extraction.py#L38))

### Table `ct_reports` — [`app/models/ct_report.py:11`](app/models/ct_report.py#L11)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `vehicle_id` | INTEGER FK→vehicles | non | |
| `document_id` | INTEGER FK→documents | oui | |
| `date` | DATE | non | Date du controle |
| `mileage` | INTEGER | oui | Km au controle |
| `center_name` | VARCHAR(200) | oui | |
| `result` | VARCHAR(30) | non | `favorable`, `defavorable`, `contre_visite` |
| `next_due_date` | DATE | oui | Prochaine echeance CT |
| `notes` | TEXT | oui | |
| `created_at` | DATETIME | non | |

**Relations** : `vehicle`, `document`, `defects` (cascade delete-orphan)
**Creation** : [`app/routers/documents.py:325`](app/routers/documents.py#L325) `_create_ct_report()`
**Schema** : [`app/schemas/ct_report.py`](app/schemas/ct_report.py)

### Table `ct_defects` — [`app/models/ct_report.py:30`](app/models/ct_report.py#L30)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `ct_report_id` | INTEGER FK→ct_reports | non | |
| `code` | VARCHAR(30) | oui | Code defaut (ex: 1.1.1.a.1) |
| `description` | VARCHAR(500) | non | |
| `severity` | VARCHAR(20) | non | `mineur`, `majeur`, `critique`, `a_surveiller` |
| `category` | VARCHAR(100) | oui | `direction`, `freinage`, `visibilite`, `eclairage`, `liaison_sol`, `structure`, `equipements`, `pollution`, `identification` |

### Table `conversations` — [`app/models/conversation.py:11`](app/models/conversation.py#L11)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `vehicle_id` | INTEGER FK→vehicles | oui | Peut etre global (null) |
| `title` | VARCHAR(200) | oui | Premier message tronque a 80 chars |
| `created_at` | DATETIME | non | |
| `updated_at` | DATETIME | non | onupdate=now() |

**Relations** : `vehicle`, `messages` (cascade delete-orphan)

### Table `messages` — [`app/models/conversation.py:24`](app/models/conversation.py#L24)

| Colonne | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER PK | non | |
| `conversation_id` | INTEGER FK→conversations | non | |
| `role` | VARCHAR(20) | non | `user` ou `assistant` |
| `content` | TEXT | non | |
| `created_at` | DATETIME | non | |

---

## 4. API REST

### Vehicules — [`app/routers/vehicles.py`](app/routers/vehicles.py)

Prefixe : `/api/vehicles`

| Methode | Endpoint | Handler (ligne) | Description | Request | Response |
|---|---|---|---|---|---|
| GET | `/api/vehicles` | [`list_vehicles:13`](app/routers/vehicles.py#L13) | Liste tous les vehicules avec stats calculees | — | `list[VehicleSummary]` |
| POST | `/api/vehicles` | [`create_vehicle:67`](app/routers/vehicles.py#L67) | Creer un vehicule (seul `name` requis) | `VehicleCreate` | `VehicleOut` (201) |
| GET | `/api/vehicles/{id}` | [`get_vehicle:76`](app/routers/vehicles.py#L76) | Detail d'un vehicule | — | `VehicleOut` |
| PATCH | `/api/vehicles/{id}` | [`update_vehicle:84`](app/routers/vehicles.py#L84) | Mise a jour partielle | `VehicleUpdate` | `VehicleOut` |
| DELETE | `/api/vehicles/{id}` | [`delete_vehicle:96`](app/routers/vehicles.py#L96) | Suppression (cascade) | — | 204 |

**Stats calculees dans `list_vehicles`** (lignes 13-63) :
- `last_mileage` : max(dernier entretien, dernier CT) par date
- `last_maintenance_date` : date du dernier MaintenanceEvent
- `total_spent` : SUM(total_cost) des factures uniquement (pas devis)
- `document_count` : COUNT(documents)
- `ct_count` : COUNT(ct_reports)

### Documents — [`app/routers/documents.py`](app/routers/documents.py)

Prefixe : `/api/documents`

| Methode | Endpoint | Handler (ligne) | Description | Request | Response |
|---|---|---|---|---|---|
| POST | `/api/documents/upload` | [`upload_and_extract:29`](app/routers/documents.py#L29) | Upload + extraction d'un fichier | FormData: `vehicle_id`, `doc_type`, `file` | `ExtractionResult` |
| POST | `/api/documents/batch-upload` | [`batch_upload:114`](app/routers/documents.py#L114) | Upload de N fichiers, retourne batch_id | FormData: `vehicle_id`, `doc_type`, `files[]` | `{batch_id, total}` |
| GET | `/api/documents/batch-status/{id}` | [`batch_status_sse:238`](app/routers/documents.py#L238) | SSE progression du batch | — | `text/event-stream` |
| GET | `/api/documents/{vehicle_id}` | [`list_documents:353`](app/routers/documents.py#L353) | Liste des documents d'un vehicule | — | `list[DocumentOut]` |
| GET | `/api/documents/{vehicle_id}/maintenance` | [`list_maintenance:363`](app/routers/documents.py#L363) | Entretiens d'un vehicule (avec items) | — | `list[MaintenanceEventOut]` |
| GET | `/api/documents/{vehicle_id}/ct-reports` | [`list_ct_reports:375`](app/routers/documents.py#L375) | CT d'un vehicule (avec defauts) | — | `list[CTReportOut]` |

#### Pipeline d'upload unique (lignes 29-110)

```
Fichier → Validation MIME → Sauvegarde disque → Creation Document DB
    → extract_document() → Parse resultat
    → Si invoice/quote : _create_maintenance_event() + _enrich_vehicle()
    → Si ct_report    : _create_ct_report() + _enrich_vehicle()
    → Sinon           : doc_type = "unknown"
```

#### Pipeline batch (lignes 114-175)

```
N fichiers → Validation + sauvegarde → Retour batch_id immediat
    → asyncio.create_task(_process_batch)
        → Semaphore(8) : 8 extractions concurrentes
        → Chaque fichier : _process_single_file() identique au single upload
    → Client ecoute SSE batch-status/{batch_id}
        → Message a chaque fichier traite : {processed, total, result}
        → Message final : {done, success_count, error_count}
```

**Concurrence batch** : [`app/routers/documents.py:159`](app/routers/documents.py#L159) — `asyncio.Semaphore(8)` + `asyncio.as_completed`

#### Enrichissement vehicule — [`_enrich_vehicle():276`](app/routers/documents.py#L276)

Ne remplit QUE les champs vides du vehicule. Champs sources : `brand`, `model`, `year`, `plate_number`, `vin`, `fuel_type`, `owner_count`.

### Chat — [`app/routers/chat.py`](app/routers/chat.py)

Prefixe : `/api/chat`

| Methode | Endpoint | Handler (ligne) | Description | Request | Response |
|---|---|---|---|---|---|
| POST | `/api/chat` | [`send_message:13`](app/routers/chat.py#L13) | Envoyer un message et obtenir la reponse IA | `ChatRequest` | `ChatResponse` |
| GET | `/api/chat/conversations` | [`list_conversations:54`](app/routers/chat.py#L54) | Liste conversations (filtre par vehicle_id) | ?vehicle_id= | `list[ConversationOut]` |
| GET | `/api/chat/conversations/{id}/messages` | [`get_messages:75`](app/routers/chat.py#L75) | Historique d'une conversation | — | `list[MessageOut]` |
| DELETE | `/api/chat/conversations/{id}` | [`delete_conversation:88`](app/routers/chat.py#L88) | Supprimer une conversation | — | 204 |

#### Flux POST /api/chat (lignes 13-50)

```
Message → Get/Create Conversation → Save user message DB
    → Build history (tous les messages de la conversation)
    → agent.chat(messages, vehicle_id, db)  ← boucle agentic
    → Save assistant message DB
    → Return {message, conversation_id}
```

---

## 5. Services metier

### Service d'extraction — [`app/services/extraction.py`](app/services/extraction.py)

**Modele** : `google/gemini-flash-2.0` via OpenRouter
**URL** : `https://openrouter.ai/api/v1/chat/completions`
**Timeout** : 120s
**Max tokens** : 4096

#### Pipeline d'extraction — `extract_document()` (ligne 209)

```
1. _build_image_content(file_path)
   ├── PDF ? → _pdf_to_images() (PyMuPDF, 200 DPI) → base64 PNG par page
   └── Image ? → _read_image() → _preprocess_image() → base64 PNG

2. Si doc_type_hint == "auto" :
   → _call_openrouter("ce document est un CT ou facture ?")
   → Repond "ct" ou "facture" → choix du prompt

3. _call_openrouter(image_parts, INVOICE_PROMPT ou CT_PROMPT)
   → Parse JSON (nettoyage markdown ```json...```)
   → Return dict structure
```

#### Preprocessing d'image — `_preprocess_image()` (ligne 115)

| Etape | Traitement | Raison |
|---|---|---|
| 1 | Correction EXIF orientation | Photos prises en paysage/renversees |
| 2 | Conversion RGB | Images RGBA/palette |
| 3 | Upscale si < 1500px (cote court) | Petites images illisibles |
| 4 | Contraste +30% | Eclairage insuffisant |
| 5 | Luminosite +10% | Sous-exposition |
| 6 | Sharpening (filtre SHARPEN) | Flou de mise au point |

**Note** : le preprocessing ne s'applique PAS aux rendus PDF (deja propres, ligne 171).

#### Prompts d'extraction

**INVOICE_PROMPT** (ligne 17) — extrait :
- `doc_type`, `date`, `mileage`, `garage_name`, `total_cost`
- `vehicle_info` : `brand`, `model`, `year`, `plate_number`, `vin`, `fuel_type`
- `items[]` : `description`, `category`, `part_name`, `quantity`, `unit_price`, `labor_cost`, `total_price`
- `notes`

**CT_PROMPT** (ligne 54) — extrait :
- `date`, `mileage`, `center_name`, `result`, `next_due_date`
- `vehicle_info` : idem + `owner_count`
- `defects[]` : `code`, `description`, `severity`, `category`
- `notes`

### Service agent — [`app/services/agent.py`](app/services/agent.py)

**Modele** : `claude-sonnet-4-20250514`
**Max tokens** : 4096
**Max iterations** : 10 (boucle agentic)

#### Boucle agentic — `chat()` (ligne 33)

```
system = SYSTEM_PROMPT + _build_context(db, vehicle_id)

Boucle (max 10 tours) :
  1. client.messages.create(model, system, tools, messages)
  2. Separer text_parts et tool_uses
  3. Si pas de tool_use → return texte
  4. Sinon :
     - Ajouter le message assistant (avec tool_use blocks) a l'historique
     - Pour chaque tool_use : execute_tool(name, input, db)
     - Ajouter les tool_result a l'historique
     - Reboucler
```

**Contexte injecte** — `_build_context()` (ligne 14) :
- Liste de tous les vehicules (id, nom, marque, modele, annee)
- Marqueur "(SELECTIONNE)" sur le vehicule courant
- Instruction d'utiliser cet ID dans les appels d'outils

---

## 6. Agent conversationnel

### System prompt — [`app/agent/prompts.py`](app/agent/prompts.py)

L'assistant est defini comme expert en entretien automobile avec 5 competences :
1. **Historique** : retrouver quand un travail a ete fait
2. **Analyse d'usure** : evaluer si une piece est normalement usee
3. **Detection d'anomalies** : comparer CT successifs, reperer incoherences
4. **Evaluation de devis** : croiser avec l'historique pour justification
5. **Conseils** : rappeler intervalles d'entretien courants

**Regles** : francais obligatoire, precision (dates/km/montants), factuel, utiliser les outils avant de repondre.

### Outils disponibles — [`app/agent/tools.py`](app/agent/tools.py)

| Outil | Ligne | Description | Parametres |
|---|---|---|---|
| `get_vehicle_info` | [109](app/agent/tools.py#L109) | Resume vehicule + stats | `vehicle_id` |
| `search_maintenance` | [162](app/agent/tools.py#L162) | Recherche entretien par mot-cle/categorie/dates | `vehicle_id`, `keyword?`, `category?`, `date_from?`, `date_to?`, `event_type?` |
| `get_ct_reports` | [214](app/agent/tools.py#L214) | Tous les CT avec defauts | `vehicle_id` |
| `compare_ct_reports` | [239](app/agent/tools.py#L239) | Comparaison entre 2 CT : nouveaux defauts, aggravations, resolutions, alertes | `vehicle_id`, `ct_report_id_old`, `ct_report_id_new` |
| `get_mileage_timeline` | [312](app/agent/tools.py#L312) | Chronologie km avec moyenne km/an | `vehicle_id` |
| `get_spending_summary` | [365](app/agent/tools.py#L365) | Depenses par categorie avec pourcentages | `vehicle_id`, `year?` |

**Dispatcher** : [`execute_tool():93`](app/agent/tools.py#L93) — dict de handlers, retourne string formatee.

**Definitions pour l'API Claude** : [`TOOL_DEFINITIONS:15`](app/agent/tools.py#L15) — format input_schema JSON Schema.

#### Detail `compare_ct_reports` (lignes 239-309)

Analyse avancee :
- Identifie les defauts **nouveaux** (presents dans le CT recent mais pas l'ancien)
- Identifie les defauts **aggraves** (severite augmentee entre les deux CT)
- Identifie les defauts **resolus** (presents dans l'ancien mais plus le recent)
- **Alerte** si defaut majeur/critique apparu avec < 10 000 km entre les deux CT

#### Detail `get_mileage_timeline` (lignes 312-362)

Compile tous les points km (entretiens + CT + achat) en chronologie :
- Delta km et jours entre chaque point
- Estimation km/an entre chaque intervalle
- Moyenne globale km/an

---

## 7. Frontend

### SPA Alpine.js — [`app/static/index.html`](app/static/index.html) + [`app/static/js/app.js`](app/static/js/app.js)

#### State applicatif — [`app.js:1`](app/static/js/app.js#L1)

| Variable | Type | Description |
|---|---|---|
| `view` | string | `'vehicles'` ou `'chat'` |
| `vehicles` | array | Liste VehicleSummary |
| `selectedVehicle` | object/null | Vehicule selectionne (detail ouvert) |
| `showAddVehicle` | bool | Modal de creation visible |
| `newVehicle` | object | `{name: ''}` |
| `detailTab` | string | `'maintenance'`, `'ct'`, `'docs'` |
| `maintenanceEvents` | array | Entretiens du vehicule selectionne |
| `ctReports` | array | CT du vehicule selectionne |
| `documents` | array | Documents du vehicule selectionne |
| `uploadDocType` | string | `'auto'`, `'invoice'`, `'ct_report'`, `'quote'` |
| `uploading` | bool | Upload en cours |
| `uploadResult` | object/null | Resultat du dernier upload unique |
| `dragOver` | bool | Drag en cours sur la zone d'upload |
| `batchProgress` | object/null | `{processed, total, done, success_count?, error_count?}` |
| `batchResults` | array | Resultats par fichier du batch |
| `chatVehicleId` | number/null | Vehicule selectionne pour le chat |
| `conversations` | array | Liste des conversations |
| `currentConversation` | object/null | Conversation active |
| `chatMessages` | array | Messages de la conversation |
| `chatInput` | string | Texte en cours de saisie |
| `chatLoading` | bool | Attente reponse IA |

#### Methodes principales — [`app.js`](app/static/js/app.js)

| Methode | Ligne | Description |
|---|---|---|
| `init()` | [28](app/static/js/app.js#L28) | Charge la liste des vehicules |
| `loadVehicles()` | [33](app/static/js/app.js#L33) | GET /api/vehicles |
| `addVehicle()` | [38](app/static/js/app.js#L38) | POST /api/vehicles (name only) |
| `selectVehicle(v)` | [51](app/static/js/app.js#L51) | Charge entretiens + CT + documents en parallele |
| `loadMaintenance(id)` | [64](app/static/js/app.js#L64) | GET /api/documents/{id}/maintenance |
| `loadCTReports(id)` | [69](app/static/js/app.js#L69) | GET /api/documents/{id}/ct-reports |
| `loadDocuments(id)` | [74](app/static/js/app.js#L74) | GET /api/documents/{id} |
| `uploadFile(file)` | [80](app/static/js/app.js#L80) | Upload unique + refresh toutes les donnees |
| `handleFileSelect(e)` | [106](app/static/js/app.js#L106) | Aiguillage : 1 fichier → upload unique, N → batch |
| `handleDrop(e)` | [117](app/static/js/app.js#L117) | Idem pour drag & drop |
| `batchUpload(files)` | [128](app/static/js/app.js#L128) | POST batch-upload + ecoute SSE pour progression |
| `loadConversations()` | [178](app/static/js/app.js#L178) | GET /api/chat/conversations |
| `newConversation()` | [185](app/static/js/app.js#L185) | Reset chat state |
| `selectConversation(c)` | [193](app/static/js/app.js#L193) | Charge messages + scroll |
| `sendMessage()` | [200](app/static/js/app.js#L200) | POST /api/chat (optimistic UI) |
| `scrollChat()` | [258](app/static/js/app.js#L258) | Scroll auto vers le bas |
| `formatMarkdown(text)` | [263](app/static/js/app.js#L263) | Rendu basique markdown → HTML |

#### Vues HTML — [`index.html`](app/static/index.html)

| Section | Lignes | Description |
|---|---|---|
| Header + navigation | [31-42](app/static/index.html#L31) | Onglets "Vehicules" / "Chat" |
| Grille vehicules | [57-75](app/static/index.html#L57) | Cards avec stats (km, depenses, docs, CT) |
| Modal ajout vehicule | [83-100](app/static/index.html#L83) | Formulaire nom uniquement |
| Zone d'upload | [116-174](app/static/index.html#L116) | Drag & drop, boutons parcourir/photo, radio doc type |
| Progression batch | [154-173](app/static/index.html#L154) | Barre + resultats par fichier |
| Onglet entretiens | [184-211](app/static/index.html#L184) | Liste chronologique factures/devis |
| Onglet CT | [214-245](app/static/index.html#L214) | CT avec defauts colores par severite |
| Onglet documents | [248-264](app/static/index.html#L248) | Liste brute des documents uploades |
| Vue chat | [270-335](app/static/index.html#L270) | Sidebar conversations + zone messages + input |

#### Styles — [`app/static/css/style.css`](app/static/css/style.css)

- `[x-cloak]` : cache les elements Alpine avant init
- Scrollbar personnalisee (6px, gris)
- `.chat-md` : styles markdown pour les reponses (titres, listes, code, pre)

---

## 8. PWA et mobile

### Manifest — [`app/static/manifest.json`](app/static/manifest.json)

- `display: standalone` (plein ecran, sans barre navigateur)
- `orientation: any` (portrait + paysage)
- `theme_color: #0369a1` (bleu brand)
- Icones 192x192 et 512x512 (`purpose: any maskable`)

### Service Worker — [`app/static/sw.js`](app/static/sw.js)

| Strategie | Cible | Comportement |
|---|---|---|
| Cache-first + update | Assets statiques (`/`, CSS, JS, manifest) | Reponse instantanee, mise a jour en arriere-plan |
| Network-only | `/api/*` | Donnees toujours fraiches |

**Cache** : `carcare-v1` — nettoyage des anciens caches a l'activation.
**Enregistrement** : [`index.html:340`](app/static/index.html#L340) — conditionnel `'serviceWorker' in navigator`.

### Camera capture

Bouton "Photo" avec `capture="environment"` (camera arriere) — [`index.html:130`](app/static/index.html#L130)
Accept : `image/*` — passe ensuite par le pipeline de preprocessing.

### Meta tags PWA — [`index.html:6-11`](app/static/index.html#L6)

- `viewport-fit=cover` (ecrans avec encoche)
- `apple-mobile-web-app-capable: yes`
- `apple-mobile-web-app-status-bar-style: black-translucent`
- `apple-mobile-web-app-title: CarCare`
- `apple-touch-icon` : icone 192px

---

## 9. Configuration et deploiement

### Variables d'environnement — [`.env.example`](.env.example)

| Variable | Requis | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | oui | — | Cle API Anthropic (Claude) |
| `OPENROUTER_API_KEY` | oui | — | Cle API OpenRouter (Gemini) |
| `DATABASE_URL` | non | `sqlite:///./care.db` | URL de connexion BDD |
| `UPLOAD_DIR` | non | `./uploads` | Repertoire de stockage des fichiers |

**Chargement** : [`app/config.py`](app/config.py) — pydantic-settings, `.env` file, pas de valeurs par defaut pour les cles API (crash au demarrage si absentes).

### Dependances — [`requirements.txt`](requirements.txt)

| Package | Usage | Reference |
|---|---|---|
| `fastapi` | Framework web | [`app/main.py`](app/main.py) |
| `uvicorn[standard]` | Serveur ASGI | [`run.py`](run.py) |
| `sqlalchemy` | ORM | [`app/database.py`](app/database.py) |
| `pydantic` + `pydantic-settings` | Validation + config | [`app/config.py`](app/config.py), `app/schemas/` |
| `python-multipart` | Upload fichiers (FormData) | [`app/routers/documents.py`](app/routers/documents.py) |
| `anthropic` | SDK Claude | [`app/services/agent.py`](app/services/agent.py) |
| `httpx` | Client HTTP pour OpenRouter | [`app/services/extraction.py`](app/services/extraction.py) |
| `Pillow` | Preprocessing images | [`app/services/extraction.py:115`](app/services/extraction.py#L115) |
| `PyMuPDF` | PDF → images | [`app/services/extraction.py:89`](app/services/extraction.py#L89) |
| `python-dotenv` | Chargement .env | Utilise par pydantic-settings |
| `aiofiles` | Fichiers async | Importe par FastAPI (StaticFiles) |

### Demarrage

```bash
# Installation
pip install -r requirements.txt

# Lancement (port 8200, hot reload)
python run.py

# Ou directement
uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload
```

La base SQLite et le dossier uploads sont crees automatiquement :
- Tables : [`app/main.py:10`](app/main.py#L10) — `Base.metadata.create_all()`
- Uploads : [`app/config.py:16`](app/config.py#L16) — `UPLOAD_PATH.mkdir()`

---

## 10. Flux utilisateur

### 1. Ajout d'un vehicule

```
[Bouton "Ajouter"] → Modal (nom uniquement) → POST /api/vehicles
→ Vehicule cree avec tous champs optionnels vides
→ Les infos seront remplies au fur et a mesure des imports
```

### 2. Import d'un document unique

```
[Selectionner vehicule] → [Zone d'upload : Parcourir/Photo/Drag]
→ Choix type (Auto/Facture/CT/Devis)
→ POST /api/documents/upload
→ Spinner "Extraction en cours..."
→ Resultat : "Facture extraite : 5 lignes" / "CT extrait : favorable, 2 defauts"
→ Donnees vehicule auto-remplies si champs vides
→ Onglets Entretiens/CT/Documents rafraichis
```

### 3. Import batch (50+ documents)

```
[Selectionner vehicule] → [Parcourir : selection multiple]
→ POST /api/documents/batch-upload
→ Barre de progression : "Analyse : 12 / 50"
→ Resultats par fichier en temps reel (OK/ERR + message)
→ Resume final : "45 reussi(s), 5 erreur(s)"
→ 8 fichiers traites en parallele (Semaphore)
→ Toutes les donnees rafraichies
```

### 4. Consultation des donnees

```
[Clic vehicule] → Detail avec 3 onglets :
  - Entretiens : chronologie factures/devis avec lignes detaillees
  - CT : resultat + defauts colores par severite
  - Documents : liste brute avec statut extraction
```

### 5. Chat avec l'assistant

```
[Onglet Chat] → [Selectionner vehicule] → [Nouvelle conversation]
→ "Quand ai-je change les plaquettes ?"
→ Claude appelle search_maintenance(keyword="plaquettes")
→ Reponse avec dates, km, prix exacts
→ "Compare les deux derniers CT"
→ Claude appelle get_ct_reports() puis compare_ct_reports()
→ Reponse avec analyse detaillee + alertes si anomalies
```

---

## 11. Carte des fichiers

Index de navigation rapide — chaque entree pointe vers le fichier et la ligne cle.

### Backend

| Fichier | Role | Points d'entree |
|---|---|---|
| [`run.py`](run.py) | Lancement uvicorn | L9 : `uvicorn.run()` |
| [`app/main.py`](app/main.py) | App FastAPI + montage routes | L10 : create_all, L15-17 : routers, L24 : index |
| [`app/config.py`](app/config.py) | Settings .env | L5 : `Settings`, L16 : `UPLOAD_PATH` |
| [`app/database.py`](app/database.py) | Engine + Session SQLAlchemy | L6 : engine, L12 : SessionLocal, L15 : Base, L19 : get_db |

### Modeles

| Fichier | Classes | Table(s) |
|---|---|---|
| [`app/models/vehicle.py`](app/models/vehicle.py) | `Vehicle` | `vehicles` |
| [`app/models/document.py`](app/models/document.py) | `Document` | `documents` |
| [`app/models/maintenance.py`](app/models/maintenance.py) | `MaintenanceEvent`, `MaintenanceItem` | `maintenance_events`, `maintenance_items` |
| [`app/models/ct_report.py`](app/models/ct_report.py) | `CTReport`, `CTDefect` | `ct_reports`, `ct_defects` |
| [`app/models/conversation.py`](app/models/conversation.py) | `Conversation`, `Message` | `conversations`, `messages` |

### Schemas (Pydantic)

| Fichier | Classes |
|---|---|
| [`app/schemas/vehicle.py`](app/schemas/vehicle.py) | `VehicleCreate`, `VehicleUpdate`, `VehicleOut`, `VehicleSummary` |
| [`app/schemas/document.py`](app/schemas/document.py) | `DocumentOut`, `ExtractionResult` |
| [`app/schemas/maintenance.py`](app/schemas/maintenance.py) | `MaintenanceEventOut`, `MaintenanceItemOut` |
| [`app/schemas/ct_report.py`](app/schemas/ct_report.py) | `CTReportOut`, `CTDefectOut` |
| [`app/schemas/chat.py`](app/schemas/chat.py) | `ChatRequest`, `ChatResponse`, `ConversationOut`, `MessageOut` |

### Routers (API)

| Fichier | Prefixe | Endpoints |
|---|---|---|
| [`app/routers/vehicles.py`](app/routers/vehicles.py) | `/api/vehicles` | GET, POST, GET/:id, PATCH/:id, DELETE/:id |
| [`app/routers/documents.py`](app/routers/documents.py) | `/api/documents` | POST/upload, POST/batch-upload, GET/batch-status/:id, GET/:vid, GET/:vid/maintenance, GET/:vid/ct-reports |
| [`app/routers/chat.py`](app/routers/chat.py) | `/api/chat` | POST, GET/conversations, GET/conversations/:id/messages, DELETE/conversations/:id |

### Services

| Fichier | Fonction principale | LLM utilise |
|---|---|---|
| [`app/services/extraction.py`](app/services/extraction.py) | `extract_document()` L209 | Gemini Flash 2.0 (OpenRouter) |
| [`app/services/agent.py`](app/services/agent.py) | `chat()` L33 | Claude Sonnet 4 (Anthropic SDK) |

### Agent

| Fichier | Contenu |
|---|---|
| [`app/agent/prompts.py`](app/agent/prompts.py) | `SYSTEM_PROMPT` — definition du role et des competences |
| [`app/agent/tools.py`](app/agent/tools.py) | `TOOL_DEFINITIONS` L15, `execute_tool()` L93, 6 handlers (L109-388) |

### Frontend

| Fichier | Role |
|---|---|
| [`app/static/index.html`](app/static/index.html) | SPA complete (345 lignes) — header, vehicules, upload, detail, chat |
| [`app/static/js/app.js`](app/static/js/app.js) | Logique Alpine.js — state, API calls, upload/batch, chat |
| [`app/static/css/style.css`](app/static/css/style.css) | Styles additionnels (scrollbar, chat markdown) |
| [`app/static/manifest.json`](app/static/manifest.json) | Manifest PWA |
| [`app/static/sw.js`](app/static/sw.js) | Service Worker (cache static, network API) |

### Historique git

| Commit | Description |
|---|---|
| `578332c` | Initial v0.1.0 |
| `c626c3e` | Auto-enrichissement vehicule depuis les documents |
| `878d632` | Pipeline preprocessing images (EXIF, contraste, sharpen) |
| `90cb889` | PWA (manifest, service worker, camera capture) |
| `d15428a` | Import batch avec progression SSE temps reel |
| `c7abde9` | Parallelisation batch (8 concurrent, Semaphore) |
