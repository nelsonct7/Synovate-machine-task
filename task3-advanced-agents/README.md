# Task 3 — Advanced Multi-Agent Research Assistant

A three-agent research assistant built with **LangGraph** and served over **FastAPI**. A Router
agent decides how each question is handled, a Research agent gathers information using custom
tools of its own choosing, and an Analyst agent writes the final structured answer. Completed
research is stored in SQLite, so a repeat question skips the research workflow entirely.

## Quick start

```bash
cp .env.example .env        # then paste your Anthropic API key into it
uv sync
uv run uvicorn app.main:app --reload
```

Run the server from this folder. The knowledge base (`data/knowledge_base/`) and the memory
database (`data/memory.db`, created on startup) are resolved relative to it.

Open http://127.0.0.1:8000/docs

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/api/v1/assistant` | Ask the research assistant a question |
| `DELETE` | `/api/v1/assistant/{session_id}` | Forget a session's messages and findings |

### Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/assistant \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-1", "question": "What is the Atlas Enterprise uptime SLA?"}'
```

Send the **same question again with the same `session_id`**. The second response shows
`"route": "answer_from_memory"`, `"from_memory": true` and an empty `tools_used` list. The
Researcher and its tools did not run.

Each response has two parts:

- `answer` — `summary`, `key_points`, `caveats`, `confidence`
- `execution` — `route`, `route_reason`, `agents_run`, `tools_used`, `from_memory`, so you can
  see which parts of the system actually ran

## Workflow

```
START -> recall -> router --+-- "research" ----------> researcher <--> tools
                            |                               |
                            |                               v
                            +-- "direct_answer" ---------> analyst -> END
                            |                               ^
                            +-- "answer_from_memory" -------+
```

| Step | Type | Responsibility |
|---|---|---|
| `recall` | Plain code, no LLM | Loads recent conversation and shortlists past findings by keyword overlap |
| `router` | Agent 1 | Chooses `research`, `answer_from_memory` or `direct_answer` |
| `researcher` | Agent 2 | Calls tools in a loop until it has enough, then writes research notes |
| `tools` | LangGraph `ToolNode` | Executes the tool calls the Researcher requested |
| `analyst` | Agent 3 | Produces the final structured answer from whatever material the route supplied |

## Tools

The Research Agent chooses which tools to call, if any. The API never calls a tool directly.

| Tool | File | Use |
|---|---|---|
| `web_search` | `app/tools/web_search.py` | Current and external information, via DuckDuckGo. No API key needed. |
| `knowledge_base_search` | `app/tools/knowledge_base.py` | Synnovate's internal documents in `data/knowledge_base/` |
| `calculator` | `app/tools/calculator.py` | Exact arithmetic. Parses the expression safely with `ast`, never `eval`. |

To add a tool, add it to `ALL_TOOLS` in `app/tools/registry.py`. No change to the agents, the
graph or the API is needed.

### Sample questions

| Question | Expected route and tools |
|---|---|
| "What is the Atlas Enterprise uptime SLA?" | `research` → `knowledge_base_search` |
| "By what percentage did events processed grow from Q4 2025 to Q1 2026?" | `research` → `knowledge_base_search`, `calculator` |
| "What's the latest news on EU AI regulation?" | `research` → `web_search` |
| "Hi, what can you do?" | `direct_answer`, no tools |
| Any earlier question, repeated in the same session | `answer_from_memory`, no tools |

## Memory

Memory is stored in SQLite (`app/memory/store.py`) so it survives a restart. There are two tables:

- **`messages`**: every question and answer, per session. The last few turns go to the Router and
  the Analyst, which keeps answers aware of the conversation.
- **`findings`**: completed research notes, per session. These let later questions skip the
  research workflow.

Deciding whether a stored finding answers a new question works in two stages:

1. **Cheap shortlist (`app/memory/recall.py`).** Keyword overlap picks at most 3 candidate
   findings. No LLM call is made.
2. **One judgement (the Router).** The Router sees the candidates and decides whether one
   genuinely covers the question. If it names a finding that isn't in the shortlist, the
   workflow falls back to fresh research rather than answering from nothing.

## How the requirements are met

| Requirement | Where |
|---|---|
| Custom tools | `app/tools/` — web search, knowledge base, calculator |
| Agent-driven tool calling | `bind_tools` in `app/graph/nodes/researcher.py`; loop via `tools_condition` in `builder.py` |
| Memory & conversation context | `app/memory/store.py`, `app/graph/nodes/recall.py` |
| Conditional routing | `add_conditional_edges` in `app/graph/builder.py`; decision in `app/graph/nodes/router.py` |
| Skipping work already done | `answer_from_memory` route; evidence in the `execution` block of the response |
| Structured output | `AssistantAnswer`, `RouteDecision` in `app/schemas/` |
| FastAPI backend | `app/main.py`, `app/api/routes/` |
| Validation & error handling | `app/schemas/`, `app/exceptions.py`, `app/api/errors.py` |

## Architecture

```
api/routes/  ->  graph/service.py  ->  graph/builder.py  ->  graph/nodes/*  ->  graph/llm.py
   (HTTP)       (orchestration +        (LangGraph)          (agents)          (Anthropic)
                 memory writes)                                  |
                                                        tools/*, memory/*
```

The Router and Researcher run at low reasoning effort. Routing runs on every request, so it needs
to be fast and cheap. The Analyst runs at medium effort because it writes the answer the user
sees.

## Error handling

| Situation | Status | `error` |
|---|---|---|
| Invalid session id or blank question | 422 | `validation_error` |
| Model unreachable or request failed | 503 | `llm_unavailable` |
| Workflow finished without an answer | 500 | `graph_execution_failed` |
| Anything unexpected | 500 | `internal_error` |

A failed web search does not abort the request. The tool returns the failure as text, and the
Researcher carries on with what it has.

Every error is returned as `{"error": ..., "detail": ...}`, never as a stack trace.
