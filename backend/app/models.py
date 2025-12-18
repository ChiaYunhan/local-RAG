from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4
import enum


class SummaryType(enum.Enum):
    ABSTRACTIVE = "abstractive"
    EXTRACTIVE = "extractive"


class Topic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str
    summary: Optional[str]
    summary_type: SummaryType


class ProcessingResult(BaseModel):
    source_file: str
    topics: List[Topic]
    final_summary: str
    model_used: str
    processing_time_seconds: float
    total_tokens: int
    output_path: str
