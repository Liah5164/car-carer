from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import Base, engine
from app.routers import vehicles, documents, chat

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Care of your Car", version="0.1.0")

# API routes
app.include_router(vehicles.router)
app.include_router(documents.router)
app.include_router(chat.router)

# Static files (frontend)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def index():
    return FileResponse(str(static_dir / "index.html"))
