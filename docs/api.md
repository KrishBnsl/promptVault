# REST API Documentation

**Base URL:** `http://localhost:8000/api`

## Prompts

### Create Prompt
```
POST /api/prompts
```
**Body:**
```json
{
  "name": "string (required)",
  "content": "string (required)",
  "description": "string",
  "variables": {"key": "type"},
  "model_config": {"provider": "openai", "model": "gpt-4o-mini"},
  "commit_message": "string",
  "tags": ["tag1"]
}
```

### List Prompts
```
GET /api/prompts?tags=tag1&limit=50&offset=0
```

### Get Prompt
```
GET /api/prompts/{name}
```

### List Versions
```
GET /api/prompts/{name}/versions
```

### Create Version
```
POST /api/prompts/{name}/versions
```
**Body:**
```json
{
  "content": "updated prompt content",
  "variables": {},
  "model_config": {},
  "commit_message": "Describe the change"
}
```

### Get Version
```
GET /api/prompts/{name}/versions/{version}
```

### Rollback
```
POST /api/prompts/{name}/rollback
```
**Body:**
```json
{
  "version": 1,
  "commit_message": "Rollback to v1"
}
```

## Datasets

### Create Dataset
```
POST /api/datasets
```
**Body:**
```json
{
  "name": "string (required)",
  "description": "string",
  "items": [{"input": {}, "expected_output": "string"}]
}
```

### List Datasets
```
GET /api/datasets?limit=50&offset=0
```

### Get Dataset
```
GET /api/datasets/{name}
```

## Evaluations

### List Evaluations
```
GET /api/evaluations
```

### Run Evaluation
```
POST /api/evaluations
```
**Body:**
```json
{
  "prompt_name": "string (required)",
  "version": 1,
  "dataset_name": "string (required)",
  "model_config": {}
}
```

### Get Evaluation Status
```
GET /api/evaluations/{id}
```

### Get Evaluation Report
```
GET /api/evaluations/{id}/report
```
