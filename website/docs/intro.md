---
sidebar_position: 1
title: Introduction
---

# PromptVault

**Open-source prompt versioning, evaluation, and management as an MCP server.**

PromptVault is a self-hosted tool for AI engineers and prompt engineers to:

- **Version prompts** like code with immutable versions, diffs, and rollback
- **Evaluate prompts** against datasets using LLMs (OpenAI, Anthropic, Gemini, Ollama)
- **Track costs** with built-in pricing for 23+ models
- **Access everything** through an MCP server, CLI, or REST API

## Why PromptVault?

Managing prompts across teams is hard. Prompts live in spreadsheets, Slack messages, or scattered files. There's no version history, no way to compare changes, and no systematic way to evaluate quality.

PromptVault fixes this by treating prompts as first-class artifacts:

| Problem | PromptVault Solution |
|---------|---------------------|
| Prompts scattered across files | Centralized SQLite database |
| No version history | Immutable versions with diffs |
| Manual testing | Automated evaluation against datasets |
| No cost visibility | Automatic cost tracking per evaluation |
| Lock-in to one interface | MCP + CLI + REST API |

## Quick Example

```bash
# Create a prompt
promptctl prompt create summarize \
  --content "Summarize in {tone} style: {article}" \
  --variables '{"tone": "formal|casual", "article": "string"}'

# Create a test dataset
echo '{"input": {"article": "AI is transforming..."}, "expected_output": "AI transforms..."}' > data.jsonl
promptctl dataset create test-data --file data.jsonl

# Run evaluation with Gemini
promptctl eval run summarize --dataset test-data \
  --model-config '{"provider": "gemini", "model": "gemini-3.7-flash"}'

# See results
promptctl eval report <evaluation-id>
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

## Three Interfaces

### MCP Server (Primary)
The main interface. Add to Claude Desktop or any MCP client:
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
→ [MCP Tools Reference](/docs/mcp-tools)

### CLI (`promptctl`)
Full-featured command-line tool:
```bash
promptctl prompt create my-prompt --content "Hello {name}"
```
→ [CLI Reference](/docs/cli-reference)

### REST API
HTTP API for web apps and integrations:
```bash
curl http://localhost:8000/api/prompts
```
→ [API Reference](/docs/api-reference)

## Next Steps

- [Installation](/docs/installation) — Get started in 2 minutes
- [API Reference](/docs/api-reference) — All 12 REST endpoints
- [MCP Tools](/docs/mcp-tools) — All 14 MCP tools
- [Evaluation](/docs/evaluation) — How evals work + pricing
