# Shim for langchain-community expecting 'ddgs' instead of 'duckduckgo_search'
from duckduckgo_search import DDGS

__all__ = ["DDGS"]
