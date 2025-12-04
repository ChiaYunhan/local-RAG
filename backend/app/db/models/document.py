from app.core.database import Base
from sqlalchemy import Column, String, Date, Enum, Integer, Index
from sqlalchemy.orm import relationship
from app.db.schema.document import DocumentStatus
from app.db.models.documentChunk import DocumentChunk


class Document(Base):
    __tablename__ = "Documents"

    document_id = Column(Integer, primary_key=True)
    file_name = Column(String(100))
    summary_status = Column(
        Enum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.IN_PROGRESS,
        index=True,
    )
    filepath = Column(String(200))
    created_at = Column(Date, index=True)
    updated_at = Column(Date, index=True)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    # Composite index for common query patterns
    __table_args__ = (
        # Index for filtering by status and sorting by date
        Index("ix_documents_status_created", "summary_status", "created_at"),
    )
