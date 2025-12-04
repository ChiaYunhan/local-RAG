from app.core.database import Base
from sqlalchemy import Index, Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship


class DocumentChunk(Base):
    __tablename__ = "Chunks"

    chunk_id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("Documents.document_id"))
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer)

    document = relationship("Document", back_populates="chunks")
    embeddings = relationship(
        "Embedding", back_populates="chunk", cascade="all, delete-orphan", lazy="noload"
    )
