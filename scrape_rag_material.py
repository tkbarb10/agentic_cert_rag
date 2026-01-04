from tavily import TavilyClient
from load_env import load_env
from typing import List, Dict
import math

load_env()

tavily_client = TavilyClient()

def website_map(root_url: str, instructions: str, max_depth: int=5, include_usage: bool=True, **kwargs):
    """Fetch a crawl map of URLs starting at a root location.

    Args:
        root_url: Starting URL to map.
        instructions: Provider-specific mapping instructions.
        max_depth: Maximum depth to crawl from the root URL.
        include_usage: Whether to include provider usage metadata in the response.
        **kwargs: Additional keyword arguments passed to the map request.

    Returns:
        Mapping results returned by the Tavily client.
    """

    try:
        print("Beginning map quest...")

        map_results = tavily_client.map(
        root_url,
        instructions=instructions,
        max_depth=max_depth,
        include_usage=include_usage
        )

        print("Map quest completed!")

        return map_results
    
    except Exception as e:
        print("Map quest unsuccessful")
        print(f"Thwarted by: {e}")

# returns a dict object that includes the base_url, results (list of links), usage, response time in seconds and request_id

def extract_links(url_list: List[str]) -> dict:
    """Group URLs into batches of 20 for downstream extraction.

    Args:
        url_list: Flat list of URLs to group.

    Returns:
        Dictionary mapping group names to URL lists.
    """
    url_dict = {}
    n_group = math.ceil(len(url_list) / 20)

    print(f"There are {len(url_list)} urls, dividing into {n_group} groups for content extraction")

    for i in range(n_group):
        n = i * 20
        url_dict[f"group_{i}"] = url_list[n:n + 20]
    
    return url_dict


def extract_content(url_dict: Dict[str, str]):
    """Extract raw markdown content for each URL group.

    Args:
        url_dict: Mapping of group names to lists of URLs.

    Returns:
        Dictionary of extraction results keyed by group.
    """
    result_set = {}

    for key, url_list in url_dict.items():
        
        # Initialize a list to hold results for this specific key
        key_results = []

        for url in url_list:
            try:
                # Note: We pass [url] as a list containing a single string
                result = tavily_client.extract(
                    urls=[url], 
                    include_raw_content='markdown',
                    extract_depth='advanced',
                    timeout=60,
                    include_usage=True
                )

                key_results.append(result)

            except Exception as e:
                print(f"Skipping individual URL {url} in {key} due to error: {e}")
                continue # Move to the next URL in the list

        result_set[key] = key_results

    return result_set


def raw_web_content(root_url: str, instructions: str, max_depth: int=5, include_usage: bool=True, **kwargs):
    """Map a site, extract markdown content, and return raw strings.

    Args:
        root_url: Starting URL to map.
        instructions: Provider-specific mapping instructions.
        max_depth: Maximum depth to crawl from the root URL.
        include_usage: Whether to include provider usage metadata in the response.
        **kwargs: Additional keyword arguments passed to the map request.

    Returns:
        List of raw markdown content strings from extracted pages.
    """
    map_results = website_map(
        root_url=root_url,
        instructions=instructions,
        max_depth=max_depth,
        include_usage=include_usage
    )

    url_list = map_results['results']

    url_dict = extract_links(
        url_list=url_list
    )

    result_set = extract_content(
        url_dict=url_dict
    )

    content_strings = []

    for key, value in result_set.items():
        for item in value:
            content_strings.append(item['results'][0]['raw_content'])
    
    return content_strings
