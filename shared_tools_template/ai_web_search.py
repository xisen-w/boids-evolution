"""
AI Web Search Tool - Perform web searches using Tavily API
Created by: system
"""

import os
import json
from datetime import datetime

def execute(parameters, context=None):
    """
    Execute the ai_web_search tool.
    
    Parameters:
    - query: The query to search for
    
    Returns:
    - Dictionary with search results and metadata
    """
    try:
        # Import TavilyClient
        from tavily import TavilyClient
        
        # Get query parameter
        query = parameters.get("query", "")
        if not query:
            return {
                "success": False,
                "error": "No query provided",
                "result": "Please provide a 'query' parameter"
            }
        
        # Initialize Tavily client
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "Tavily API key not found",
                "result": "Please set TAVILY_API_KEY environment variable"
            }
        
        client = TavilyClient(api_key)
        
        # Perform search
        response = client.search(query=query)
        
        # Return structured response
        return {
            "success": True,
            "query": query,
            "results": response.get("results", []),
            "follow_up_questions": response.get("follow_up_questions"),
            "answer": response.get("answer"),
            "images": response.get("images", []),
            "response_time": response.get("response_time"),
            "request_id": response.get("request_id"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": "Web search failed"
        }
    