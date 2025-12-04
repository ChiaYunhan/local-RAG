from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector


class Embedding(Base):
    __tablename__ = "Embeddings"

    embedding_id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("Chunks.chunk_id"))
    sentence_text = Column(Text, nullable=False)
    sentence_index = Column(Integer, nullable=False)

    embedding_vector = Column(Vector(384))

    chunk = relationship("DocumentChunk", back_populates="embeddings")
