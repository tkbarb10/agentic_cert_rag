from groq import Groq
import os
from dotenv import load_dotenv
import chromadb
from utils.load_yaml_config import load_yaml_config
from utils.prompt_builder import build_prompt
from config.paths import PROMPT_CONFIG_FPATH

load_dotenv()

groq_api = os.getenv('GROQ_API_KEY')

chroma_client = chromadb.PersistentClient()
store = chroma_client.get_collection(name='aya_healthcare')

client = Groq(
    api_key=groq_api
    )

def aya_gradio_chat(message, history):
    """Stream a chat completion response for a Gradio chat session.

    Args:
        message: Latest user message text.
        history: Gradio chat history list of message dicts with roles and content.

    Yields:
        Incremental assistant response chunks as strings.
    """

    prompt = load_yaml_config(PROMPT_CONFIG_FPATH)['basic_prompt']
    
    conversation_history = []
    for msg in history:
        if msg['role'] == 'user':
            conversation_history.append({"role": "user", "content": msg['content'][0]['text']})
        else:
            conversation_history.append({"role": "assistant", "content": msg['content'][0]['text']})

    helpful_docs = store.query(
    query_texts=[message],
    n_results=5
    )

    flat_docs = helpful_docs['documents'][0] # type: ignore
    system_prompt = build_prompt(prompt, flat_docs, "Self-Ask")
    print(system_prompt)
    
    messages = [
        {"role": "system", "content": system_prompt}
    ] + conversation_history + [{"role": "user", "content": message}]

    response = client.chat.completions.create(
        model='openai/gpt-oss-20b',
        messages=messages, # type: ignore
        stream=True
        )
    
    output = []
    reasoning = []
    metadata = []

    for chunk in response:

        if chunk.choices[0].delta.content != None:
            output.append(chunk.choices[0].delta.content)
            yield "".join(output)

        if chunk.choices[0].delta.reasoning:
            reasoning.append(chunk.choices[0].delta.reasoning) 

        if chunk.usage:
            metadata.append(chunk.usage.to_dict())
    
    print(f"Reasoning: {"".join(reasoning)}")
    print(f"Metadata: {metadata}")
