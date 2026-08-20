# MCP Tools & Resources

## Tools

### prompt_create
Create a new prompt with initial version.

**Input:**
```json
{
  "name": "string (required)",
  "content": "string (required)",
  "description": "string (optional)",
  "variables": {"key": "type"} (optional),
  "model_config": {"provider": "openai", "model": "gpt-4o-mini"} (optional),
  "commit_message": "string (optional)",
  "tags": ["tag1", "tag2"] (optional)
}
```

### prompt_get
Retrieve a specific version of a prompt.

**Input:**
```json
{
  "name": "string (required)",
  "version": "integer (optional, default: latest)"
}
```

### prompt_list
List all prompts.

**Input:**
```json
{
  "tags": ["tag1"] (optional),
  "limit": 50 (optional),
  "offset": 0 (optional)
}
```

### prompt_versions
List all versions of a prompt.

**Input:**
```json
{
  "name": "string (required)"
}
```

### prompt_diff
Show diff between two prompt versions.

**Input:**
```json
{
  "name": "string (required)",
  "version_a": "integer (required)",
  "version_b": "integer (required)"
}
```

### prompt_rollback
Rollback to a previous prompt version.

**Input:**
```json
{
  "name": "string (required)",
  "version": "integer (required)",
  "commit_message": "string (optional)"
}
```

### dataset_create
Create a new dataset from items.

**Input:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "items": [{"input": {}, "expected_output": "string"}] (required)
}
```

### dataset_list
List datasets.

**Input:**
```json
{
  "limit": 50 (optional),
  "offset": 0 (optional)
}
```

### dataset_get
Get a dataset with items.

**Input:**
```json
{
  "name": "string (required)"
}
```

### evaluation_run
Run evaluation of a prompt version against a dataset.

**Input:**
```json
{
  "prompt_name": "string (required)",
  "version": "integer (optional)",
  "dataset_name": "string (required)",
  "model_config": {} (optional)
}
```

### evaluation_status
Check status of an evaluation run.

**Input:**
```json
{
  "evaluation_id": "string (required)"
}
```

### evaluation_report
Get full evaluation report with results and metrics.

**Input:**
```json
{
  "evaluation_id": "string (required)"
}
```

### evaluation_compare
Compare two evaluation runs.

**Input:**
```json
{
  "evaluation_id_a": "string (required)",
  "evaluation_id_b": "string (required)"
}
```

## Resources

| URI Pattern | Description |
|-------------|-------------|
| `prompt://{name}/latest` | Get latest version of a prompt |
| `prompt://{name}/version/{version}` | Get specific version content |
| `dataset://{dataset_name}` | Get dataset items as JSON |
| `evaluation://{evaluation_id}/report` | Get evaluation report as JSON |
