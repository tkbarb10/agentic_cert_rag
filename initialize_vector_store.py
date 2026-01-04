from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import torch
from typing import Optional
from utils.kwarg_parser import parse_value

def initialize_embedding_model(model_name: str="sentence-transformers/all-MiniLM-L6-v2", encode_kwargs: dict={"normalize_embeddings": True}, show_progress: bool=True):

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )

    print(f"\nDevice being used in the embedding model is {device}\n")

    model = HuggingFaceEmbeddings(
        model_name=model_name, 
        model_kwargs={"device": device},
        encode_kwargs=encode_kwargs,
        show_progress=show_progress
        )
        
    return model


def create_vector_store(persist_path: str, collection_name: str, embedding_model=None, db_kwargs: Optional[dict]=None):
    
    db_kwargs = db_kwargs or {}

    # Extend collection metadata if the user wishes to update other parameters in the chroma client configuration or replace the distance measurement
    user_metadata = db_kwargs.pop("collection_metadata", {})
    collection_metadata={"hnsw:space": "cosine"}
    collection_metadata.update(user_metadata)

    store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=persist_path,
        collection_metadata=collection_metadata,
        **db_kwargs
    )

    return store


if __name__ == "__main__":

    embedding_model = None
    store = None
    model_name = None
    encode_kwargs = None
    show_progress = None
    persist_path = None
    collection_name = None
    db_kwargs = None

    while embedding_model is None:

        if model_name is None:

            user_choice = input("Enter the embedding model name you wish to use.  If you're ok with the default (all-MiniLM-L6-v2), just hit Enter: ")

            if user_choice == "":
                model_name = "sentence-transformers/all-MiniLM-L6-v2"
            else:
                model_name = user_choice

        if encode_kwargs is None:

            encode_kwargs = input("The default is to normalize embeddings.  Hit Enter if this is ok, type false to change: ")

            if encode_kwargs == "":
                encode_kwargs={"normalize_embeddings": True}
            else:
                encode_kwargs={"normalize_embeddings": False}

        if show_progress is None:

            show_progress = input("The default is for the model to show the progress of the embedding.  Hit Enter to leave as is, or type false if you don't wish to see a progress output: ")

            if show_progress == "":
                show_progress = True
            else:
                show_progress = False
    
        try:
            embedding_model = initialize_embedding_model(
                model_name=model_name,
                encode_kwargs=encode_kwargs,
                show_progress=show_progress
            )
        except Exception as e:
            print("Oh dear, we are experiencing technical difficulties with initializing the embedding model")
            print(f"Your mission, should you choose to accept it, is to fix this error: {e}")
            model_name = None
    
    print("Next, let's go ahead and set up the vector store.  For this, we'll be using the LangChain chromadb wrapper\n")

    while store is None:

        if persist_path is None:

            user_path = input("Type in the path you wish to save the vector store embeddings to, or hit Enter to keep the default.  The default path is ./chroma/rag_material: ")

            if user_path == "":
                persist_path = "./chroma/rag_material"
            else:
                persist_path=user_path

        if collection_name is None:

            collection_name = input("Type in what you wish to name the vector store collection, or the collection you wish to load if one already exists: ")

        if db_kwargs is None:
            add_kwargs = input("Do you wish to change any other default parameter in the Langchain Chroma() class? Type 'yes' or 'no': ")

            if add_kwargs in ['yes', 'y', 'Yes', 'YES', 'yeah', 'ya']:

                db_kwargs = {}
                user_kwargs = input("Ok then enter your parameters in this format: arg_name1=value1,arg_name2=value2: ")

                for kwarg in user_kwargs.split(","):
                    dict_pair = parse_value(kwarg)
                    if dict_pair and len(dict_pair) == 2:
                        db_kwargs[dict_pair[0]] = dict_pair[1]
                
                print(f"Here are the custom parameters that will used in the vector store {db_kwargs}")
                
            else:
                db_kwargs = {}

        try:

            store = create_vector_store(
                persist_path=persist_path, 
                embedding_model=embedding_model, 
                collection_name=collection_name, 
                db_kwargs=db_kwargs
                )
            
        except Exception as e:
            print("Oh dear, we are experiencing technical difficulties with initializing the vector store")
            print(f"Your mission, should you choose to accept it, is to fix this error: {e}")
            persist_path = None
            db_kwargs = None