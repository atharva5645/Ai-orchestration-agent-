import logging
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"

class LocalEmbeddings:
    _instance = None

    @classmethod
    def get_embeddings(cls):
        """Returns a singleton instance of the HuggingFace embeddings model."""
        if cls._instance is None:
            logger.info(f"Loading highly-optimized local embedding model: {MODEL_NAME}...")
            # We explicitly pass a larger encode batch size to speed up CPU inference
            cls._instance = HuggingFaceEmbeddings(
                model_name=MODEL_NAME,
                encode_kwargs={'batch_size': 128}
            )
            logger.info("Embedding model loaded successfully.")
        return cls._instance

# Expose a ready-to-use instance getter
get_embeddings = LocalEmbeddings.get_embeddings
