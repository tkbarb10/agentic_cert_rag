from load_env import load_env
from groq import Groq
from utils.load_yaml_config import load_yaml_config
from utils.prompt_builder import build_prompt
from typing import List
from utils.rate_limits import ping

load_env()

config = load_yaml_config("prompts/prompt.yaml")
scrape_parts = config.get("scrape_prompt", "Clean this string of html tags and other web artifacts")
scrape_prompt = build_prompt(scrape_parts)

print(f"This is the current prompt sent to the LLM for cleaning up the raw web content: \n\n{scrape_prompt}")

# change this to accomodate different providers
client = Groq()

def create_message_payload(web_content: List[str]):
    payloads = []

    for string in web_content:
        message_payload = ([
            {"role": "system", "content": scrape_prompt},
            {"role": "user", "content": f"Raw Content:\n {string}"}
        ])

        payloads.append(message_payload)

    return payloads

def cleaned_content(web_content: List[str], model: str='openai/gpt-oss-20b', reasoning_effort: str='low', temperature: float=0.5):
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