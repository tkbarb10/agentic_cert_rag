from tavily import TavilyClient
from load_env import load_env
from typing import List, Dict
import math

load_env()

tavily_client = TavilyClient()

def website_map(root_url: str, instructions: str, max_depth: int=5, include_usage: bool=True, **kwargs):

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
    url_dict = {}
    n_group = math.ceil(len(url_list) / 20)

    print(f"There are {len(url_list)} urls, dividing into {n_group} groups for content extraction")

    for i in range(n_group):
        n = i * 20
        url_dict[f"group_{i}"] = url_list[n:n + 20]
    
    return url_dict


def extract_content(url_dict: Dict[str, str]):
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

