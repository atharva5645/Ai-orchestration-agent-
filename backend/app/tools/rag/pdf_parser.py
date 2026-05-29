import os
import time
import logging
from langchain_community.document_loaders import PyMuPDFLoader
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

    start_time = time.time()
    logger.info(f"Loading PDF from {file_path} using PyMuPDF...")
    
    # PyMuPDF is significantly faster than PyPDFLoader for parsing
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    
    parse_time = time.time() - start_time
    logger.info(f"PDF parsed in {parse_time:.2f} seconds.")

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
        return 0, 0.0

    vectorstore = get_vectorstore()
    
    batch_size = 100
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    embed_start_time = time.time()
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(chunks))
        batch = chunks[start_idx:end_idx]
        
        logger.info(f"Embedding batch {i+1}/{total_batches}...")
        vectorstore.add_documents(batch)
    
    embed_time = time.time() - embed_start_time
    total_time = time.time() - start_time
    
    logger.info(f"Ingestion complete! Embedded in {embed_time:.2f}s. Total pipeline time: {total_time:.2f}s.")
    return len(chunks), total_time
