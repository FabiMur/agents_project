from ddgs import DDGS
from strands import tool


@tool
def image_search(query: str) -> str:
    """Search the web for images related to the given query and return the URL of the first result."""
    results = DDGS().images(query, max_results=1)
    if results:
        return results[0]["image"]
    return ""
