# Title

Built a full-stack app with FastAPI + Alpine.js (no build step) -- AI extracts data from car invoices, Claude agent queries the database

# Body

Hey r/Python,

I just open-sourced a project I've been working on and wanted to share some of the technical patterns since a few of them might be interesting to this community.

**Car Carer** is a self-hosted car maintenance tracker. You upload invoices/inspection reports (PDF or photo), AI extracts structured data, and then you chat with an AI agent that queries your maintenance history. GitHub: https://github.com/Greal-dev/car-carer

Here's what I think is technically interesting:

## 1. Agentic loop with Claude (no framework)

I'm not using LangChain, LlamaIndex, or any agent framework. The agent is a plain loop using the Anthropic SDK directly:

```python
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=SYSTEM_PROMPT + context,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        max_tokens=4096,
    )

    if response.stop_reason == "tool_use":
        # Execute each tool call and feed results back
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input, db)
                messages.append(...)  # tool_result
    else:
        break  # Final text response
```

13 tools, each a pure function that takes a DB session and returns a string. No abstractions, no chains, no prompt templates. The dispatcher is a dict mapping tool names to functions. It's about 200 lines total for the entire agent.

## 2. Multi-modal extraction pipeline with Gemini

The extraction service converts PDFs to images (PyMuPDF at 200 DPI), preprocesses them (EXIF correction, contrast enhancement, sharpening via Pillow), then sends them to Gemini Flash 2.0 via OpenRouter's chat completions API with a structured JSON prompt:

```python
# PDF -> images -> base64 -> OpenRouter (Gemini Flash)
doc = fitz.open(pdf_path)
for page in doc:
    pix = page.get_pixmap(dpi=200)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    img = preprocess_image(img)  # EXIF, contrast, sharpen
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    base64_img = base64.b64encode(buffered.getvalue()).decode()
```

The prompt asks for a strict JSON schema and I parse the response with fallback extraction (regex for JSON blocks if the model wraps it in markdown). Different prompts for invoices vs. inspection reports, auto-detected from the document content.

## 3. SSE batch upload with concurrency control

Batch upload uses Server-Sent Events to stream progress back to the frontend. The backend processes N files concurrently (configurable, default 3) and sends structured SSE events for each file:

```python
async def batch_upload_sse(files, vehicle_id, db):
    semaphore = asyncio.Semaphore(settings.batch_max_concurrent)

    async def process_one(file):
        async with semaphore:
            yield sse_event("processing", {"filename": file.filename})
            result = await extract_document(file)
            yield sse_event("complete", {"filename": file.filename, ...})

    # Process all files, streaming SSE events as they complete
```

This lets you import 50+ invoices at once and watch the progress bar fill up in real-time.

## 4. Zero-build frontend

The entire frontend is Alpine.js 3 + Tailwind CSS, both loaded from CDN. One HTML file (`index.html`), one JS file (`app.js`), one CSS file. No Node, no npm, no webpack, no Vite. FastAPI serves the static files directly.

I know this isn't for everyone, but for a self-hosted tool where you control the deployment, it's incredibly freeing. Hot reload is instant (just refresh), the Docker image is tiny, and there's zero JS toolchain to maintain.

## 5. Vehicle auto-enrichment

When you upload a document, the extraction returns vehicle info (brand, model, plate number, VIN, fuel type). The backend automatically fills in any missing vehicle fields:

```python
def _enrich_vehicle(vehicle, extracted_data):
    vehicle_info = extracted_data.get("vehicle_info", {})
    if vehicle_info.get("brand") and not vehicle.brand:
        vehicle.brand = vehicle_info["brand"]
    if vehicle_info.get("plate_number") and not vehicle.plate_number:
        vehicle.plate_number = vehicle_info["plate_number"]
    # ... etc
```

So you create a vehicle with just a name ("My Car"), upload one invoice, and suddenly it knows it's a 2019 Peugeot 308 diesel with plate AB-123-CD.

## Numbers

- 15 Python dependencies (requirements.txt)
- 13 SQLAlchemy models, 13 database tables
- 60+ API routes across 5 routers
- 13 agent tools
- 65 tests, 13 test files
- 4 languages (FR/EN/DE/ES)
- MIT license

## What I'd love feedback on

- The agent architecture: is a raw loop better than using a framework? I found it simpler but I'm curious about others' experiences.
- The extraction pipeline: anyone using Gemini's vision API for document extraction? How do you handle low-quality photos?
- FastAPI + Alpine.js: anyone else doing this combo? It feels like a sweet spot for self-hosted tools.

Link: https://github.com/Greal-dev/car-carer

Happy to dive deeper into any of these patterns. Thanks for reading!
