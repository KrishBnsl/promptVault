---
sidebar_position: 6
title: Evaluation
---

# Evaluation Engine

PromptVault's evaluation engine runs your prompts against datasets using LLMs, scores the results, and tracks costs.

## How It Works

1. **Load** the prompt version and dataset
2. **Substitute** variables: `{question}` → actual input values
3. **Call** the LLM for each dataset item
4. **Score** results (exact match by default)
5. **Track** latency, token usage, and cost
6. **Aggregate** metrics across all items

## Running an Evaluation

### Via CLI
```bash
promptctl eval run my-prompt \
  --dataset my-data \
  --model-config '{"provider": "gemini", "model": "gemini-3.7-flash"}'
```

### Via API
```bash
curl -X POST http://localhost:8000/api/evaluations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "my-prompt",
    "dataset_name": "my-data",
    "llm_config": {"provider": "gemini", "model": "gemini-3.7-flash"}
  }'
```

### Via MCP
```
evaluation_run(prompt_name="my-prompt", dataset_name="my-data")
```

## Metrics

| Metric | Description |
|--------|-------------|
| `exact_match_rate` | Fraction of outputs matching expected (case-insensitive, stripped) |
| `avg_latency_ms` | Average response time in milliseconds |
| `avg_cost` | Average cost per item in USD |
| `total_tokens` | Aggregate `{prompt_tokens, completion_tokens, total_tokens}` |
| `total_items` | Total dataset items evaluated |
| `successful_items` | Items completed without error |
| `failed_items` | Items that errored |

## Scoring

Default scorer: **exact match** (case-insensitive, whitespace-stripped).

```python
# "Paris." vs "Paris" → 0.0 (punctuation mismatch)
# "Paris" vs "Paris"  → 1.0 (match)
# "paris" vs "Paris"  → 1.0 (case-insensitive)
```

Custom scoring can be added via the `model_config.cost_per_1k_tokens` override for cost, or by extending the evaluation engine.

## Cost Calculation

Cost is computed automatically based on the model name using the built-in cost table.

**Formula:**
```
cost = (prompt_tokens / 1000) * input_price + (completion_tokens / 1000) * output_price
```

### Override Cost
Provide custom prices in `model_config`:
```json
{
  "provider": "openai",
  "model": "my-custom-model",
  "cost_per_1k_tokens": {"input": 0.001, "output": 0.002}
}
```

## Pricing Table (per 1K tokens, August 2026)

### OpenAI

| Model | Input | Output |
|-------|-------|--------|
| gpt-4o | $0.0025 | $0.01 |
| gpt-4o-mini | $0.00015 | $0.0006 |
| gpt-4.1 | $0.002 | $0.008 |
| gpt-4.1-mini | $0.0004 | $0.0016 |
| gpt-4.1-nano | $0.0001 | $0.0004 |
| gpt-5 | $0.00125 | $0.01 |
| gpt-5-mini | $0.00025 | $0.002 |
| gpt-5-nano | $0.00005 | $0.0004 |
| o3 | $0.002 | $0.008 |
| o3-mini | $0.0011 | $0.0044 |
| o4-mini | $0.0011 | $0.0044 |

### Anthropic

| Model | Input | Output |
|-------|-------|--------|
| claude-haiku-4-5 | $0.001 | $0.005 |
| claude-sonnet-5 | $0.002 | $0.01 |
| claude-opus-5 | $0.005 | $0.025 |
| claude-opus-4-7 | $0.005 | $0.025 |

### Google Gemini

| Model | Input | Output |
|-------|-------|--------|
| gemini-3.7-flash | $0.00075 | $0.00375 |
| gemini-3.6-flash | $0.00075 | $0.00375 |
| gemini-3.5-flash | $0.0015 | $0.009 |
| gemini-3.1-pro | $0.002 | $0.012 |
| gemini-3-flash | $0.0005 | $0.003 |
| gemini-2.5-flash | $0.00015 | $0.0006 |
| gemini-2.5-flash-lite | $0.0001 | $0.0004 |
| gemini-2.0-flash | $0.0001 | $0.0004 |

## Comparing Evaluations

Run the same prompt with different models or configurations, then compare:

```bash
# Run with Gemini
promptctl eval run my-prompt --dataset test \
  --model-config '{"provider": "gemini", "model": "gemini-3.7-flash"}'
# → eval-id-1

# Run with OpenAI
promptctl eval run my-prompt --dataset test \
  --model-config '{"provider": "openai", "model": "gpt-4.1-mini"}'
# → eval-id-2

# Compare
curl http://localhost:8000/api/evaluations/eval-id-1/report
curl http://localhost:8000/api/evaluations/eval-id-2/report
```

## Example Output

```json
{
  "metrics": {
    "avg_latency_ms": 3542,
    "avg_cost": 0.000015,
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
      "scores": {"exact_match": 1.0},
      "cost": 0.000013,
      "latency_ms": 1673
    },
    {
      "input": {"question": "Capital of France?"},
      "expected_output": "Paris",
      "actual_output": "Paris.",
      "scores": {"exact_match": 0.0},
      "cost": 0.000017,
      "latency_ms": 5412
    }
  ]
}
```

Note: The second result scored 0.0 because the LLM added a period ("Paris." vs "Paris"). This is the expected behavior of exact match scoring — it catches formatting differences.
