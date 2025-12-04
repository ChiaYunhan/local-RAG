from app.db.models.embedding import Embedding
from app.db.repository.base import BaseRepository


class EmbeddingRepository(BaseRepository):
    def create_chunk(self, embedding_data):
        new_embedding = Embedding(**embedding_data.model_dump())

        self.session.add(new_embedding)
        self.session.commit()
        self.session.refresh(new_embedding)

        return new_embedding
