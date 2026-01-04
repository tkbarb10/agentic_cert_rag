import tiktoken

def get_token_count(model: str, content: str) -> int:
    """Return the token count for content using the model's tokenizer.

    Args:
        model: Model name used to select the tokenizer.
        content: Text content to tokenize.

    Returns:
        Number of tokens in the content.
    """

    encoding = tiktoken.encoding_for_model(model)
    num_tokens = encoding.encode(content)
    return len(num_tokens)
