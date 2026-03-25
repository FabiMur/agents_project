import json
from ddgs import DDGS
from strands import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for the given query and return a JSON string with the results."""
    try:
        results = DDGS().text(query, max_results=max_results)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Search error: {e}"
