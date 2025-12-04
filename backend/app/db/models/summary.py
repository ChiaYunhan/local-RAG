from app.core.database import Base
from sqlalchemy import Column, String, Integer, Enum, Date, ForeignKey, Index
from app.db.schema.summary import SummaryStatus, SummaryType


class Summary(Base):
    __tablename__ = "Summaries"

    summary_id = Column(Integer, primary_key=True)
    summary_type = Column(Enum(SummaryType), nullable=False, index=True)
    filepath = Column(String)
    summary_status = Column(
        Enum(SummaryStatus),
        nullable=False,
        default=SummaryStatus.IN_PROGRESS,
        index=True,
    )
    document_id = Column(Integer, ForeignKey("Documents.document_id"), index=True)
    created_at = Column(Date, index=True)
    updated_at = Column(Date, index=True)

    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for finding summaries by document and type
        Index("ix_summaries_doc_type", "document_id", "summary_type"),
        # Index for filtering by status and sorting by date
        Index("ix_summaries_status_created", "summary_status", "created_at"),
    )
