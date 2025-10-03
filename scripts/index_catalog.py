import argparse
from app.rag import load_documents, split_documents, build_vector_store
from app.config import DATA_DIR

def main():
    parser = argparse.ArgumentParser(description="Index course PDFs into the vector store")
    parser.add_argument("--data_dir", type=str, default=DATA_DIR, help="Directory with PDFs/TXT/MD")
    parser.add_argument("--persist", action="store_true", help="Persist the vector store (Chroma)")
    args = parser.parse_args()

    print(f"[Index] Loading documents from: {args.data_dir}")
    docs = load_documents(args.data_dir)
    print(f"[Index] Loaded {len(docs)} docs")
    chunks = split_documents(docs)
    print(f"[Index] Split into {len(chunks)} chunks")
    vs = build_vector_store(chunks)
    print("[Index] Vector store built and ready.")

if __name__ == "__main__":
    main()
