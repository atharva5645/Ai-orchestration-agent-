import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import DocumentUploadResponse
from app.tools.rag.pdf_parser import ingest_pdf

logger = logging.getLogger(__name__)

router = APIRouter()

# Temporary storage for uploaded PDFs before ingestion
UPLOAD_DIR = os.path.join(os.getcwd(), "temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    ticker: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint to securely upload financial PDFs (Annual Reports, 10-Ks).
    It temporarily saves the file to disk, runs it through the RAG chunking pipeline,
    and inserts the semantic embeddings into ChromaDB with ticker metadata.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # 1. Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File {file.filename} saved to {file_path}. Initiating RAG ingestion for {ticker}...")
        
        # 2. Ingest into ChromaDB
        chunks_inserted, time_taken = ingest_pdf(file_path, ticker)
        
        return DocumentUploadResponse(
            status="success",
            filename=file.filename,
            ticker=ticker.upper(),
            chunks_processed=chunks_inserted,
            time_taken=time_taken,
            message="Document successfully embedded into local ChromaDB."
        )

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 3. Clean up the temporary file to preserve disk space and security
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")

@router.post("/reset")
async def reset_vectorstore():
    try:
        from app.tools.rag.vectorstore import VectorStoreManager
        
        # If the DB is loaded in memory, try to delete the collection first 
        # to bypass Windows SQLite file lock (WinError 32) issues.
        if hasattr(VectorStoreManager, "_instance") and VectorStoreManager._instance is not None:
            try:
                VectorStoreManager._instance.delete_collection()
            except Exception as e:
                logger.warning(f"Failed to delete collection via API: {e}")
            VectorStoreManager._instance = None
            
        import shutil
        chroma_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 
            "..", "..", "..", "chroma_db")
        )
        
        if os.path.exists(chroma_path):
            try:
                shutil.rmtree(chroma_path)
            except Exception as e:
                logger.warning(f"Could not remove chroma_db completely (likely file lock): {e}")
                
        if not os.path.exists(chroma_path):
            os.makedirs(chroma_path, exist_ok=True)
        
        return {"status": "success", "message": "Vector DB reset complete"}
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
