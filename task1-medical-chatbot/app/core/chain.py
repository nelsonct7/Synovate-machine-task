"""The LangChain chain: prompt template -> Claude -> plain text."""

from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.core.llm import get_llm
from app.core.prompts import build_chat_prompt


@lru_cache
def get_chain() -> Runnable:
    """Return the shared medical-chat chain, building it only once."""
    return build_chat_prompt() | get_llm() | StrOutputParser()
