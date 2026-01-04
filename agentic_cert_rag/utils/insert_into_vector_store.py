from typing import Any
from .load_files import load_files_as_list
from pathlib import Path
from .chunk_content import chunk_markdown_text


def upload_content_to_store(store: Any, documents_path: str | Path, **kwargs):
    """Load, chunk, and upload documents into a vector store.

    Args:
        store: Vector store instance with an add_documents method.
        documents_path: File or directory path containing documents to ingest.
        **kwargs: Chunking keyword arguments forwarded to chunk_markdown_text.
    """

    publications = load_files_as_list(documents_path)
    docs = chunk_markdown_text(publications, **kwargs)
    store.add_documents(docs)

    print(f"Successfully added files from {documents_path} to vector store")
