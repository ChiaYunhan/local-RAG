from datetime import datetime
import enum
from pydantic import BaseModel, ConfigDict


class DocumentStatus(enum.Enum):
    ERROR = "error"
    COMPLETED = "completed"
    IN_PROGRESS = "in progress"


class DocumentInCreate(BaseModel):
    """Schema for creating a new document"""

    file_name: str
    summary_status: DocumentStatus
    filepath: str
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseModel):
    """Schema for returning document data"""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    document_id: int
    file_name: str
    summary_status: DocumentStatus
    filepath: str
    created_at: datetime
    updated_at: datetime


class DocumentStatusUpdate(BaseModel):
    """Schema for updating document status"""

    summary_status: DocumentStatus
