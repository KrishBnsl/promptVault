# PromptVault

**Open-source prompt versioning, evaluation, and management as an MCP server.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-github.io-blue.svg)](https://krishbnsl.github.io/promptVault/)

## What is PromptVault?

PromptVault is a self-hosted tool for AI engineers and prompt engineers to:

- **Version prompts** like code with immutable versions and rollback support
- **Evaluate prompts** against datasets using LLM providers (OpenAI, Anthropic, Ollama)
- **Access everything** through an MCP server, CLI, or REST API

## Quickstart

### Install (no clone needed)

```bash
pip install promptvault
```

Or with uv/pipx:
```bash
uvx --from git+https://github.com/KrishBnsl/promptVault.git promptctl --help
```

Or with Docker:
```bash
docker run -p 8000:8000 -e GEMINI_API_KEY=your-key ghcr.io/krishbnsl/promptvault
```

### From Source

```bash
git clone https://github.com/KrishBnsl/promptVault.git
cd promptVault
uv sync
cp .env.example .env
# Edit .env with your API keys
```

### Create Your First Prompt

```bash
promptctl prompt create summarize \
  --content "Summarize the following article in {tone} style:\n\n{article}" \
  --description "Summarizes an article" \
  --variables '{"tone": "concise", "article": "string"}' \
  --model-config '{"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.2}' \
  --tags "summarization,content"
```

### Create a Dataset

```bash
echo '{"input": {"article": "AI is transforming..."}, "expected_output": "AI transforms..."}' > dataset.jsonl
promptctl dataset create article-summaries --file dataset.jsonl
```

### Run Evaluation

```bash
promptctl eval run summarize --dataset article-summaries
```

### Use with MCP (Claude Desktop)

Add to your Claude Desktop config:

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

## CLI Reference

```bash
promptctl prompt create <name> --content <text> [options]
promptctl prompt list [--tags TAGS] [--limit N]
promptctl prompt show <name> [--version N]
promptctl prompt versions <name>
promptctl prompt diff <name> <version-a> <version-b>
promptctl prompt rollback <name> --version N

promptctl dataset create <name> --file <jsonl-or-json>
promptctl dataset list

promptctl eval run <prompt-name> --dataset <dataset-name>
promptctl eval report <evaluation-id>

promptctl serve [--stdio|--http] [--port 8000]
promptctl web [--port 8080]
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `prompt_create` | Create a new prompt with initial version |
| `prompt_get` | Retrieve a prompt version |
| `prompt_list` | List all prompts |
| `prompt_versions` | List all versions of a prompt |
| `prompt_diff` | Diff two prompt versions |
| `prompt_rollback` | Rollback to a previous version |
| `dataset_create` | Create a dataset |
| `dataset_list` | List datasets |
| `dataset_get` | Get dataset with items |
| `evaluation_run` | Run evaluation |
| `evaluation_status` | Check evaluation status |
| `evaluation_report` | Get evaluation report |
| `evaluation_compare` | Compare two evaluations |

## REST API

**Base URL:** `http://localhost:8000/api`

```bash
# Create a prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "content": "Hello {name}"}'

# List prompts
curl http://localhost:8000/api/prompts

# Get a prompt
curl http://localhost:8000/api/prompts/test
```

## Configuration

Copy `.env.example` to `.env` and configure:

```
PROMPTVAULT_DB_PATH=./promptvault.db
PROMPTVAULT_DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
```

## Architecture

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   MCP Client │   │     CLI     │   │  REST Client │
│ (Claude etc) │   │ (promptctl) │   │ (curl, apps) │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────┐
│              PromptVault Core                   │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │ Versioning  │ │ Evaluation   │ │ Storage  │ │
│  │ Engine      │ │ Engine       │ │ Layer    │ │
│  └─────────────┘ └──────────────┘ └──────────┘ │
│  ┌──────────────────────────────────────────┐  │
│  │        SQLite Database (local)           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Documentation

📖 **Full docs:** https://krishbnsl.github.io/promptVault/

- [Getting Started](https://krishbnsl.github.io/promptVault/docs/intro)
- [API Reference](https://krishbnsl.github.io/promptVault/docs/api-reference)
- [CLI Reference](https://krishbnsl.github.io/promptVault/docs/cli-reference)
- [MCP Tools](https://krishbnsl.github.io/promptVault/docs/mcp-tools)
- [Agent Docs (llms.txt)](https://raw.githubusercontent.com/KrishBnsl/promptVault/main/llms.txt)

## License

MIT License - see [LICENSE](LICENSE) for details.
