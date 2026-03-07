from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# Force .env to override system env vars
load_dotenv(Path(__file__).parent.parent / ".env", override=True)


class Settings(BaseSettings):
    anthropic_api_key: str
    openrouter_api_key: str
    database_url: str = "sqlite:///./care.db"
    upload_dir: str = "./uploads"


settings = Settings()

UPLOAD_PATH = Path(settings.upload_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
