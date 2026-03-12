# Project Memory System

Persistent, queryable project knowledge derived from git history. Gives AI coding agents context about decisions, patterns, conventions, and debt — so they stop rediscovering what's already known.

## Quick Start

```bash
cd .agent/memory

# One-time setup — creates venv, installs deps, creates .env
./scripts/install

# Set your API key
# Edit .env and paste your OpenRouter key (https://openrouter.ai/keys)

# Build memories from recent commits (test run)
./project-memory build --limit 20

# Verify it worked
./project-memory inspect stats
```

The script auto-activates its local `.venv` — no need to specify the venv python path.

## Requirements

- Python 3.10+
- `OPENROUTER_API_KEY` env var (for build mode)

Everything else is handled by `scripts/install`.

## Usage

```bash
# MCP server over stdio (for AI agent integration)
./project-memory serve

# Incremental build — processes commits since last build
./project-memory build
./project-memory build --limit 20     # limit to N commits

# Full rebuild — drops everything, reprocesses all history
./project-memory rebuild

# Debug/inspect raw data
./project-memory inspect help
./project-memory inspect tables
./project-memory inspect memories
./project-memory inspect memory 1
./project-memory inspect stats
./project-memory inspect schema
./project-memory inspect fts
./project-memory inspect builds
```

## MCP Tools

When running in `serve` mode, the following tools are available to AI agents:

| Tool | Purpose |
| ---- | ------- |
| `memory_query_file` | Query memories by file path or directory |
| `memory_search` | Full-text search across memory summaries |
| `memory_get` | Get a specific memory by ID with linked memories |
| `memory_stats` | Overview of the knowledge store |
| `memory_inspect` | Debug/inspect system internals |

## Configuration

| Env Var | Default | Purpose |
| ------- | ------- | ------- |
| `OPENROUTER_API_KEY` | *(required for build)* | API key for LLM calls |
| `MEMORY_BUILD_MODEL` | `google/gemini-2.0-flash-001` | Model for memory extraction |
| `MEMORY_BUILD_API_URL` | `https://openrouter.ai/api/v1/chat/completions` | API endpoint |

Verified models: `google/gemini-2.0-flash-001`, `google/gemini-2.0-flash-lite-001`, `openai/gpt-4o-mini`, `google/gemini-2.5-flash`.

## Git Integration

**Auto-build on merge** (optional):

```bash
git config core.hooksPath .githooks
```

This enables the `post-merge` hook which runs `build` and commits the updated DB automatically. The hook uses the venv Python if available, falls back to system `python3`.

**Structured commits** — use the `/commit` workflow to generate git messages with trailers that produce richer memories:

```
Type: feature|fix|refactor|config|debt|docs|test
Rationale: why this approach
Confidence: high|medium|low
```

## Testing

```bash
cd .agent/memory
./scripts/install  # if not already done
.venv/bin/pip install pytest
.venv/bin/python -m pytest tests/ -v
```

## Architecture

Single file (`project-memory`), SOLID class design:

| Class | Responsibility |
| ----- | -------------- |
| `Database` | SQLite + schema + FTS5 |
| `MemoryStore` | CRUD, file queries, full-text search |
| `LinkStore` | Bidirectional memory relationships |
| `BuildMetaStore` | Build run tracking |
| `DecayEngine` | Importance decay (0.95× per unaccessed cycle) |
| `GitLogParser` | Parses `git log` output + trailers |
| `LLMClient` | OpenRouter API via `requests` |
| `BuildAgent` | Commits → LLM → memories → decay |
| `Inspector` | Debug/inspect raw data |
| `McpServer` | 5 tools over stdio |

Data lives in `project_memory.db` (SQLite, committed to repo, marked binary via `.gitattributes`).
