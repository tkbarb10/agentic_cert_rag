# Gradio Chat App with Tool Calling - Update Guide

## Summary of Changes

Your Gradio chat function has been updated to match your command-line version with the following improvements:

### ✨ New Features

1. **Tool Calling Integration**: The model can now call the `web_search` tool when it needs additional information
2. **User Notifications**: Visual feedback when web search is triggered (🔍 icon)
3. **Document Tracking**: Console logging of all retrieved documents for each query
4. **Metadata Logging**: Reasoning and usage metadata printed to console
5. **Syntax Fix**: Fixed missing comma between `tool_choice` and `stream` parameters

## What Was Fixed

### Original Error
```python
tool_choice='auto'
stream=True  # ❌ Missing comma caused syntax error
```

### Fixed Version
```python
tool_choice='auto',
stream=True  # ✅ Proper syntax
```

## Files Provided

### 1. `model_app_updated.py` (Main File)
The core implementation with:
- Tool calling support for web search
- User notifications when searching the web
- Console logging of retrieved documents
- Reasoning and metadata tracking

### 2. `document_tracker.py` (Optional Utility)
A utility class for persistent document tracking:
- Logs every query and its retrieved documents
- Tracks web search usage
- Saves session data to JSON files
- Provides session summaries

### 3. `model_app_with_tracking.py` (Enhanced Version)
Same as the main file but with document tracker integrated (commented out by default)

## How It Works

### Flow Diagram
```
User Query
    ↓
Retrieve Documents (always)
    ↓
Send to Model with retriever context
    ↓
Model Decides: Need more info?
    ├─ No → Stream response
    └─ Yes → Call web_search tool
           ↓
       Execute web search
           ↓
       Show "🔍 Searching..." to user
           ↓
       Stream final response with web data
```

### Console Output Example
```
==================================================
QUERY: What are Aya's benefits for travel nurses?
==================================================
RETRIEVED DOCUMENTS: 3 documents

Doc 1:
  Content: Aya offers comprehensive health insurance...

Doc 2:
  Content: Benefits include housing stipends...

Doc 3:
  Content: 401k matching and continuing education...
==================================================

🔍 WEB SEARCH TRIGGERED: Aya Healthcare travel nurse benefits 2024
📄 WEB SEARCH RESULT: Aya Healthcare offers competitive...

📊 REASONING: User asking about benefits...
📊 METADATA: [{'completion_tokens': 150, 'prompt_tokens': 1200, ...}]
```

## Usage

### Basic Setup (No Document Tracking)
Use `model_app_updated.py` as-is:

```python
from model_app_updated import aya_gradio_chat
import gradio as gr

demo = gr.ChatInterface(
    fn=aya_gradio_chat,
    type="messages",
    title="Aya Healthcare Assistant"
)

demo.launch()
```

### With Document Tracking
Use `model_app_with_tracking.py` and uncomment tracking lines:

```python
# In model_app_with_tracking.py

# 1. Uncomment the import
from document_tracker import DocumentTracker

# 2. Uncomment the tracker initialization
doc_tracker = DocumentTracker(output_dir="./session_logs")

# 3. Uncomment the logging in aya_gradio_chat()
doc_tracker.log_query(
    query=message,
    docs=docs,
    web_search_used=tool_call is not None,
    web_query=web_query_used,
    web_result=web_result_used
)

# 4. At the end of your Gradio session, save logs
save_session_logs()
```

### Accessing Session Logs
After your session ends:

```python
from document_tracker import DocumentTracker

# Load and analyze a session
import json
with open('./session_logs/session_20240105_143022.json') as f:
    session = json.load(f)

# See all queries and documents
for entry in session:
    print(f"Query: {entry['query']}")
    print(f"Docs retrieved: {entry['num_docs_retrieved']}")
    if entry['web_search']['used']:
        print(f"Web search: {entry['web_search']['query']}")
```

## User Experience

### Without Web Search
```
User: What is Aya Healthcare?
Assistant: Aya Healthcare is a leading travel nursing agency...
```

### With Web Search
```
User: What's Aya's stock price?
Assistant: 🔍 *Searching the web for: 'Aya Healthcare stock price'*

Based on recent data, Aya Healthcare is a privately held company...
```

## Configuration

### Adjust Number of Retrieved Documents
```python
store_retriever = store.as_retriever(
    search_type="mmr", 
    search_kwargs={"k": 5}  # Change from 3 to 5
)
```

### Adjust Document Print Length
```python
# In aya_gradio_chat()
print(f"  Content: {doc[:500]}...")  # Change from 200 to 500 chars
```

### Disable Console Logging
Comment out the print statements in `aya_gradio_chat()`:

```python
# print("\n" + "="*50)
# print(f"QUERY: {message}")
# ... etc
```

## Testing the Tool Calling

Try these queries to trigger web search:

1. **Recent/Current Info**: "What's Aya's latest news?" 
2. **Time-Sensitive**: "Aya Healthcare stock price today"
3. **Outside Knowledge Base**: "How does Aya compare to Cross Country Nurses?"

## Troubleshooting

### Web Search Not Triggering
- The model decides when to search based on the retrieved context
- If context is sufficient, it won't search (this is expected behavior)
- Try queries that explicitly ask for recent/current information

### Syntax Errors
- Make sure all comma separators are present in function parameters
- Check that `json` is imported in the function (we added `import json` at the top of `aya_gradio_chat()`)

### Document Tracker Issues
- Ensure the `session_logs/` directory has write permissions
- The tracker creates the directory automatically if it doesn't exist

## Next Steps

1. Replace your current `model_app.py` with `model_app_updated.py`
2. Test with a few queries to verify tool calling works
3. Optionally enable document tracking if you want to analyze retrieval patterns
4. Adjust console logging verbosity to your preference

## Questions?

- **Q**: Will web search slow down responses?
  **A**: Only when triggered. Most queries will use only cached documents and stream normally.

- **Q**: Can I disable web search entirely?
  **A**: Yes, just remove the `tools` parameter from the API call.

- **Q**: How do I see which documents were most useful?
  **A**: Enable document tracking and analyze the JSON logs after your session.
