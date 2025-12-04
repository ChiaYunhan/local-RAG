from sqlalchemy import text
from app.core.database import Base, engine
from app.db.models.document import Document
from app.db.models.summary import Summary
from app.db.models.documentChunk import DocumentChunk
from app.db.models.embedding import Embedding


def init_database():
    """
    Initialize database: create extensions, tables, and indexes
    Called once at application startup
    """

    # Step 1: Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Step 2: Create all tables
    Base.metadata.create_all(bind=engine)

    # Step 3: Create vector indexes
    with engine.connect() as conn:
        index_exists = conn.execute(
            text(
                """
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'embeddings_vector_idx'
            """
            )
        ).fetchone()

        if not index_exists:
            conn.execute(
                text(
                    """
                    CREATE INDEX embeddings_vector_idx
                    ON "Embeddings"
                    USING hnsw (embedding_vector vector_cosine_ops)
                """
                )
            )
            conn.commit()
            print("✓ Vector index created")
        else:
            print("✓ Vector index exists")
