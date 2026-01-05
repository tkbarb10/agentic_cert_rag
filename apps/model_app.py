from groq import Groq
import json
from tavily import TavilyClient
from config.load_env import load_env
from vector_store.retriever_tool import initialize_retriever_tool
from utils.load_yaml_config import load_yaml_config
from utils.prompt_builder import build_prompt
from utils.tavily_web_search import web_search
from config.paths import PROMPT_CONFIG_FPATH
# from utils.document_tracker import DocumentTracker  # Uncomment to use document tracking

load_env()

client = Groq()

retriever_tool = initialize_retriever_tool(
    persist_path="./store/aya_healthcare",
    collection_name="aya_healthcare_rag",
    tool_name='aya_healthcare_database',
    description="Searches through Aya Healthcare's internal scraped data. Use this for specific questions about Aya's services, policies, or website info."
)

# Initialize document tracker (optional)
# doc_tracker = DocumentTracker(output_dir="./session_logs")

def aya_gradio_chat(message, history):
    """Stream a chat completion response for a Gradio chat session with tool calling support.

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

    # Retrieve relevant documents
    docs = retriever_tool.invoke(message)

    tracked_docs = docs.split("\n\n") # build_prompt iterates through a list to add in docs.  double space is the doc separator used when creating the retriever tool
    
    # Track documents used for this query
    # print("\n" + "="*50)
    # print(f"QUERY: {message}")
    # print("="*50)
    # print(f"RETRIEVED DOCUMENTS: {len(tracked_docs)} documents")
    # for i, doc in enumerate(tracked_docs, 1):
    #     print(f"\nDoc {i}:")
    #     print(f"  Content: {doc[:200]}..." if len(doc) > 200 else f"  Content: {doc}")
    # print("="*50 + "\n")

    system_prompt = build_prompt(prompt, tracked_docs, "Self-Ask")
    
    messages = [
        {"role": "system", "content": system_prompt}
    ] + conversation_history + [{"role": "user", "content": message}]

    print(messages)

    # First API call - may trigger tool use
    response = client.chat.completions.create(
        model='openai/gpt-oss-20b',
        messages=messages, # type: ignore
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Used for searching the web for additional information about Aya Healthcare if provided context isn't enough",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "web_query": {
                                "type": "string",
                                "description": "The search query to look up on the internet"
                            }
                        },
                        "required": ["web_query"]
                    }
                }
            }
        ],
        tool_choice='auto',
        stream=True
    )
    
    output = []
    reasoning = []
    metadata = []
    tool_call = None
    web_query_used = None
    web_result_used = None

    # Stream first response and check for tool calls
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            output.append(chunk.choices[0].delta.content)
            yield "".join(output)

        if chunk.choices[0].delta.reasoning:
            reasoning.append(chunk.choices[0].delta.reasoning) 

        if chunk.choices[0].delta.tool_calls:
            tool_call = chunk.choices[0].delta.tool_calls[0]

        if chunk.usage:
            metadata.append(chunk.usage.to_dict())
    
    # If model called the web search tool
    if tool_call:
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)['web_query']
        web_query_used = args
        
        # Notify user that web search is happening
        search_notification = f"\n\n🔍 *Searching the web for: '{args}'*\n\n"
        output.append(search_notification)
        yield "".join(output)
        
        print(f"\n🔍 WEB SEARCH TRIGGERED: {args}")
        
        # Execute web search
        tool_call_content = web_search(args)
        web_result_used = tool_call_content
        print(f"📄 WEB SEARCH RESULT: {tool_call_content}\n")
        
        # Add tool call and result to messages
        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": tool_call_content
        })
        
        # Second API call with tool results
        second_response = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=messages, # type: ignore
            stream=True
        )

        # Stream second response
        for chunk in second_response:
            if chunk.choices[0].delta.content is not None:
                output.append(chunk.choices[0].delta.content)
                yield "".join(output)

            if chunk.choices[0].delta.reasoning:
                reasoning.append(chunk.choices[0].delta.reasoning) 

            if chunk.usage:
                metadata.append(chunk.usage.to_dict())
    
    # Log this query to document tracker (optional)
    # doc_tracker.log_query(
    #     query=message,
    #     docs=docs,
    #     web_search_used=tool_call is not None,
    #     web_query=web_query_used,
    #     web_result=web_result_used
    # )
    
    # Print final metadata
    print(f"\n📊 REASONING: {''.join(reasoning)}")
    print(f"📊 METADATA: {metadata}\n")

def save_session_logs():
    """Save all session logs to file. Call this at the end of your Gradio session."""
    # output_file = doc_tracker.save_session()
    # summary = doc_tracker.get_summary()
    # print(f"\n✅ Session saved to: {output_file}")
    # print(f"📊 Session summary: {summary}")
    pass  # Uncomment the lines above to use
