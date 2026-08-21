---
sidebar_position: 5
title: MCP Tools
---

# MCP Tools Reference

PromptVault exposes 14 tools and 4 resources via MCP (Model Context Protocol) over stdio.

**Server name:** `pvlt-mcp`

## Setup

Add to your MCP client config (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "pvlt": {
      "command": "promptctl",
      "args": ["serve"]
    }
  }
}
```

---

## Prompt Tools

### prompt_create

Create a new prompt with initial version.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Unique prompt name |
| `content` | string | Yes | Prompt template with `{variable}` placeholders |
| `description` | string | No | Human description (default: "") |
| `variables` | object | No | Variable definitions, e.g. `{"name": "string"}` |
| `model_config` | object | No | LLM config, e.g. `{"provider": "openai", "model": "gpt-4o-mini"}` |
| `commit_message` | string | No | Version commit message |
| `tags` | array | No | Classification tags |

**Example:**
```json
{
  "name": "code-reviewer",
  "content": "Review this code:\n{code}\nLanguage: {language}",
  "variables": {"code": "string", "language": "string"},
  "tags": ["code-review", "dev"]
}
```

### prompt_update

Create the next immutable version of an existing prompt.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Existing prompt name |
| `content` | string | Yes | New prompt content |
| `variables` | object | No | Variables; inherits when omitted |
| `model_config` | object | No | Model configuration; inherits when omitted |
| `commit_message` | string | No | Description of the change |

### prompt_get

Retrieve a specific version of a prompt.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Prompt name |
| `version` | integer | No | Version number (default: latest) |

### prompt_list

List all prompts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tags` | array | No | Filter by tags (AND logic) |
| `limit` | integer | No | Max results (default: 50) |
| `offset` | integer | No | Pagination offset (default: 0) |

### prompt_versions

List all versions of a prompt.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Prompt name |

### prompt_diff

Show diff between two prompt versions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Prompt name |
| `version_a` | integer | Yes | First version number |
| `version_b` | integer | Yes | Second version number |

### prompt_rollback

Rollback to a previous version. Creates a new version with the old content.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Prompt name |
| `version` | integer | Yes | Target version to rollback to |
| `commit_message` | string | No | Commit message |

---

## Dataset Tools

### dataset_create

Create a new dataset from items.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Unique dataset name |
| `items` | array | Yes | Array of `{"input": {...}, "expected_output": "..."}` |
| `description` | string | No | Human description |

### dataset_list

List datasets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max results (default: 50) |
| `offset` | integer | No | Pagination offset |

### dataset_get

Get a dataset with all items.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Dataset name |

---

## Evaluation Tools

### evaluation_run

Run evaluation of a prompt version against a dataset.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt_name` | string | Yes | Prompt name |
| `dataset_name` | string | Yes | Dataset name |
| `version` | integer | No | Specific version (default: latest) |

### evaluation_status

Check status of an evaluation run.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `evaluation_id` | string | Yes | Evaluation ID |

### evaluation_report

Get full evaluation report with results and metrics.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `evaluation_id` | string | Yes | Evaluation ID |

**Returns:**
- `evaluation_id`, `status`, `model_config`
- `metrics`: `avg_latency_ms`, `avg_cost`, `total_tokens`, `exact_match_rate`, `total_items`, `successful_items`, `failed_items`
- `results`: Array of `{input, expected_output, actual_output, latency_ms, token_usage, cost, scores, error}`

### evaluation_compare

Compare two evaluation runs side by side.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `evaluation_id_a` | string | Yes | First evaluation ID |
| `evaluation_id_b` | string | Yes | Second evaluation ID |

---

## MCP Resources

Resources provide read-only access to data via URI patterns.

| URI Pattern | Description |
|-------------|-------------|
| `prompt://{name}/latest` | Latest version of a prompt |
| `prompt://{name}/version/{version}` | Specific version of a prompt |
| `dataset://{dataset_name}` | Dataset with all items |
| `evaluation://{evaluation_id}/report` | Full evaluation report |
