from groq import Groq
from load_env import load_env

load_env()

client = Groq()

def ping(model: str):
    """Ping the model to retrieve the token rate limit header.

    Args:
        model: LLM model identifier to query.

    Returns:
        Token rate limit value from the response headers.
    """
    ping = client.chat.completions.with_raw_response.create(
        messages=[{"role": "user", "content": "p"}],
        model=model, 
        max_completion_tokens=1 
    )

    return ping.headers.get('x-ratelimit-limit-tokens')
