from app.db.models.summary import Summary
from app.db.repository.base import BaseRepository
from app.db.schema.summary import SummaryInCreate


class SummaryRepository(BaseRepository):
    def create_summary(self, summary_data: SummaryInCreate):
        new_summary = Summary(**summary_data.model_dump())

        self.session.add(new_summary)
        self.session.commit()
        self.session.refresh(new_summary)

        return new_summary
