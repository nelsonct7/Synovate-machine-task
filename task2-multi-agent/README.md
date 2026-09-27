# Task 2 — Multi-Agent Research System

A two-agent research workflow built with **LangGraph** and served over **FastAPI**. A Research
Agent gathers information on a topic; an Analyst Agent turns it into a structured summary.

## Quick start

```bash
cp .env.example .env        # then paste your Anthropic API key into it
uv sync
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/api/v1/research` | Run the two-agent research workflow on a topic |

### Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "CRISPR gene editing for sickle cell disease"}'
```

The response contains:

- `summary` — the Analyst's structured output: `overview`, `key_findings`, `implications`,
  `open_questions` and `confidence` (`low` / `medium` / `high`). This is the final answer.
- `research_notes` — the Research Agent's intermediate notes, returned so the hand-off between
  the two agents is visible.

## Workflow

```
START -> researcher -> analyst -> END
```

| Agent | Reads from state | Writes to state | Responsibility |
|---|---|---|---|
| Research Agent | `topic` | `research_notes` | Gathers facts, figures and open debates. Never concludes. |
| Analyst Agent | `topic`, `research_notes` | `summary` | Interprets the notes into a structured summary. Never researches. |

The agents communicate **only through the shared state** (`app/graph/state.py`). Each state key
has exactly one writer, which keeps their responsibilities separate.

## How the requirements are met

| Requirement | Where |
|---|---|
| LangGraph workflow | `app/graph/builder.py` — two nodes, three edges |
| Two agents with separate roles | `app/graph/nodes/researcher.py`, `app/graph/nodes/analyst.py` |
| Role separation via prompts | `app/graph/prompts.py` — one system prompt per agent |
| State passing between agents | `app/graph/state.py` (`ResearchState`) |
| Structured final response | `ResearchSummary` in `app/schemas/research.py`, enforced with `with_structured_output` |
| FastAPI backend | `app/main.py`, `app/api/routes/` |
| Validation & error handling | `app/schemas/`, `app/exceptions.py`, `app/api/errors.py` |

## Architecture

```
api/routes/  ->  graph/service.py  ->  graph/builder.py  ->  graph/nodes/*  ->  graph/llm.py
   (HTTP)         (orchestration)        (LangGraph)          (agents)          (Anthropic)
```

The route knows nothing about LangGraph, and the graph knows nothing about HTTP.

Each agent requests the model settings its own job needs: the Researcher runs at low reasoning
effort (gathering), the Analyst at medium (interpretation).

## Error handling

| Situation | Status | `error` |
|---|---|---|
| Invalid or blank topic | 422 | `validation_error` |
| Model unreachable or request failed | 503 | `llm_unavailable` |
| Researcher produced no notes, or no summary was produced | 500 | `graph_execution_failed` |
| Anything unexpected | 500 | `internal_error` |

Every error is returned as `{"error": ..., "detail": ...}`, never as a stack trace.
