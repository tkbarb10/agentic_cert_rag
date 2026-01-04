import tiktoken

def get_token_count(model: str, content: str) -> int:

    encoding = tiktoken.encoding_for_model(model)
    num_tokens = encoding.encode(content)
    return len(num_tokens)