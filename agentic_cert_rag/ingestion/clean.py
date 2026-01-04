from ..utils.load_env import load_env
from groq import Groq
from ..utils.load_yaml_config import load_yaml_config
from ..utils.prompt_builder import build_prompt
from ..paths import PROMPT_CONFIG_FPATH
from typing import List
from ..utils.rate_limits import ping

load_env()

config = load_yaml_config(PROMPT_CONFIG_FPATH)
scrape_parts = config.get("scrape_prompt", "Clean this string of html tags and other web artifacts")
scrape_prompt = build_prompt(scrape_parts)

print(f"This is the current prompt sent to the LLM for cleaning up the raw web content: \n\n{scrape_prompt}")

# change this to accomodate different providers
client = Groq()

def create_message_payload(web_content: List[str]):
    """Build message payloads for LLM cleaning requests.

    Args:
        web_content: List of raw web content strings to clean.

    Returns:
        List of message payloads suitable for Groq chat completions.
    """
    payloads = []

    for string in web_content:
        message_payload = ([
            {"role": "system", "content": scrape_prompt},
            {"role": "user", "content": f"Raw Content:\n {string}"}
        ])

        payloads.append(message_payload)

    return payloads

def cleaned_content(web_content: List[str], model: str='openai/gpt-oss-20b', reasoning_effort: str='low', temperature: float=0.5):
    """Clean web content strings using a chat model and return joined output.

    Args:
        web_content: List of raw web content strings to clean.
        model: LLM model identifier to use.
        reasoning_effort: Provider-specific reasoning effort setting.
        temperature: Sampling temperature for the model.

    Returns:
        Combined cleaned content as a single string.
    """
    cleaned_content = []

    rate_limit = ping(model)

    message_payloads = create_message_payload(web_content=web_content)

    for i, message in enumerate(message_payloads):

        char_count = sum(len(m.get('content', '')) for m in message)
        estimated_tokens = char_count / 4

        if estimated_tokens > rate_limit:
            print(f"Web content at index {i} is estimated to be {estimated_tokens} tokens, greater than your rate limit of {rate_limit} tokens per minute.  Skipping this message and processing the rest")
            continue

        response = client.chat.completions.create(
            model=model,
            messages=message,
            reasoning_effort=reasoning_effort, # type: ignore
            temperature=temperature
        )

        cleaned_content.append(response.choices[0].message.content)
    
    cleaned_string = "\n\n".join(f"=== WEB CONTENT ===\n\n{item}" for item in cleaned_content)
    
    return cleaned_string
