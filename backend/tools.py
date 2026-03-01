from duckduckgo_search import DDGS

def web_search(query: str) -> str:
    """Search the web for recipe information."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                # Format the results into a readable string
                formatted = "\n\n".join([f"{r['title']}: {r['body']}" for r in results])
                return formatted
            return "No search results found."
    except Exception as e:
        return f"Search failed: {str(e)}"
