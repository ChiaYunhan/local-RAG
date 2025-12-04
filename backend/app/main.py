from fastapi import FastAPI, Depends, UploadFile, HTTPException
from contextlib import asynccontextmanager
from app.util.init_db import init_database
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.service.documentService import DocumentService
from app.db.schema.document import DocumentResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Startup and shutdown events
    Runs once when the application starts
    """
    # Startup: Initialize database
    print("🚀 Starting application...")
    init_database()
    print("✓ Database initialized")

    yield  # Application runs here

    # Shutdown: Cleanup (if needed)
    print("👋 Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/healthcheck")
def hello():
    return {"health": "healthy"}


@app.post("/document/upload", response_model=DocumentResponse, status_code=200)
async def upload_document(file: UploadFile, session: Session = Depends(get_db)):
    try:
        document = await DocumentService(session=session).create_document(file=file)
        return document
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error uploading document: {str(e)}"
        )


@app.get("/documents/list")
def get_documents(session: Session = Depends(get_db)):
    try:
        documents = DocumentService(session=session).get_all_documents()
        return documents
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error uploading document: {str(e)}"
        )
