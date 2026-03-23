# Car Carer

> [English](README.md) | [Francais](README.fr.md) | [Deutsch](README.de.md) | **Espanol**

**Tu companero de IA para el mantenimiento del coche**

![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

---

## Que es Car Carer?

Car Carer es una aplicacion web autoalojada para el seguimiento completo del mantenimiento de tus vehiculos. Sube facturas, presupuestos o informes de ITV (en formato PDF o foto), y la IA extrae automaticamente los datos estructurados: fechas, kilometraje, costes, piezas, defectos y mucho mas. Ademas, un asistente de chat inteligente te permite consultar el historial de mantenimiento de tu vehiculo en lenguaje natural, detectar anomalias y obtener recomendaciones personalizadas.

---

## Caracteristicas

- :page_facing_up: **Extraccion de documentos con IA** — Gemini Flash 2.0 via OpenRouter analiza facturas, presupuestos e informes de ITV con vision multimodal (PDF e imagenes)
- :robot: **Asistente de chat inteligente** — Claude Sonnet 4 con bucle agentico y 6 herramientas: buscar mantenimiento, consultar ITVs, comparar inspecciones, cronologia de kilometraje, resumen de gastos e info del vehiculo
- :car: **Gestion multi-vehiculo** — Administra N vehiculos con estadisticas calculadas (kilometraje, gasto total, documentos, puntuacion de salud)
- :zap: **Carga por lotes** — Sube 50+ documentos de una vez con progreso en tiempo real via SSE (8 extracciones concurrentes)
- :sparkles: **Auto-enriquecimiento del vehiculo** — Marca, modelo, matricula, VIN, tipo de combustible y numero de propietarios se rellenan automaticamente desde los documentos
- :bell: **Recordatorios de mantenimiento** — Alertas basadas en el historial y las inspecciones tecnicas
- :iphone: **PWA instalable** — Funciona en movil, captura directa con la camara trasera, modo offline para assets estaticos
- :hammer_and_wrench: **Sin paso de compilacion** — Frontend SPA con Alpine.js 3 + Tailwind CSS via CDN, sin Node.js necesario

---

## Capturas de pantalla

> :construction: Proximamente

---

## Inicio rapido

### 1. Clonar el repositorio

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd care-of-your-car
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus claves API (ver seccion [Configuracion](#configuracion)).

### 5. Iniciar la aplicacion

```bash
python run.py
```

La aplicacion estara disponible en **http://localhost:8200**

La base de datos SQLite (`care.db`) y la carpeta `uploads/` se crean automaticamente en el primer inicio.

### 6. Explorar la API

Abre **http://localhost:8200/docs** para acceder a la documentacion interactiva Swagger.

---

## Configuracion

Todas las variables se definen en el archivo `.env` en la raiz del proyecto.

| Variable | Requerida | Valor por defecto | Descripcion |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Si | — | Clave API de Anthropic para el asistente de chat (Claude Sonnet 4) |
| `OPENROUTER_API_KEY` | Si | — | Clave API de OpenRouter para la extraccion de documentos (Gemini Flash 2.0) |
| `DATABASE_URL` | No | `sqlite:///./care.db` | URL de conexion a la base de datos |
| `UPLOAD_DIR` | No | `./uploads` | Directorio de almacenamiento de archivos subidos |
| `BATCH_MAX_CONCURRENT` | No | `3` | Numero de extracciones simultaneas en carga por lotes |
| `BATCH_MAX_FILES` | No | `100` | Numero maximo de archivos por lote |
| `EXTRACTION_TIMEOUT` | No | `60` | Timeout en segundos para cada extraccion |
| `EXTRACTION_MODEL` | No | `google/gemini-flash-2.0` | Modelo LLM para extraccion via OpenRouter |
| `MAX_PHOTO_SIZE_MB` | No | `10` | Tamano maximo de foto en MB |

---

## Stack tecnico

| Capa | Tecnologia | Version |
|---|---|---|
| Backend | FastAPI + Uvicorn | 0.115.6 / 0.34.0 |
| Base de datos | SQLite + SQLAlchemy (sincrono) | 2.0.36 |
| LLM Chat | Claude Sonnet 4 (SDK Anthropic) | anthropic 0.44.0 |
| LLM Extraccion | Gemini Flash 2.0 (OpenRouter) | httpx 0.28+ |
| Procesamiento PDF | PyMuPDF (fitz) | 1.25.3 |
| Procesamiento imagen | Pillow | 11.1.0 |
| Frontend | Alpine.js 3 + Tailwind CSS (CDN) | CDN, sin build |
| Runtime | Python | 3.12+ |

---

## Estructura del proyecto

```
care-of-your-car/
├── run.py                      # Punto de entrada (uvicorn)
├── .env                        # Claves API (gitignored)
├── .env.example                # Plantilla de configuracion
├── requirements.txt            # Dependencias Python
├── care.db                     # Base de datos SQLite (auto-creada)
├── uploads/                    # Archivos subidos (auto-creado)
├── app/
│   ├── main.py                 # Aplicacion FastAPI, montaje de rutas
│   ├── config.py               # Settings desde .env (pydantic-settings)
│   ├── database.py             # Engine SQLAlchemy, sesion, base
│   ├── models/                 # Modelos SQLAlchemy (8 tablas)
│   │   ├── vehicle.py          # Vehicle
│   │   ├── document.py         # Document
│   │   ├── maintenance.py      # MaintenanceEvent + MaintenanceItem
│   │   ├── ct_report.py        # CTReport + CTDefect
│   │   └── conversation.py     # Conversation + Message
│   ├── schemas/                # Schemas Pydantic (validacion)
│   ├── routers/                # Endpoints API REST
│   │   ├── vehicles.py         # CRUD vehiculos + estadisticas
│   │   ├── documents.py        # Upload, lotes, SSE, extraccion
│   │   └── chat.py             # Chat, conversaciones, historial
│   ├── services/
│   │   ├── extraction.py       # Pipeline Gemini: PDF→imagen, preprocesamiento, extraccion
│   │   └── agent.py            # Bucle agentico Claude con herramientas
│   ├── agent/
│   │   ├── prompts.py          # System prompt del asistente
│   │   └── tools.py            # 6 herramientas + dispatcher
│   └── static/
│       ├── index.html          # SPA Alpine.js (aplicacion completa)
│       ├── js/app.js           # Logica Alpine.js (estado, API, chat)
│       ├── css/style.css       # Estilos adicionales
│       ├── manifest.json       # Manifiesto PWA
│       ├── sw.js               # Service Worker
│       └── icons/              # Iconos PWA (192x192, 512x512)
```

---

## Documentacion API

Car Carer expone una API REST completa documentada automaticamente por FastAPI.

Accede a la documentacion interactiva Swagger en:

```
http://localhost:8200/docs
```

### Endpoints principales

| Grupo | Prefijo | Descripcion |
|---|---|---|
| Vehiculos | `/api/vehicles` | CRUD completo + estadisticas calculadas |
| Documentos | `/api/documents` | Upload individual y por lotes, extraccion IA, listado |
| Chat | `/api/chat` | Envio de mensajes, historial de conversaciones |

---

## Contribuir

Las contribuciones son bienvenidas. Para colaborar:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/mi-funcionalidad`)
3. Realiza tus cambios y anade tests si corresponde
4. Asegurate de que la aplicacion arranca correctamente (`python run.py`)
5. Haz commit de tus cambios (`git commit -m "Agregar mi funcionalidad"`)
6. Sube la rama (`git push origin feature/mi-funcionalidad`)
7. Abre un Pull Request describiendo los cambios

### Directrices

- Mantener la simplicidad: sin paso de compilacion frontend, sin Docker obligatorio
- Seguir la estructura de carpetas existente
- Documentar los endpoints nuevos (FastAPI los documenta automaticamente con type hints)
- Las claves API nunca deben ir hardcodeadas ni comprometidas en el repositorio

---

## Licencia

Este proyecto esta licenciado bajo la [Licencia MIT](LICENSE).

---

## Agradecimientos

Construido con:

- [Claude](https://www.anthropic.com/) (Anthropic) — Asistente de chat inteligente con herramientas
- [Gemini](https://deepmind.google/technologies/gemini/) (Google) via [OpenRouter](https://openrouter.ai/) — Extraccion de documentos con vision multimodal
- [FastAPI](https://fastapi.tiangolo.com/) — Framework web moderno y rapido
- [Alpine.js](https://alpinejs.dev/) — Framework reactivo ligero para el frontend
- [Tailwind CSS](https://tailwindcss.com/) — Framework de utilidades CSS
