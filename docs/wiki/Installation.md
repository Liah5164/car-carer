# Installation

## Docker (Recommended)

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd car-carer
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

Open http://localhost:8200

## Docker Pull (GHCR)

```bash
docker pull ghcr.io/greal-dev/car-carer:latest
```

## Manual Install

```bash
git clone https://github.com/Greal-dev/car-carer.git
cd car-carer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
python run.py
```

## Requirements

- Python 3.12+
- Anthropic API key (for chat) — https://console.anthropic.com
- OpenRouter API key (for extraction) — https://openrouter.ai
