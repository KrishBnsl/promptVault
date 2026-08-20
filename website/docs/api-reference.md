---
sidebar_position: 3
title: API Reference
---

# REST API Reference

**Base URL:** `http://localhost:8000/api`

Start the server:
```bash
promptctl serve --http --port 8000
```

Interactive Swagger docs at: `http://localhost:8000/docs`

---

## Prompts

### POST /api/prompts

Create a new prompt with initial version.

```bash
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "summarizer",
    "content": "Summarize this in {tone} style:\n\n{article}",
    "description": "Summarizes articles",
    "variables": {"tone": "formal|casual", "article": "string"},
    "model_config": {"provider": "openai", "model": "gpt-4o-mini"},
    "commit_message": "Initial version",
    "tags": ["nlp", "summarization"]
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "name": "summarizer",
  "description": "Summarizes articles",
  "tags": ["nlp", "summarization"],
  "current_version_id": "uuid",
  "created_at": "2026-08-20T12:00:00",
  "updated_at": "2026-08-20T12:00:00"
}
```

### GET /api/prompts

List all prompts.

```bash
# List all
curl http://localhost:8000/api/prompts

# Filter by tags
curl "http://localhost:8000/api/prompts?tags=nlp,summarization"

# Paginate
curl "http://localhost:8000/api/prompts?limit=10&offset=20"
```

### GET /api/prompts/`{name}`

Get prompt with latest version content.

```bash
curl http://localhost:8000/api/prompts/summarizer
```

**Response:**
```json
{
  "id": "uuid",
  "name": "summarizer",
  "current_version": {
    "version": 1,
    "content": "Summarize this in {tone} style:\n\n{article}",
    "variables": {"tone": "formal|casual", "article": "string"},
    "model_config": {"provider": "openai", "model": "gpt-4o-mini"}
  }
}
```

### GET /api/prompts/`{name}`/versions

List all versions of a prompt.

```bash
curl http://localhost:8000/api/prompts/summarizer/versions
```

### GET /api/prompts/`{name}`/versions/`{version}`

Get specific version.

```bash
curl http://localhost:8000/api/prompts/summarizer/versions/2
```

### POST /api/prompts/`{name}`/rollback

Rollback to a previous version. Creates a new version with the old content.

```bash
curl -X POST http://localhost:8000/api/prompts/summarizer/rollback \
  -H "Content-Type: application/json" \
  -d '{"version": 1, "commit_message": "Reverting to v1"}'
```

---

## Datasets

### POST /api/datasets

Create a new dataset.

```bash
curl -X POST http://localhost:8000/api/datasets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "qa-test",
    "description": "Q&A test cases",
    "items": [
      {"input": {"question": "What is 2+2?"}, "expected_output": "4"},
      {"input": {"question": "Capital of France?"}, "expected_output": "Paris"}
    ]
  }'
```

### GET /api/datasets

List datasets.

```bash
curl http://localhost:8000/api/datasets
```

### GET /api/datasets/`{name}`

Get dataset with all items.

```bash
curl http://localhost:8000/api/datasets/qa-test
```

---

## Evaluations

### POST /api/evaluations

Run evaluation of a prompt version against a dataset.

```bash
curl -X POST http://localhost:8000/api/evaluations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "summarizer",
    "dataset_name": "qa-test",
    "version": 1,
    "llm_config": {
      "provider": "gemini",
      "model": "gemini-3.7-flash"
    }
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "status": "completed",
  "model_config": {
    "provider": "gemini",
    "model": "gemini-3.7-flash",
    "temperature": 0.0,
    "max_tokens": 512
  }
}
```

### GET /api/evaluations/`{id}`

Get evaluation status.

```bash
curl http://localhost:8000/api/evaluations/<id>
```

### GET /api/evaluations/`{id}`/report

Get full evaluation report with all results and metrics.

```bash
curl http://localhost:8000/api/evaluations/<id>/report
```

**Response:**
```json
{
  "evaluation_id": "uuid",
  "status": "completed",
  "metrics": {
    "avg_latency_ms": 3542,
    "avg_cost": 0.000015,
    "total_tokens": {"prompt_tokens": 26, "completion_tokens": 3, "total_tokens": 29},
    "exact_match_rate": 0.5,
    "total_items": 2,
    "successful_items": 2,
    "failed_items": 0
  },
  "results": [
    {
      "input": {"question": "What is 2+2?"},
      "expected_output": "4",
      "actual_output": "4",
      "latency_ms": 1673,
      "token_usage": {"prompt_tokens": 13, "completion_tokens": 1, "total_tokens": 14},
      "cost": 0.000013,
      "scores": {"exact_match": 1.0},
      "error": null
    }
  ]
}
```
