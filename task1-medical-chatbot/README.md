# Task 1 — Medical Domain Chatbot

A domain-specific medical information chatbot built with **LangChain** and **FastAPI**.

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
| `POST` | `/api/v1/chat` | Ask a medical question |
| `DELETE` | `/api/v1/chat/{session_id}` | Forget a conversation |

### Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-1", "message": "What are the common symptoms of iron deficiency?"}'
```

Send a second message with the **same `session_id`** — e.g. `"And in children?"` — and the reply
will stay on topic, because the stored history is re-sent with each request.

## How the requirements are met

| Requirement | Where |
|---|---|
| FastAPI backend | `app/main.py`, `app/api/routes/` |
| LangChain LLM workflow | `app/core/chain.py` — `prompt \| llm \| parser` |
| Medical domain | `app/core/prompts.py`, `app/core/guardrails.py` |
| Reusable components | 15 modules, largest 68 lines; `main.py` contains no business logic |
| Prompt templates | `app/core/prompts.py` |
| LLM integration | `app/core/llm.py` |
| Conversation handling | `app/core/memory.py` |
| Context-aware responses | `MessagesPlaceholder("history")` in the prompt |
| Validation & error handling | `app/schemas/`, `app/exceptions.py`, `app/api/errors.py` |

## Architecture

```
api/routes/  ->  core/service.py  ->  core/chain.py  ->  core/llm.py
   (HTTP)         (orchestration)      (LangChain)       (Anthropic)
                        |
                   core/memory.py, core/guardrails.py
```

Each layer knows only about the one below it. Swapping Claude for another provider is a change
to `core/llm.py` and `config.py` only.

## Safety

The assistant provides general health information. It does not diagnose, does not give dosages,
and appends a disclaimer to every in-domain answer. Off-topic questions are refused.
