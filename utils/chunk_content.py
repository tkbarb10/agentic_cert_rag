from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from typing import List

def chunk_markdown_text(paper_content: str | List[str], chunk_size: int=750, chunk_overlap: int=50):
    """Split markdown text into chunks using header-aware splitting.

    Args:
        paper_content: Markdown string or list of markdown strings to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap size between chunks.

    Returns:
        Flattened list of chunked documents.
    """

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Main Topic"), ("##", "Subtopic")]
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )

    docs = []

    if isinstance(paper_content, list):
        for content in paper_content:

            markdown_docs = markdown_splitter.split_text(content)
            text_docs = text_splitter.split_documents(markdown_docs)
            docs.append(text_docs)
    
    else:
        markdown_docs = markdown_splitter.split_text(paper_content)
        text_docs = text_splitter.split_documents(markdown_docs)
        docs.append(text_docs)
        
    return sum(docs, [])
