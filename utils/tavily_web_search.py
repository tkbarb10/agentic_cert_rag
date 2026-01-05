from tavily import TavilyClient
from config.load_env import load_env

load_env()
tavily_client = TavilyClient()

def web_search(web_query):
    """Execute web search using Tavily API.
    
    Args:
        web_query: The search query string
        
    Returns:
        String containing the search result answer
    """
    response = tavily_client.search(web_query, include_answer=True, max_results=3)
    return response.get("answer", "Tell user that no additional information could be found for their query")