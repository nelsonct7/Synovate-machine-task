"""The tools available to the Research Agent.

One list, imported wherever tools are needed. Adding a tool to the system means adding
it here - not editing the agent, the graph, or the API.
"""

from langchain_core.tools import BaseTool

from app.tools.calculator import calculator
from app.tools.knowledge_base import knowledge_base_search
from app.tools.web_search import web_search

ALL_TOOLS: list[BaseTool] = [web_search, knowledge_base_search, calculator]
