from langchain_community.tools import DuckDuckGoSearchRun

# Simple web search tool using DuckDuckGo (no API key needed)
search = DuckDuckGoSearchRun()

def web_search(query: str) -> str:
    """Search the web for recipe information."""
    try:
        result = search.run(query)
        return result
    except Exception as e:
        return f"Search failed: {str(e)}"
