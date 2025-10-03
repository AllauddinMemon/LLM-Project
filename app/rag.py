from typing import List, Optional, Tuple, Dict, Any
import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# Pinecone optional
try:
    from langchain_community.vectorstores import Pinecone as PineconeVectorStore
    import pinecone
    HAVE_PINECONE = True
except Exception:
    HAVE_PINECONE = False

from langchain.schema import Document

from .config import (
    EMBEDDING_MODEL,
    VECTOR_STORE,
    CHROMA_PERSIST_DIR,
    PINECONE_API_KEY,
    PINECONE_ENV,
    PINECONE_INDEX_NAME,
)

def load_documents(data_dir: str) -> List[Document]:
    docs: List[Document] = []
    for path in Path(data_dir).rglob("*"):
        if path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(path))
            for d in loader.load():
                # ensure metadata has source and page
                d.metadata.setdefault("source", path.name)
                d.metadata.setdefault("page", d.metadata.get("page", 0))
                docs.append(d)
        elif path.suffix.lower() in {".txt", ".md"}:
            loader = TextLoader(str(path), encoding="utf-8")
            for d in loader.load():
                d.metadata.setdefault("source", path.name)
                d.metadata.setdefault("page", 0)
                docs.append(d)
    return docs

def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(docs)

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def build_vector_store(chunks: List[Document]):
    embeddings = get_embeddings()
    if VECTOR_STORE == "chroma":
        vs = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        vs.persist()
        return vs
    elif VECTOR_STORE == "pinecone":
        if not HAVE_PINECONE:
            raise RuntimeError("Pinecone not installed. Please install pinecone-client and langchain-community.")
        if PINECONE_API_KEY is None:
            raise RuntimeError("PINECONE_API_KEY not set.")
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        vs = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=PINECONE_INDEX_NAME,
        )
        return vs
    else:
        raise ValueError(f"Unsupported VECTOR_STORE: {VECTOR_STORE}")

def load_vector_store():
    """Load a persisted vector store (Chroma) or connect to Pinecone index."""
    embeddings = get_embeddings()
    if VECTOR_STORE == "chroma":
        return Chroma(
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
    elif VECTOR_STORE == "pinecone":
        if not HAVE_PINECONE:
            raise RuntimeError("Pinecone not installed.")
        if PINECONE_API_KEY is None:
            raise RuntimeError("PINECONE_API_KEY not set.")
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        return PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings,
        )
    else:
        raise ValueError(f"Unsupported VECTOR_STORE: {VECTOR_STORE}")
