---
sidebar_position: 2
title: Installation
---

# Installation

## Prerequisites

- Python 3.11+

## Quick Install (no clone needed)

```bash
pip install promptvault
```

Or with uv:
```bash
uvx promptvault
```

## From Source

```bash
git clone https://github.com/KrishBnsl/promptVault.git
cd promptVault
uv sync
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# At minimum, add one provider key:
GEMINI_API_KEY=your-key-here
# or
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

## Using pip

```bash
pip install promptvault
```

## Docker

```bash
docker build -t promptvault .
docker run -p 8000:8000 -v $(pwd)/data:/app/data promptvault
```

Or with docker-compose:

```bash
docker-compose up
```

## Verify Installation

```bash
# Test CLI
promptctl --help

# Start REST API
promptctl serve --http --port 8000

# Open Swagger docs
open http://localhost:8000/docs
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPTVAULT_DB_PATH` | `./promptvault.db` | SQLite database path |
| `PROMPTVAULT_DEFAULT_PROVIDER` | `openai` | Default LLM provider |
| `OPENAI_API_KEY` | (empty) | OpenAI API key |
| `ANTHROPIC_API_KEY` | (empty) | Anthropic API key |
| `GEMINI_API_KEY` | (empty) | Gemini API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |

## Provider Setup

### OpenAI
1. Get key at [platform.openai.com](https://platform.openai.com/api-keys)
2. Set `OPENAI_API_KEY=sk-...` in `.env`

### Anthropic
1. Get key at [console.anthropic.com](https://console.anthropic.com/)
2. Set `ANTHROPIC_API_KEY=sk-ant-...` in `.env`

### Google Gemini
1. Get key at [aistudio.google.com](https://aistudio.google.com/apikey)
2. Set `GEMINI_API_KEY=...` in `.env`

### Ollama (Local)
1. Install [Ollama](https://ollama.ai)
2. Pull a model: `ollama pull llama3.2`
3. Set `OLLAMA_BASE_URL=http://localhost:11434` (default)

## Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "promptvault": {
      "command": "promptctl",
      "args": ["serve"]
    }
  }
}
```

Restart Claude Desktop to load the server.
