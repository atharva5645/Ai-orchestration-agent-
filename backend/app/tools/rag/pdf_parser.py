import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.tools.rag.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)

def ingest_pdf(file_path: str, asset_ticker: str):
    """
    Parses a PDF, chunks it using a financial-optimized text splitter, 
    and inserts it into ChromaDB.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found at {file_path}")

    logger.info(f"Loading PDF from {file_path}...")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Financial documents have large tables and dense paragraphs.
    # A chunk size of 1500 with 300 overlap ensures we don't sever tables in half.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    logger.info("Splitting document into chunks...")
    chunks = text_splitter.split_documents(documents)

    # Attach metadata for retrieval filtering
    for chunk in chunks:
        chunk.metadata["ticker"] = asset_ticker.upper()
        chunk.metadata["source_file"] = os.path.basename(file_path)

    logger.info(f"Generated {len(chunks)} chunks. Inserting into ChromaDB...")
    
    if not chunks:
        logger.warning("No text could be extracted from this PDF.")
        return 0

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    
    logger.info("Ingestion complete.")
    return len(chunks)
