from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from backend.rag.embeddings import get_embeddings
import os
import json

def initialize_vector_store():
    persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/vectordb")
    
    clinic_info_path = os.path.join(os.path.dirname(__file__), "../../data/clinic_info.json")
    
    if os.path.exists(clinic_info_path):
        with open(clinic_info_path, 'r') as f:
            clinic_data = json.load(f)
        
        documents = []
        for item in clinic_data.get("faqs", []):
            doc = Document(
                page_content=f"Q: {item['question']}\nA: {item['answer']}",
                metadata={"source": "clinic_faq", "question": item['question']}
            )
            documents.append(doc)
        
        for key, value in clinic_data.get("info", {}).items():
            doc = Document(
                page_content=f"{key}: {value}",
                metadata={"source": "clinic_info", "category": key}
            )
            documents.append(doc)
        
        embeddings = get_embeddings()
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        return vector_store
    else:
        embeddings = get_embeddings()
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

def get_vector_store():
    persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/vectordb")
    embeddings = get_embeddings()
    
    if not os.path.exists(persist_directory) or not os.listdir(persist_directory):
        print("Vector store not found. Initializing...")
        return initialize_vector_store()
    
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
