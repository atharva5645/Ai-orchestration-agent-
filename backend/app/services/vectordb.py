import chromadb
from chromadb.config import Settings
from typing import List

class VectorDBService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def add_documents(self, collection_name: str, documents: List[str], ids: List[str], metadatas: List[dict] = None):
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def query(self, collection_name: str, query_texts: List[str], n_results: int = 5):
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_texts=query_texts,
            n_results=n_results
        )

vectordb_service = VectorDBService()
