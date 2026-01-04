from utils.load_yaml_config import load_yaml_config
from utils.prompt_builder import build_prompt
from load_env import load_env
import os
from paths import PROMPT_CONFIG_FPATH, OUTPUTS_DIR
from groq import Groq
from utils.token_count import get_token_count

load_env()

# change this to accomodate different providers
client = Groq()

config = load_yaml_config(PROMPT_CONFIG_FPATH)
prep_parts = config.get("prep_prompt", "Prep this string for storage into a vector database by removing redundant information and categorizing sections")
prep_prompt = build_prompt(prep_parts)

print(f"This is the system prompt sent to the LLM to prepare the web content string for storage:\n\n{prep_prompt}")

# make sure output is in markdown format

def prepare_web_content(cleaned_content: str, model: str='openai/gpt-oss-120b', reasoning_effort: str='high', **kwargs):
    """Send cleaned web content to the LLM for preprocessing and save output.

    Args:
        cleaned_content: Cleaned web content string to preprocess.
        model: LLM model identifier to use.
        reasoning_effort: Provider-specific reasoning effort setting.
        **kwargs: Additional keyword arguments forwarded to the LLM call.

    Returns:
        Tuple of usage statistics and reasoning text when a response is saved.
    """

    num_tokens = get_token_count(model=model, content=cleaned_content)

    user_response = input(f"The content you wish to prep is {num_tokens} tokens, do you wish to proceed with sending web content to the language model?: ")

    if user_response.lower() in ['yes', 'y', 'ya', 'yeah', 'sure', 'yee']:

        message = [
            {"role": "system", "content": prep_prompt},
            {"role": "user", "content": cleaned_content}
        ]

        print("Sending web content to the model, this may take a second...")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=message, # type: ignore
                reasoning_effort=reasoning_effort, # type: ignore
                **kwargs
            )

            print(f"Response returned, please see output at {OUTPUTS_DIR}")

            updated_content = response.choices[0].message.content
            usage_stats = dict(response.usage) # type: ignore
            reasoning = response.choices[0].message.reasoning

            with open(os.path.join(OUTPUTS_DIR, 'prepped_rag_material.md'), "w", encoding='utf-8') as f:
                f.write(updated_content) # type: ignore

            return usage_stats, reasoning
        
        except Exception as e:
            print(f"Sorry, the request could not be completed.  This is the error: {e}.  Please take care of this and try again")
