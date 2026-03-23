# Architecture

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy 2.0 |
| Chat AI | Claude Sonnet 4 (Anthropic SDK) |
| Extraction AI | Gemini Flash 2.0 (OpenRouter) |
| Frontend | Alpine.js 3 + Tailwind CSS (CDN) |
| PDF | PyMuPDF |
| Auth | JWT + bcrypt |

## Database (13 tables)

- `users` — User accounts
- `vehicles` — Vehicles
- `documents` — Uploaded documents
- `maintenance_events` — Maintenance records
- `maintenance_items` — Individual parts/labor per event
- `ct_reports` — Technical inspection reports
- `ct_defects` — Defects found in inspections
- `fuel_records` — Fuel fill-ups
- `tax_insurance_records` — Tax and insurance
- `vehicle_notes` — Free-form notes
- `maintenance_reminders` — Custom reminders
- `vehicle_access` — Sharing/permissions
- `conversations` + `messages` — Chat history

## AI Agent (13 tools)

The chat assistant uses an agentic loop with Claude Sonnet 4. It has 13 tools that query the database to answer questions about vehicles, maintenance, fuel, taxes, notes, and upcoming deadlines.
