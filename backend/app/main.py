from fastapi import FastAPI
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Backend for Financial Deep Research Agent",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    from app.api.routes import health, research, documents
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(research.router, prefix="/api/v1/research", tags=["research"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

    @app.get("/")
    async def root():
        return {"message": f"Welcome to the {settings.app_name} API"}

    return app

app = create_app()
