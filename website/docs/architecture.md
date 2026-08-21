---
sidebar_position: 8
title: Architecture
---

# Architecture

## Overview

PromptVault is a local-first, MCP-first prompt management system. It stores everything in a single SQLite database and exposes three interfaces: MCP server (primary), CLI, and REST API.

## System Design

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

## Core Components

### Versioning Engine (`core/versioning.py`)
- Creates prompts with initial versions
- Manages immutable version history
- Handles rollback (creates new version with old content)
- Lists prompts with tag filtering

### Evaluation Engine (`core/evaluation.py`)
- Runs prompts against datasets
- Substitutes variables in prompt templates
- Calls LLM providers for each dataset item
- Scores results (exact match)
- Computes cost from built-in pricing table
- Aggregates metrics across results

### Storage Layer (`db/`)
- SQLAlchemy 2.x ORM with SQLite
- CRUD operations (`db/crud.py`)
- Session management (`db/engine.py`)

### LLM Providers (`core/providers.py`)
- Abstract `LLMProvider` base class
- Four implementations: OpenAI, Anthropic, Ollama, Gemini
- Factory function `get_provider(name)` for provider selection
- Uniform interface: `generate(prompt, model, temperature, max_tokens)`

## Data Model

### Prompts & Versions

```
Prompt (1) ──── (many) PromptVersion
   │                      │
   │ current_version_id ──┘
   │
   └── tags: JSON array
```

- **Prompt**: Named entity with metadata. Unique name.
- **PromptVersion**: Immutable snapshot. Numbered sequentially. Content is the prompt template with `{variable}` placeholders.

### Datasets

```
Dataset (1) ──── (many) DatasetItem
```

- **Dataset**: Named collection of test cases.
- **DatasetItem**: Input dict + expected output string.

### Evaluations

```
Evaluation (1) ──── (many) EvaluationResult
       │
       ├── FK to PromptVersion
       └── FK to Dataset
```

- **Evaluation**: A run of a prompt version against a dataset. Tracks status, model config, and aggregated metrics.
- **EvaluationResult**: Per-item result with actual output, scores, latency, cost, and errors.

## Key Design Decisions

### Immutable Versions
Prompt versions are never modified. Updates create new versions. Rollbacks also create new versions (with old content). This provides a complete audit trail.

### Local-First
Everything runs locally. No cloud dependency. The SQLite database lives on your machine. LLM calls go directly to provider APIs.

### MCP-First
The MCP server is the primary interface. CLI and REST API are alternative access methods that share the same core engine.

### Extensible Providers
Adding a new LLM provider requires:
1. Create a class inheriting `LLMProvider`
2. Implement `generate(prompt, model, temperature, max_tokens)`
3. Register in `get_provider()`
4. Add models to `COST_TABLE`

## File Structure

```
promptvault/
├── src/
│   ├── config.py          # Settings, env vars
│   ├── main.py            # CLI entry point
│   ├── api/
│   │   ├── main.py        # FastAPI app
│   │   ├── routes.py      # API endpoints
│   │   └── schemas.py     # Pydantic models
│   ├── cli/
│   │   └── commands.py    # Typer CLI
│   ├── core/
│   │   ├── diffing.py     # Version diffing
│   │   ├── evaluation.py  # Eval engine + cost table
│   │   ├── providers.py   # LLM providers
│   │   └── versioning.py  # Version management
│   ├── db/
│   │   ├── crud.py        # Database operations
│   │   ├── engine.py      # SQLAlchemy setup
│   │   └── models.py      # ORM models
│   ├── mcp_server/
│   │   └── server.py      # MCP server (14 tools)
│   └── web/
│       └── index.html     # Optional web UI
├── tests/                  # 28 tests
├── pyproject.toml          # Project config
├── Dockerfile              # Docker build
├── docker-compose.yml      # Docker compose
├── llms.txt                # Agent-readable overview
├── llms-full.txt           # Agent full reference
└── .env.example            # Env template
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Package Manager | uv |
| Database | SQLAlchemy 2.x + SQLite |
| API Framework | FastAPI + Uvicorn |
| CLI Framework | Typer |
| MCP SDK | mcp 2.0 |
| Validation | Pydantic v2 |
| Testing | pytest |
| Linting | Ruff |
| Build | Hatchling |
