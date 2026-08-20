---
sidebar_position: 4
title: CLI Reference
---

# CLI Reference

CLI name: `promptctl`

## Global Options

```bash
promptctl --db-path /path/to/db.db  # Custom database path
promptctl --verbose                  # Verbose output
```

---

## Prompt Commands

### promptctl prompt create

Create a new prompt with initial version.

```bash
promptctl prompt create <name> \
  --content "Hello {name}" \
  --description "A greeting prompt" \
  --variables '{"name": "string"}' \
  --model-config '{"provider": "openai", "model": "gpt-4o-mini"}' \
  --commit-message "Initial version" \
  --tags "greeting,test"
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--content` | `-c` | Yes | Prompt content (supports `@file` syntax) |
| `--description` | `-d` | No | Human description |
| `--variables` | | No | JSON dict of variable definitions |
| `--model-config` | | No | JSON dict of LLM configuration |
| `--commit-message` | `-m` | No | Version commit message |
| `--tags` | | No | Comma-separated tags |

**Reading from file:**
```bash
promptctl prompt create my-prompt --content @prompts/template.txt
```

### promptctl prompt list

List all prompts.

```bash
promptctl prompt list [--tags "tag1,tag2"] [--limit 50] [--offset 0] [--json]
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--tags` | | None | Filter by comma-separated tags |
| `--limit` | `-l` | 50 | Max results |
| `--offset` | `-o` | 0 | Pagination offset |
| `--json` | | false | Output as JSON |

### promptctl prompt show

Show prompt content and metadata.

```bash
promptctl prompt show <name> [--version 2] [--json]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--version` | `-v` | Specific version (default: latest) |
| `--json` | | Output as JSON |

### promptctl prompt versions

List all versions of a prompt.

```bash
promptctl prompt versions <name> [--json]
```

### promptctl prompt diff

Show diff between two prompt versions.

```bash
promptctl prompt diff <name> <version-a> <version-b>
```

Example output:
```diff
--- summarizer:v1
+++ summarizer:v2
@@ -1 +1 @@
-Summarize this in {tone} style:
+Summarize this article concisely in {tone} style:
```

### promptctl prompt rollback

Rollback to a previous version.

```bash
promptctl prompt rollback <name> --version 1 --commit-message "Reverting to v1"
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--version` | `-v` | Yes | Target version to rollback to |
| `--commit-message` | `-m` | No | Commit message |

---

## Dataset Commands

### promptctl dataset create

Create dataset from JSONL or JSON file.

```bash
promptctl dataset create <name> --file data.jsonl --description "Test data"
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--file` | `-f` | Yes | Path to JSONL or JSON file |
| `--description` | `-d` | No | Human description |

**JSONL format** (one JSON object per line):
```
{"input": {"question": "What is 2+2?"}, "expected_output": "4"}
{"input": {"question": "Capital of France?"}, "expected_output": "Paris"}
```

**JSON format:**
```json
[
  {"input": {"question": "What is 2+2?"}, "expected_output": "4"},
  {"input": {"question": "Capital of France?"}, "expected_output": "Paris"}
]
```

### promptctl dataset list

List all datasets.

```bash
promptctl dataset list [--limit 50] [--offset 0] [--json]
```

---

## Evaluation Commands

### promptctl eval run

Run evaluation of a prompt version against a dataset.

```bash
promptctl eval run <prompt-name> \
  --dataset <dataset-name> \
  --version 1 \
  --model-config '{"provider": "gemini", "model": "gemini-3.7-flash"}'
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--dataset` | `-d` | Yes | Dataset name |
| `--version` | `-v` | No | Specific prompt version (default: latest) |
| `--model-config` | | No | JSON model config override |

### promptctl eval report

Get evaluation report.

```bash
promptctl eval report <evaluation-id> --format table
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--format` | `-f` | json | Output format: `json` or `table` |

---

## Server Commands

### promptctl serve

Start the MCP server or REST API.

```bash
# MCP server over stdio (default)
promptctl serve

# REST API over HTTP
promptctl serve --http --port 8000
```

| Flag | Default | Description |
|------|---------|-------------|
| `--stdio` | true | Run MCP server over stdio |
| `--http` | false | Run REST API over HTTP |
| `--port` | 8000 | HTTP port |
