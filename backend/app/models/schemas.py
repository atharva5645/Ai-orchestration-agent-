from pydantic import BaseModel
from typing import Optional

class ResearchRequest(BaseModel):
    query: str
    company_symbol: Optional[str] = ""

class ResearchResponse(BaseModel):
    status: str
    final_report: Optional[str] = None
    error: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    status: str
    filename: str
    ticker: str
    chunks_processed: int
    message: str
