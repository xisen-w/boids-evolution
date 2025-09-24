"""
AI Web Search Tool - Perform web searches using Tavily API
Created by: system
"""

from datetime import datetime
from tavily import TavilyClient
import os
from typing import Dict, Any


def execute(query: str) -> Dict[str, Any]:
    """Perform a Tavily web search and return the raw response as a dict."""
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key)
    return client.search(query=query)
    