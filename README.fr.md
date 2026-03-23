# Car Carer

> [English](README.md) | **Francais** | [Deutsch](README.de.md) | [Espanol](README.es.md)

**Votre compagnon IA pour l'entretien automobile**

![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

---

## 📋 Qu'est-ce que Car Carer ?

Car Carer est une application web auto-hebergee de suivi d'entretien automobile. Importez vos factures, devis et PV de controle technique (PDF ou photo), et l'IA extrait automatiquement les donnees structurees : lignes de facturation, defauts CT, kilometres, couts. Un assistant chat intelligent, adosse a l'historique complet de vos vehicules, vous aide ensuite a comprendre, analyser et anticiper l'entretien de votre flotte.

---

## ✨ Fonctionnalites

- 🔍 **Extraction IA de documents** — Gemini Flash 2.0 (via OpenRouter) analyse vos factures, devis et PV de controle technique avec la vision multimodale (PDF et photos)
- 💬 **Assistant chat intelligent** — Claude Sonnet 4 avec 6 outils specialises : recherche d'entretien, comparaison de CT, chronologie kilometrique, bilan de depenses...
- 🚙 **Gestion multi-vehicules** — Statistiques calculees par vehicule (km, depenses, nombre de documents, score CT)
- 📦 **Import par lot** — Jusqu'a 50+ documents en une fois, avec suivi de progression en temps reel (SSE) et 8 extractions concurrentes
- 🔄 **Auto-enrichissement vehicule** — Marque, modele, plaque, VIN et type de carburant remplis automatiquement depuis les documents importes
- ⏰ **Rappels d'entretien et alertes** — Detection d'anomalies entre CT successifs, alertes sur defauts critiques
- 📱 **PWA installable** — Application installable sur mobile (Android/iOS), capture camera directe pour photographier vos documents
- 🎨 **Pas de build** — Frontend Alpine.js + Tailwind CSS via CDN, zero etape de compilation

---

## Captures d'ecran

| Tableau de bord | Import de documents |
|:---------------:|:-------------------:|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Upload](docs/screenshots/upload.png) |

| Chat IA | Suivi carburant |
|:-------:|:---------------:|
| ![Chat](docs/screenshots/chat.png) | ![Carburant](docs/screenshots/fuel.png) |

| Taxes & Assurances | Partage vehicule |
|:------------------:|:----------------:|
| ![Taxes](docs/screenshots/taxes.png) | ![Partage](docs/screenshots/sharing.png) |

---

## 🚀 Demarrage rapide

### 1. Cloner le depot

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd care-of-your-car
```

### 2. Creer l'environnement Python

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Configurer les cles API

```bash
cp .env.example .env
```

Editez `.env` et renseignez vos cles :

```env
ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
```

### 4. Lancer l'application

```bash
python run.py
```

Ouvrez **http://localhost:8200** dans votre navigateur. La base de donnees SQLite et le dossier `uploads/` sont crees automatiquement au premier demarrage.

---

## ⚙️ Configuration

Toutes les variables sont definies dans le fichier `.env` :

| Variable | Requis | Valeur par defaut | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Oui | — | Cle API Anthropic pour le chat (Claude Sonnet 4) |
| `OPENROUTER_API_KEY` | Oui | — | Cle API OpenRouter pour l'extraction (Gemini Flash 2.0) |
| `DATABASE_URL` | Non | `sqlite:///./care.db` | URL de connexion a la base de donnees |
| `UPLOAD_DIR` | Non | `./uploads` | Repertoire de stockage des fichiers uploades |
| `BATCH_MAX_CONCURRENT` | Non | `3` | Nombre d'extractions concurrentes en mode batch |
| `BATCH_MAX_FILES` | Non | `100` | Nombre maximum de fichiers par import batch |
| `EXTRACTION_TIMEOUT` | Non | `60` | Timeout (en secondes) pour chaque extraction |
| `EXTRACTION_MODEL` | Non | `google/gemini-2.5-flash` | Modele OpenRouter a utiliser pour l'extraction |
| `MAX_PHOTO_SIZE_MB` | Non | `10` | Taille maximale des photos (en Mo) |

---

## 🛠️ Stack technique

| Couche | Technologie | Version |
|---|---|---|
| Backend | FastAPI + Uvicorn | 0.115.6 / 0.34.0 |
| Base de donnees | SQLite + SQLAlchemy (sync) | 2.0.36 |
| LLM Chat | Claude Sonnet 4 (Anthropic SDK) | anthropic 0.44.0 |
| LLM Extraction | Gemini Flash 2.0 (OpenRouter) | httpx 0.28+ |
| Traitement PDF | PyMuPDF (fitz) | 1.25.3 |
| Traitement image | Pillow | 11.1.0 |
| Frontend | Alpine.js 3 + Tailwind CSS (CDN) | Pas de build |
| Runtime | Python | 3.12+ |

---

## 📁 Structure du projet

```
care-of-your-car/
├── run.py                      # Point d'entree (uvicorn, port 8200)
├── .env.example                # Template de configuration
├── requirements.txt            # Dependances Python
├── app/
│   ├── main.py                 # Application FastAPI, montage des routes
│   ├── config.py               # Settings depuis .env (pydantic-settings)
│   ├── database.py             # Engine SQLAlchemy + session
│   ├── models/                 # Modeles SQLAlchemy (8 tables)
│   │   ├── vehicle.py          # Vehicle
│   │   ├── document.py         # Document
│   │   ├── maintenance.py      # MaintenanceEvent + MaintenanceItem
│   │   ├── ct_report.py        # CTReport + CTDefect
│   │   └── conversation.py     # Conversation + Message
│   ├── schemas/                # Schemas Pydantic (validation)
│   ├── routers/                # Endpoints API
│   │   ├── vehicles.py         # CRUD vehicules + stats
│   │   ├── documents.py        # Upload, batch, extraction, enrichissement
│   │   └── chat.py             # Chat agent + historique conversations
│   ├── services/
│   │   ├── extraction.py       # Pipeline Gemini (PDF → images → extraction)
│   │   └── agent.py            # Boucle agentic Claude (max 10 tours)
│   ├── agent/
│   │   ├── prompts.py          # System prompt de l'assistant
│   │   └── tools.py            # 6 outils + dispatcher
│   └── static/                 # Frontend SPA
│       ├── index.html          # Interface Alpine.js
│       ├── js/app.js           # Logique applicative
│       ├── css/style.css       # Styles additionnels
│       ├── manifest.json       # Manifest PWA
│       ├── sw.js               # Service Worker
│       └── icons/              # Icones PWA (192x192, 512x512)
└── tests/                      # Tests
```

---

## 📡 Documentation API

L'application expose une documentation interactive Swagger generee automatiquement par FastAPI.

Une fois le serveur lance, rendez-vous sur :

- **Swagger UI** : [http://localhost:8200/docs](http://localhost:8200/docs)
- **ReDoc** : [http://localhost:8200/redoc](http://localhost:8200/redoc)

### Endpoints principaux

| Methode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/vehicles` | Lister les vehicules avec stats |
| `POST` | `/api/vehicles` | Creer un vehicule |
| `POST` | `/api/documents/upload` | Uploader et extraire un document |
| `POST` | `/api/documents/batch-upload` | Import batch (retourne un batch_id) |
| `GET` | `/api/documents/batch-status/{id}` | Suivi SSE de la progression batch |
| `POST` | `/api/chat` | Envoyer un message au chat agent |
| `GET` | `/api/chat/conversations` | Lister les conversations |

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment participer :

1. **Forkez** le depot
2. **Creez** une branche pour votre fonctionnalite (`git checkout -b feature/ma-fonctionnalite`)
3. **Commitez** vos modifications (`git commit -m "Ajout de ma fonctionnalite"`)
4. **Poussez** vers votre fork (`git push origin feature/ma-fonctionnalite`)
5. **Ouvrez** une Pull Request

### Conventions

- Code Python : suivez PEP 8
- Messages de commit : en francais ou en anglais, concis et descriptifs
- Ajoutez des tests pour toute nouvelle fonctionnalite

---

## 📄 Licence

Ce projet est distribue sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de details.

---

## 🙏 Remerciements

Construit avec :

- [Claude](https://www.anthropic.com/) (Anthropic) — Assistant chat intelligent
- [Gemini](https://deepmind.google/technologies/gemini/) (Google) via [OpenRouter](https://openrouter.ai/) — Extraction de documents
- [FastAPI](https://fastapi.tiangolo.com/) — Framework web Python
- [Alpine.js](https://alpinejs.dev/) — Framework frontend reactif
- [Tailwind CSS](https://tailwindcss.com/) — Framework CSS utilitaire
