"""
AI Web Search Tool - Perform web searches
Created by: system
"""

from tavily import TavilyClient
import os

def execute(parameters, context=None):
    """
    Execute the ai_web_search tool.
    
    Parameters:
    - query: The query to search for
    """
    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    response = client.search(
        query=parameters.get("query")
    )
    return response
    