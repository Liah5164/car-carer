# Configuration

All settings are in `.env`. Copy `.env.example` to get started.

## Required

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude (chat assistant) |
| `OPENROUTER_API_KEY` | API key for Gemini Flash (document extraction) |

## Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./care.db` | Database connection string |
| `UPLOAD_DIR` | `./uploads` | Upload directory |
| `JWT_EXPIRE_HOURS` | `72` | JWT token expiration |
| `BATCH_MAX_CONCURRENT` | `3` | Max concurrent batch extractions |
| `BATCH_MAX_FILES` | `100` | Max files per batch upload |
| `EXTRACTION_TIMEOUT` | `60` | Extraction API timeout (seconds) |
| `EXTRACTION_MODEL` | `google/gemini-2.5-flash` | Model for document extraction |
| `MAX_PHOTO_SIZE_MB` | `10` | Max vehicle photo size |

## Getting API Keys

### Anthropic (Claude)
1. Go to https://console.anthropic.com
2. Create an account
3. Generate an API key
4. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### OpenRouter (Gemini)
1. Go to https://openrouter.ai
2. Create an account
3. Add credits ($5 is enough for hundreds of extractions)
4. Generate an API key
5. Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-...`
