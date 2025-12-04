from typing import Optional, List
from .base import BaseRepository
from app.db.models.document import Document
from app.db.schema.document import DocumentInCreate, DocumentStatus


class DocumentRepository(BaseRepository):
    def create_document(self, document_data: DocumentInCreate) -> Document:
        """Create a new document record"""
        # Convert Pydantic model to dict for SQLAlchemy
        new_document = Document(**document_data.model_dump())

        self.session.add(new_document)
        self.session.commit()
        self.session.refresh(new_document)

        # Expunge from session to prevent lazy loading issues
        self.session.expunge(new_document)

        return new_document

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.session.query(Document).filter(Document.document_id == document_id).first()

    def get_all_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents with pagination"""
        return self.session.query(Document).offset(skip).limit(limit).all()

    def get_documents_by_status(self, status: DocumentStatus, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get documents filtered by status"""
        return (
            self.session.query(Document)
            .filter(Document.summary_status == status)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_document_status(self, document_id: int, status: DocumentStatus) -> Optional[Document]:
        """Update document status"""
        document = self.get_document_by_id(document_id)
        if document:
            document.summary_status = status  # type: ignore
            self.session.commit()
            self.session.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        document = self.get_document_by_id(document_id)
        if document:
            self.session.delete(document)
            self.session.commit()
            return True
        return False
