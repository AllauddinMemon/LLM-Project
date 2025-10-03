import os
from dotenv import load_dotenv

load_dotenv()

# LLM provider: 'groq' or 'gemini'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Vector store: 'chroma' or 'pinecone'
VECTOR_STORE = os.getenv("VECTOR_STORE", "chroma").lower()
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", ".chroma")

# Pinecone (optional)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "intellicourse-index")

# Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

DATA_DIR = os.getenv("DATA_DIR", "data/sample")
TOP_K = int(os.getenv("TOP_K", "4"))
