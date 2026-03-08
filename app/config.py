import secrets

from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path, override=True)

# Auto-generate JWT_SECRET in .env if missing
if not any(line.startswith("JWT_SECRET=") for line in _env_path.read_text().splitlines() if line.strip()) if _env_path.exists() else True:
    _secret = secrets.token_hex(32)
    with open(_env_path, "a") as f:
        f.write(f"\nJWT_SECRET={_secret}\n")
    load_dotenv(_env_path, override=True)


class Settings(BaseSettings):
    anthropic_api_key: str
    openrouter_api_key: str
    database_url: str = "sqlite:///./care.db"
    upload_dir: str = "./uploads"
    jwt_secret: str = ""


settings = Settings()

UPLOAD_PATH = Path(settings.upload_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
