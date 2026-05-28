import os
import asyncio
from app.tools.rag.vectorstore import get_vectorstore
from app.tools.rag.retriever import retrieve_financial_context

def run_test():
    print("Testing RAG Architecture...")
    
    # 1. Initialize Vector Store
    vectorstore = get_vectorstore()
    print("Vectorstore initialized successfully.")
    
    # 2. Insert Dummy Chunks
    from langchain_core.documents import Document
    doc1 = Document(
        page_content="Microsoft (MSFT) reported a 20% increase in Cloud revenue for Q3.",
        metadata={"ticker": "MSFT", "source_file": "msft_q3.pdf", "page": 1}
    )
    doc2 = Document(
        page_content="Apple (AAPL) iPhone sales slowed down by 5% in the Asia market.",
        metadata={"ticker": "AAPL", "source_file": "aapl_annual.pdf", "page": 4}
    )
    
    print("Inserting mock documents into ChromaDB...")
    vectorstore.add_documents([doc1, doc2])
    print("Insertion complete.")
    
    # 3. Retrieve
    print("\nRetrieving MSFT context...")
    res = retrieve_financial_context("What happened with Microsoft's cloud?", ticker="MSFT", top_k=1)
    print(res)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env.dev")
    run_test()
