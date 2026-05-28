import logging
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

# We use all-MiniLM-L6-v2 because it's extremely fast, small (~80MB), 
# and runs locally without hitting API rate limits.
MODEL_NAME = "all-MiniLM-L6-v2"

class LocalEmbeddings:
    _instance = None

    @classmethod
    def get_embeddings(cls):
        """Returns a singleton instance of the HuggingFace embeddings model."""
        if cls._instance is None:
            logger.info(f"Loading local embedding model: {MODEL_NAME}...")
            cls._instance = HuggingFaceEmbeddings(model_name=MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        return cls._instance

# Expose a ready-to-use instance getter
get_embeddings = LocalEmbeddings.get_embeddings
