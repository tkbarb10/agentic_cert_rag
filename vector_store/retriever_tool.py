from vector_store.initialize import create_vector_store, initialize_embedding_model
from langchain_core.tools import create_retriever_tool

def initialize_retriever_tool(persist_path: str, collection_name: str, tool_name: str, description: str):

    embedding_model = initialize_embedding_model(show_progress=False) # the tqdm progress bar doesn't work with gradio

    store = create_vector_store(
        persist_path=persist_path,
        collection_name=collection_name,
        embedding_model=embedding_model
    )

    store_retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 3})

    retriever_tool = create_retriever_tool(
        retriever=store_retriever,
        name=tool_name,
        description=description,
        response_format="content_and_artifact"
    )

    return retriever_tool