---
sidebar_position: 7
title: Configuration
---

# Configuration

PromptVault is configured via environment variables or a `.env` file.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPTVAULT_DB_PATH` | `./promptvault.db` | SQLite database file path |
| `PROMPTVAULT_DEFAULT_PROVIDER` | `openai` | Default LLM provider |
| `OPENAI_API_KEY` | (empty) | OpenAI API key |
| `ANTHROPIC_API_KEY` | (empty) | Anthropic API key |
| `GEMINI_API_KEY` | (empty) | Google Gemini API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `EMBEDDING_PROVIDER` | `openai` | Embedding provider (reserved) |

## .env File

Copy the template:
```bash
cp .env.example .env
```

Edit with your keys:
```bash
PROMPTVAULT_DB_PATH=./promptvault.db
PROMPTVAULT_DEFAULT_PROVIDER=gemini
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=your-key-here
OLLAMA_BASE_URL=http://localhost:11434
```

## LLM Providers

### OpenAI
- **Provider name:** `openai`
- **Default model:** `gpt-4.1-mini`
- **Auth:** `OPENAI_API_KEY`
- **Models:** gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-5, gpt-5-mini, gpt-5-nano, o3, o3-mini, o4-mini

### Anthropic
- **Provider name:** `anthropic`
- **Default model:** `claude-sonnet-5`
- **Auth:** `ANTHROPIC_API_KEY`
- **Models:** claude-haiku-4-5, claude-sonnet-5, claude-opus-5, claude-opus-4-7

### Google Gemini
- **Provider name:** `gemini`
- **Default model:** `gemini-3.7-flash`
- **Auth:** `GEMINI_API_KEY`
- **Models:** gemini-3.7-flash, gemini-3.6-flash, gemini-3.5-flash, gemini-3.1-pro, gemini-3-flash, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.0-flash

### Ollama (Local)
- **Provider name:** `ollama`
- **Default model:** `llama3.2`
- **Auth:** None required
- **Setup:** Install [Ollama](https://ollama.ai), pull a model: `ollama pull llama3.2`

## Model Config Override

Any endpoint that accepts `model_config` can override defaults:

```json
{
  "provider": "gemini",
  "model": "gemini-3.7-flash",
  "temperature": 0.2,
  "max_tokens": 1024,
  "cost_per_1k_tokens": {"input": 0.001, "output": 0.002}
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `provider` | `openai` | LLM provider name |
| `model` | `gpt-4.1-mini` | Model identifier |
| `temperature` | `0.0` | Sampling temperature |
| `max_tokens` | `512` | Max output tokens |
| `cost_per_1k_tokens` | (auto) | Custom cost override `{input, output}` |

## Docker Configuration

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  -e PROMPTVAULT_DB_PATH=/app/data/promptvault.db \
  -v $(pwd)/data:/app/data \
  promptvault
```

Or with docker-compose:

```yaml
services:
  promptvault:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PROMPTVAULT_DB_PATH=/app/data/promptvault.db
    volumes:
      - ./data:/app/data
```

## Database

PromptVault uses SQLite by default. The database file is created automatically at the path specified by `PROMPTVAULT_DB_PATH`.

Tables are created on first run. No migrations needed.

To reset the database:
```bash
rm promptvault.db
```

To use a different path:
```bash
promptctl --db-path /custom/path/db.db prompt list
```
