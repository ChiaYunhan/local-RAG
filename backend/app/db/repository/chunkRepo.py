from app.db.models.documentChunk import DocumentChunk
from app.db.repository.base import BaseRepository


class ChunkRepository(BaseRepository):
    def create_chunk(self, chunk_data):
        new_chunk = DocumentChunk(**chunk_data.model_dump())

        self.session.add(new_chunk)
        self.session.commit()
        self.session.refresh(new_chunk)

        return new_chunk
