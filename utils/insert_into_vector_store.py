from typing import Any
from utils.load_files import load_files_as_list
from pathlib import Path
from utils.chunk_content import chunk_markdown_text


def upload_content_to_store(store: Any, documents_path: str | Path, **kwargs):

    publications = load_files_as_list(documents_path)
    docs = chunk_markdown_text(publications, **kwargs)
    store.add_documents(docs)

    print(f"Successfully added files from {documents_path} to vector store")