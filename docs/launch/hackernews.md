# Title

Show HN: Car Carer -- AI-powered car maintenance tracker (self-hosted, open-source)

# URL

https://github.com/Greal-dev/car-carer

# Comment (first comment by author)

I built this because I was tired of manually entering data into car maintenance apps. The idea is simple: upload your invoices and inspection reports (PDF or photo), and AI extracts structured data automatically -- dates, mileage, parts, costs, categories. Then you can query your maintenance history in natural language through a chat agent.

The extraction uses Gemini Flash 2.0 (multimodal, via OpenRouter) and the chat uses Claude Sonnet 4 in an agentic loop with 13 tools that query the database -- it can search maintenance history, compare inspections, compute spending breakdowns, track fuel consumption, flag overdue services, and detect suspicious anomalies between consecutive inspections.

Stack: FastAPI + SQLite + Alpine.js (no build step). Runs with `docker-compose up`. MIT licensed, 65 tests, 4 languages.

The main difference from existing tools like LubeLogger: zero manual data entry. You batch-upload a folder of invoices and the AI handles the rest, including auto-filling your vehicle info (brand, model, plate number, VIN) from the documents themselves.
