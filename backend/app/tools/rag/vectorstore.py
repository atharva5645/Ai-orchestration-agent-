import os
import logging
from langchain_chroma import Chroma
from app.tools.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

# Store Chroma DB locally in the project root
CHROMA_PERSIST_DIR = os.path.join(os.getcwd(), "chroma_db")
COLLECTION_NAME = "financial_reports"

class VectorStoreManager:
    _instance = None

    @classmethod
    def get_vectorstore(cls):
        if cls._instance is None:
            logger.info(f"Initializing ChromaDB vector store at {CHROMA_PERSIST_DIR}...")
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
            
            cls._instance = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=get_embeddings(),
                persist_directory=CHROMA_PERSIST_DIR
            )
            logger.info("ChromaDB vector store loaded.")
        return cls._instance

get_vectorstore = VectorStoreManager.get_vectorstore
