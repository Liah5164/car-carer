# Title

I built an AI-powered car maintenance tracker that reads your invoices so you don't have to type anything

# Body

Hey r/selfhosted,

I've been keeping car invoices in a shoebox for years. Every time I needed to know when I last changed the brake pads or how much I spent at the garage, I'd dig through a pile of crumpled papers. I tried LubeLogger and similar tools, but I always dropped them after a week because manually entering every line item from every invoice is just... painful.

So I built **Car Carer** -- a self-hosted car maintenance tracker where you upload your documents and AI does the rest.

## What it does

1. **Upload** a PDF invoice, a photo of a receipt, or a technical inspection report
2. **AI extracts** everything automatically -- date, mileage, garage name, individual parts with costs and categories, vehicle info (plate number, VIN, fuel type...)
3. **Ask questions** in natural language -- "When did I last change the oil?", "Compare my last two inspections", "How much did I spend on brakes this year?"

The chat assistant is an actual agentic loop with 13 tools that query your database. It's not just a chatbot wrapper -- it can cross-reference inspection reports, detect anomalies (a major defect appearing from nowhere between two inspections is flagged as suspicious), track mileage evolution, compute spending breakdowns, monitor fuel consumption, check insurance/tax renewals, and give proactive maintenance alerts.

## What makes it different from LubeLogger

LubeLogger (great project, 2400+ stars) is a solid manual tracker. Car Carer takes a different approach: **zero manual data entry**. You upload documents, AI extracts structured data. You chat with your data instead of browsing tables. Vehicle info (brand, model, plate, VIN, fuel type) is auto-filled from your first uploaded invoice. It also handles things LubeLogger doesn't: fuel consumption tracking, tax/insurance renewal alerts, custom maintenance reminders, proactive analysis that flags overdue services and unresolved inspection defects.

It's not a replacement -- it's a different philosophy. If you like manual control, LubeLogger is great. If you want to dump a folder of invoices and let AI figure it out, that's Car Carer.

## Stack

- **Backend**: FastAPI + SQLite (SQLAlchemy) -- no Postgres needed, zero config database
- **Extraction AI**: Gemini Flash 2.0 via OpenRouter (multimodal, reads PDFs and photos)
- **Chat AI**: Claude Sonnet 4 (Anthropic SDK, agentic loop with 13 tools)
- **Frontend**: Alpine.js + Tailwind CSS via CDN -- **no build step, no Node, no npm, no webpack**
- **PWA**: installable on mobile, camera capture for snapping invoices on the go
- **Auth**: JWT with multi-user support and vehicle sharing (share a car with your mechanic or family)
- **Docker**: `docker-compose up` and you're done
- **i18n**: FR/EN/DE/ES

15 Python dependencies total. No JS build chain. The entire frontend is a single HTML file + one JS file + one CSS file served statically.

## How to try it

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd car-carer
cp .env.example .env
# Add your ANTHROPIC_API_KEY and OPENROUTER_API_KEY
docker-compose up
```

Open http://localhost:8200. That's it.

You need an Anthropic API key (for the chat) and an OpenRouter API key (for document extraction). Both have free tiers / low cost.

## Screenshots

> [TODO: vehicle dashboard, document upload with extraction result, chat conversation, batch upload progress]

## Current state

- v0.2.0, MIT licensed
- 65 tests passing, 13 test files
- 13 database tables, 60+ API routes, 13 agent tools
- Batch upload: import 50+ documents at once with real-time SSE progress (8 concurrent extractions)
- PDF export of vehicle maintenance reports
- 4 languages (auto-detected from browser)

## What's next

- Notifications (upcoming service reminders, expiring insurance)
- Cost prediction based on history
- Multi-model support for extraction (not just Gemini)
- Mobile app improvements (offline mode)

## Links

- **GitHub**: https://github.com/Greal-dev/car-carer
- **License**: MIT

It's still early and I'd love feedback. Architecture suggestions, feature ideas, things that annoy you -- all welcome. Happy to answer any questions.
