import enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SummaryStatus(enum.Enum):
    ERROR = "error"
    COMPLETED = "completed"
    IN_PROGRESS = "in progress"


class SummaryType(enum.Enum):
    ABSTRACTIVE = "abstractive"
    EXTRACTIVE = "extractive"


class SummaryInCreate(BaseModel):
    """Schema for creating a new summary"""

    summary_type: SummaryType
    filepath: str
    summary_status: SummaryStatus
    document_id: int
    created_at: datetime
    updated_at: datetime


class SummaryResponse(BaseModel):
    """Schema for returning summary data"""

    model_config = ConfigDict(from_attributes=True)

    summary_id: int
    summary_type: SummaryType
    filepath: str
    summary_status: SummaryStatus
    document_id: int
    created_at: datetime
    updated_at: datetime
