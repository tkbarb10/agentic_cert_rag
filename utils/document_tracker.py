"""
Document Tracker Utility
Tracks and logs all documents retrieved during a Gradio session
"""
import json
from datetime import datetime
from pathlib import Path

class DocumentTracker:
    """Tracks documents retrieved for each query in a session."""
    
    def __init__(self, output_dir="./session_logs"):
        """Initialize the document tracker.
        
        Args:
            output_dir: Directory to save session logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_data = []
        
    def log_query(self, query, docs, web_search_used=False, web_query=None, web_result=None):
        """Log a query and its retrieved documents.
        
        Args:
            query: The user's query
            docs: List of retrieved documents
            web_search_used: Whether web search was triggered
            web_query: The web search query if used
            web_result: The web search result if used
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_docs_retrieved": len(docs),
            "documents": [
                {
                    "doc_index": i,
                    "content": doc[:500],  # Store first 500 chars
                    "full_length": len(doc)
                }
                for i, doc in enumerate(docs, 1)
            ],
            "web_search": {
                "used": web_search_used,
                "query": web_query,
                "result": web_result
            }
        }
        self.session_data.append(entry)
        
    def save_session(self):
        """Save the entire session to a JSON file."""
        output_file = self.output_dir / f"session_{self.session_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        return output_file
    
    def get_summary(self):
        """Get a summary of the session."""
        total_queries = len(self.session_data)
        total_docs = sum(entry['num_docs_retrieved'] for entry in self.session_data)
        web_searches = sum(1 for entry in self.session_data if entry['web_search']['used'])
        
        return {
            "session_id": self.session_id,
            "total_queries": total_queries,
            "total_docs_retrieved": total_docs,
            "web_searches_performed": web_searches
        }
