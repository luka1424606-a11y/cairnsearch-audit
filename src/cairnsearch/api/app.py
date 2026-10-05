"""FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from cairnsearch.config import get_config
from cairnsearch.db import Database
from cairnsearch.queue import WorkerPool
from cairnsearch.watcher import FolderWatcher
from cairnsearch.indexer import IndexManager

from .routes import search, status, documents, index, rag, folders, quarantine, system, progress, features


logger = logging.getLogger(__name__)

# Global instances
db: Database = None
worker_pool: WorkerPool = None
folder_watcher: FolderWatcher = None
index_manager: IndexManager = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Safe target lifespan.

    Startup must not initialize the legacy SQLite/indexing runtime or mutate
    persistent data. PostgreSQL lifecycle belongs to the target platform
    foundation and is intentionally not wired into the legacy routes yet.
    """
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    config = get_config()
    
    app = FastAPI(
        title="cairnsearch",
        description="Local document search engine with AI-powered Q&A",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(search.router, prefix="/api", tags=["search"])
    app.include_router(status.router, prefix="/api", tags=["status"])
    app.include_router(documents.router, prefix="/api", tags=["documents"])
    app.include_router(index.router, prefix="/api", tags=["index"])
    app.include_router(rag.router, prefix="/api", tags=["rag"])
    app.include_router(folders.router, prefix="/api", tags=["folders"])
    app.include_router(quarantine.router, prefix="/api", tags=["quarantine"])
    app.include_router(system.router, prefix="/api", tags=["system"])
    app.include_router(progress.router, prefix="/api", tags=["progress"])
    app.include_router(features.router, prefix="/api", tags=["features"])
    
    # Serve static files for UI
    ui_path = Path(__file__).parent.parent.parent.parent / "ui"
    if ui_path.exists():
        app.mount("/", StaticFiles(directory=str(ui_path), html=True), name="ui")
    
    return app


def get_db() -> Database:
    """Get database instance."""
    return db


def get_worker_pool() -> WorkerPool:
    """Get worker pool instance."""
    return worker_pool


def get_index_manager() -> IndexManager:
    """Get index manager instance."""
    return index_manager


app = create_app()
