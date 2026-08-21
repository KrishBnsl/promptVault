# CLI Command Reference

## Global Options
- `--db-path` or `PROMPTVAULT_DB_PATH` env var to specify SQLite file
- `--verbose` for debug logging

## Prompt Commands

### promptctl prompt create
Create a new prompt with initial version.

```bash
promptctl prompt create <name> --content <text-or-file> [--description TEXT] [--variables JSON] [--model-config JSON] [--commit-message TEXT] [--tags LIST]
```

**Examples:**
```bash
promptctl prompt create summarize --content "Summarize {article} in {tone}" --variables '{"article": "string", "tone": "string"}' --model-config '{"provider": "openai", "model": "gpt-4o-mini"}' --commit-message "Initial version" --tags summarization,content

promptctl prompt create summarize --content @prompt.txt
```

### promptctl prompt update
Create the next immutable version of an existing prompt.

```bash
promptctl prompt update <name> --content <text-or-file> [--variables JSON] [--model-config JSON] [--commit-message TEXT]
```

### promptctl prompt list
List all prompts.

```bash
promptctl prompt list [--tags TAG1,TAG2] [--limit N] [--offset M] [--json]
```

### promptctl prompt show
Show prompt content and metadata.

```bash
promptctl prompt show <name> [--version N] [--json]
```

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

### promptctl prompt rollback
Rollback to a previous prompt version.

```bash
promptctl prompt rollback <name> --version N [--commit-message TEXT]
```

## Dataset Commands

### promptctl dataset create
Create a new dataset from JSONL or JSON file.

```bash
promptctl dataset create <name> --file <jsonl-or-json> [--description TEXT]
```

**File format:**
- JSONL: Each line is `{"input": {...}, "expected_output": "..."}`
- JSON: Array of such objects

### promptctl dataset list
List all datasets.

```bash
promptctl dataset list [--limit N] [--offset M] [--json]
```

## Evaluation Commands

### promptctl eval run
Run evaluation of a prompt version against a dataset.

```bash
promptctl eval run <prompt-name> --version N --dataset <dataset-name> [--model-config JSON]
```

### promptctl eval report
Get evaluation report.

```bash
promptctl eval report <evaluation-id> [--format json|table]
```

## Server Commands

### promptctl serve
Start the MCP server or REST API.

```bash
promptctl serve [--stdio|--http] [--host 127.0.0.1] [--port 8000]
```

### promptctl web
Start the optional web UI.

```bash
promptctl web [--host 127.0.0.1] [--port 8080]
```
