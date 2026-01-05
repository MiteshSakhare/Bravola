"""
Feedback Event schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackEventBase(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=100)
    event_category: str = Field(..., min_length=1, max_length=50)
    actual_value: Optional[float] = None
    predicted_value: Optional[float] = None
    context_data: Optional[str] = None


class FeedbackEventCreate(FeedbackEventBase):
    strategy_id: Optional[str] = None
    campaign_id: Optional[str] = None


class FeedbackEventResponse(FeedbackEventBase):
    id: int
    event_id: str
    merchant_id: int
    strategy_id: Optional[int] = None
    campaign_id: Optional[int] = None
    variance: Optional[float] = None
    is_processed: bool
    model_updated: bool
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
