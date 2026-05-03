"""
Ingest PDFs and create vector store for RAG system.
"""
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DATA_PATH = Path(__file__).parent.parent / "data" / "raw"
VECTORSTORE_PATH = Path("C:/vectorstore_diabetes")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_documents():
    documents = []
    if not DATA_PATH.exists():
        print(f"Data path does not exist: {DATA_PATH}")
        return documents

    pdf_files = list(DATA_PATH.glob("*.pdf")) + list(DATA_PATH.glob("*.PDF"))
    if not pdf_files:
        print(f"No PDF files found in {DATA_PATH}")
        return documents

    print(f"Found {len(pdf_files)} PDF files. Loading...")
    for pdf_file in pdf_files:
        print(f"Loading {pdf_file.name}...")
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()
        for page in pages:
            page.metadata["source_file"] = pdf_file.name
        documents.extend(pages)

    print(f"Loaded {len(documents)} documents in total.")
    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks


def create_vectorstore(chunks):
    print("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("Creating vector store...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"Vector store saved to {VECTORSTORE_PATH}")
    return vectorstore


def main():
    print("=" * 50)
    print("Starting PDF ingestion pipeline...")
    print("=" * 50)

    documents = load_documents()
    if not documents:
        print("No documents to process. Exiting.")
        return

    chunks = split_documents(documents)
    create_vectorstore(chunks)

    print("=" * 50)
    print("Ingestion completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()