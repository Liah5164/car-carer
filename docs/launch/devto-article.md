---
title: How I Built an AI Car Maintenance Tracker with Claude + Gemini (Open Source)
published: false
description: Upload invoices, AI extracts structured data, chat with your car's history. Self-hosted, FastAPI + Alpine.js, no build step.
tags: python, ai, opensource, fastapi
cover_image: [TODO: add cover image URL]
---

# How I Built an AI Car Maintenance Tracker with Claude + Gemini (Open Source)

I have a shoebox full of car invoices. Not metaphorically -- an actual shoebox. Oil changes, brake pads, timing belt, inspection reports, tires. Every time my mechanic asks "when did you last change the oil?" I stare blankly and say "maybe... last spring?"

I've tried car maintenance apps. The problem is always the same: you have to manually enter every line item from every invoice. Date, mileage, part name, cost, category. For one invoice with 8 line items, that's 2 minutes of typing. Multiply by 30 invoices and you've lost an hour of your life to data entry. Nobody sticks with it.

So I built something different.

## The Idea

What if you could just **upload** your invoices -- PDFs, photos from your phone, whatever -- and AI would extract all the structured data automatically? And then, instead of browsing tables and charts, you could just **ask questions** in natural language?

"When did I last change the brake pads?"
"Compare my last two inspections -- any new defects?"
"How much did I spend on tires this year?"
"Is my oil change overdue?"

That's **Car Carer**: a self-hosted web app that turns a pile of invoices into a queryable car maintenance database, powered by two AI models working together.

## Architecture Overview

```
Upload (PDF/photo)
    |
    v
[Gemini Flash 2.0] -- extracts structured data (JSON)
    |
    v
[SQLite Database] -- 13 tables (vehicles, maintenance, inspections, fuel, reminders...)
    |
    v
[Claude Sonnet 4] -- agentic chat with 13 tools that query the DB
    |
    v
Natural language answers with dates, costs, and alerts
```

The stack is deliberately simple:

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI + Uvicorn | Async, fast, auto-generated API docs |
| Database | SQLite + SQLAlchemy | Zero config, single file, good enough for personal use |
| Extraction | Gemini Flash 2.0 (via OpenRouter) | Best multimodal price/quality, reads handwriting |
| Chat | Claude Sonnet 4 (Anthropic SDK) | Best tool-use model, reliable agentic loops |
| Frontend | Alpine.js + Tailwind CSS (CDN) | No build step, no Node, no npm |
| Mobile | PWA (Service Worker) | Installable, camera capture |

15 Python dependencies. That's it.

## The Extraction Pipeline

This is where Gemini shines. The pipeline:

1. **PDF handling**: PyMuPDF converts each page to a 200 DPI image
2. **Image preprocessing**: Pillow corrects EXIF rotation, enhances contrast, applies sharpening
3. **Multimodal prompt**: The image is sent to Gemini Flash 2.0 with a structured JSON prompt

The prompt asks for a precise schema:

```python
INVOICE_PROMPT = """Analyse this car maintenance invoice.
Extract the following as strict JSON:

{
  "doc_type": "invoice" or "quote",
  "date": "YYYY-MM-DD",
  "mileage": number or null,
  "garage_name": "string or null",
  "total_cost": number or null,
  "vehicle_info": {
    "brand": "...", "model": "...", "plate_number": "...",
    "vin": "...", "fuel_type": "..."
  },
  "items": [
    {
      "description": "work description",
      "category": "one of 15 predefined categories",
      "part_name": "...",
      "quantity": number,
      "unit_price": number,
      "labor_cost": number,
      "total_price": number
    }
  ]
}
"""
```

There are 15 maintenance categories (engine, braking, suspension, tires, oil change, filters, timing belt, exhaust, electrical, lighting, bodywork, AC, steering, transmission, cooling) so every line item is automatically categorized for spending breakdowns.

The same pipeline handles technical inspection reports, with a different prompt that extracts defects with severity levels (minor, major, critical) and defect codes.

**Auto-enrichment bonus**: the extraction returns vehicle info (brand, model, plate number, VIN, fuel type). The backend automatically fills in any missing vehicle fields. Create a vehicle with just a name, upload one invoice, and suddenly the app knows it's a 2019 Peugeot 308 diesel.

## The Chat Agent

This is where Claude comes in. The agent is not a simple Q&A chatbot -- it's a full agentic loop with 13 tools:

```python
TOOL_DEFINITIONS = [
    {"name": "get_vehicle_info", ...},
    {"name": "search_maintenance", ...},      # keyword, category, date range
    {"name": "get_ct_reports", ...},           # all inspections with defects
    {"name": "compare_ct_reports", ...},       # diff between two inspections
    {"name": "get_mileage_timeline", ...},     # km evolution over time
    {"name": "get_spending_summary", ...},     # spending by category
    {"name": "get_vehicle_analysis", ...},     # proactive alerts
    {"name": "get_fuel_stats", ...},           # consumption L/100km
    {"name": "get_fuel_history", ...},         # fuel log
    {"name": "get_vehicle_notes", ...},        # user notes
    {"name": "add_vehicle_note", ...},         # create a note
    {"name": "get_tax_insurance_status", ...}, # renewals and deadlines
    {"name": "get_upcoming_renewals", ...},    # upcoming deadlines
]
```

Each tool is a pure function: takes a DB session + parameters, returns a formatted string. No framework, no LangChain, no abstractions. The entire agent is ~100 lines:

```python
while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=SYSTEM_PROMPT + vehicle_context,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        max_tokens=4096,
    )

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input, db)
                # Feed result back to Claude
        continue

    break  # Final answer
```

The `compare_ct_reports` tool is my favorite. It diffs two inspection reports and flags:
- **New defects** that weren't there before (suspicious if severity is major/critical)
- **Escalated defects** (minor -> major)
- **Resolved defects** (good news)
- **Anomaly detection**: a major defect appearing from nowhere after only 5,000 km is flagged as suspicious

The `get_vehicle_analysis` tool runs a proactive health check: overdue oil changes, aging timing belt, unresolved inspection defects, expiring insurance. Ask "how is my car doing?" and you get a priority-sorted alert list.

## The Frontend: Zero Build

This was a deliberate choice. The entire frontend is:
- `index.html` -- one SPA page with Alpine.js directives
- `app.js` -- Alpine.js component logic (~1500 lines)
- `style.css` -- custom styles for scrollbars and chat formatting
- Alpine.js 3 and Tailwind CSS loaded from CDN

No Node. No npm. No webpack. No Vite. No `package.json`. FastAPI serves the static directory directly.

For a self-hosted tool, this is a sweet spot: instant "hot reload" (just refresh the browser), tiny Docker image, zero JS toolchain to maintain or upgrade. The tradeoff is no TypeScript and no component framework, but for a tool this size, plain Alpine.js handles it well.

The app is also a PWA -- installable on Android/iOS with a Service Worker that caches static assets. On mobile, you can snap a photo of an invoice directly from the app's camera button and upload it.

## Vehicle Sharing

A feature I added for a specific use case: sharing a vehicle with a mechanic, family member, or co-owner. You generate a share link with configurable permissions (view-only or full access), and the recipient can see the vehicle's history and chat with the agent about it.

This is useful when:
- Your mechanic wants to check what was done before
- You share a car with a spouse
- A fleet manager needs to track multiple vehicles

## By the Numbers

| Metric | Value |
|---|---|
| Python dependencies | 15 |
| Database tables | 13 |
| API routes | 60+ |
| Agent tools | 13 |
| Tests | 65 (13 test files) |
| Languages | 4 (FR/EN/DE/ES) |
| Frontend build step | None |
| License | MIT |

## Try It

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd car-carer
cp .env.example .env
# Add your ANTHROPIC_API_KEY and OPENROUTER_API_KEY to .env
docker-compose up
```

Open http://localhost:8200. Create a vehicle, upload an invoice, start chatting.

You need two API keys:
- **Anthropic** (for the chat agent) -- Claude Sonnet 4
- **OpenRouter** (for document extraction) -- Gemini Flash 2.0

Both are affordable for personal use. A typical extraction costs fractions of a cent.

**GitHub**: https://github.com/Greal-dev/car-carer

## What's Next

- Push notifications for upcoming maintenance and expiring insurance
- Cost prediction based on historical data
- Support for more extraction models (not just Gemini)
- Better offline PWA mode
- Community-contributed extraction prompts for different invoice formats

If you're a car owner drowning in invoices or a developer interested in practical AI extraction pipelines, I'd love your feedback. Issues and PRs welcome.

---

*Car Carer is MIT licensed and open source. Built with FastAPI, Claude, Gemini, Alpine.js, and Tailwind CSS.*
