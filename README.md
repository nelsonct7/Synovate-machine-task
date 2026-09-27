# Synnovate Machine Task

Three LLM applications built with **LangChain**, **LangGraph** and **FastAPI**, backed by
Anthropic's Claude models. Each task is a self-contained project with its own dependencies,
configuration and README.

| Task | Folder | What it is |
|---|---|---|
| 1 | [`task1-medical-chatbot/`](task1-medical-chatbot/) | Medical-domain chatbot with conversation memory and safety guardrails (LangChain) |
| 2 | [`task2-multi-agent/`](task2-multi-agent/) | Two-agent research workflow: a Researcher gathers, an Analyst writes a structured summary (LangGraph) |
| 3 | [`task3-advanced-agents/`](task3-advanced-agents/) | Three-agent research assistant with routing, custom tools and SQLite-backed memory (LangGraph) |

See each folder's README for its endpoints, workflow and how it meets the task requirements.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- An Anthropic API key from https://console.anthropic.com

## Running a task

Every task starts the same way. Run these commands from inside the task's folder:

```bash
cd task1-medical-chatbot     # or task2-multi-agent / task3-advanced-agents
cp .env.example .env         # Windows: Copy-Item .env.example .env
                             # then paste your Anthropic API key into .env
uv sync
uv run uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive API docs.

All three tasks default to port 8000. To run more than one at a time, give each its own port,
for example `uv run uvicorn app.main:app --reload --port 8001`.

## Repository layout

Each task follows the same structure:

```
task*/
├── app/
│   ├── main.py          # FastAPI app; no business logic
│   ├── config.py        # Settings loaded from .env
│   ├── exceptions.py    # Domain exceptions
│   ├── api/             # Routes and error handlers
│   ├── schemas/         # Request/response models (Pydantic)
│   └── core/ or graph/  # The LangChain chain or LangGraph workflow
├── .env.example
├── pyproject.toml
└── README.md
```

Task 3 also has `app/tools/` (web search, knowledge base, calculator), `app/memory/` and
`data/knowledge_base/`.

`.env` files are git-ignored. Only `.env.example` is committed.
