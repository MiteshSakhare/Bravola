"""
Feedback Engine endpoints
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.feedback import FeedbackEvent
from app.schemas.feedback import FeedbackEventCreate, FeedbackEventResponse
from app.models.strategy import Strategy

router = APIRouter()

@router.post("/record-action")
async def record_human_feedback(
    strategy_id: str,
    action: str, # "approve", "reject", "modify"
    comments: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Captures Human Feedback (HITL - Human in the Loop)
    """
    # 1. Find the strategy
    result = await db.execute(
        select(Strategy).where(Strategy.strategy_id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    # Graceful handling if strategy not found (e.g. if deleted)
    if not strategy:
        # Log warning but don't crash
        print(f"Warning: Feedback received for unknown strategy {strategy_id}")
        return {"status": "ignored", "reason": "strategy_not_found"}

    # 2. Update Strategy Status
    if action == "approve":
        strategy.status = "approved"
        event_category = "positive"
    elif action == "reject":
        strategy.status = "rejected"
        event_category = "negative"
    else:
        strategy.status = "modified"
        event_category = "neutral"

    # 3. Create Feedback Event (This feeds the Drift Detection Engine)
    feedback_event = FeedbackEvent(
        event_id=f"FB_{uuid.uuid4().hex[:8]}",
        merchant_id=current_merchant.id,
        strategy_id=strategy.id,
        event_type="human_feedback",
        event_category=event_category,
        context_data=json.dumps({"action": action, "comments": comments}),
        created_at=datetime.utcnow()
    )
    
    db.add(feedback_event)
    await db.commit()

    return {"status": "recorded", "action": action}

@router.post("/events", response_model=FeedbackEventResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback_event(
    event_data: FeedbackEventCreate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Record a feedback event
    """
    # Calculate variance if both values provided
    variance = None
    if event_data.actual_value is not None and event_data.predicted_value is not None:
        variance = event_data.actual_value - event_data.predicted_value
    
    feedback_event = FeedbackEvent(
        event_id=f"FEED_{uuid.uuid4().hex[:8].upper()}",
        merchant_id=current_merchant.id,
        event_type=event_data.event_type,
        event_category=event_data.event_category,
        actual_value=event_data.actual_value,
        predicted_value=event_data.predicted_value,
        variance=variance,
        context_data=event_data.context_data,
        is_processed=False,
        model_updated=False
    )
    
    db.add(feedback_event)
    await db.commit()
    await db.refresh(feedback_event)
    
    return feedback_event