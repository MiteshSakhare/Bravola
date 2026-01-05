"""
Feedback Engine endpoints (Fixed for 422 Error)
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
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

# ✅ FIX: Create a Pydantic model for the request body
class FeedbackActionRequest(BaseModel):
    strategy_id: str
    action: str  # "approve", "reject", "modify"
    comments: Optional[str] = None

@router.post("/record-action")
async def record_human_feedback(
    payload: FeedbackActionRequest, # ✅ FIX: Use the model here
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Captures Human Feedback (HITL - Human in the Loop)
    """
    # 1. Find the strategy using String ID (STRAT_...)
    result = await db.execute(
        select(Strategy).where(
            Strategy.strategy_id == payload.strategy_id,
            Strategy.merchant_id == current_merchant.id
        )
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        # If not found by string ID, try integer ID as fallback (legacy support)
        if payload.strategy_id.isdigit():
             result = await db.execute(
                select(Strategy).where(
                    Strategy.id == int(payload.strategy_id),
                    Strategy.merchant_id == current_merchant.id
                )
            )
             strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # 2. Update Strategy Status based on Action
    if payload.action == "approve":
        strategy.status = "active"
        strategy.confidence_score = min(1.0, strategy.confidence_score + 0.1)
    elif payload.action == "reject":
        strategy.status = "dismissed"
        strategy.confidence_score = max(0.0, strategy.confidence_score - 0.2)
    elif payload.action == "modify":
        strategy.status = "active" # Modified strategies are usually accepted
    
    # 3. Record Feedback Event for AI Learning
    event_category = "positive" if payload.action == "approve" else "negative"
    
    feedback_event = FeedbackEvent(
        event_id=f"FB_{uuid.uuid4().hex[:8].upper()}",
        merchant_id=current_merchant.id,
        strategy_id=strategy.id,
        event_type="human_feedback",
        event_category=event_category,
        context_data=json.dumps({"action": payload.action, "comments": payload.comments}),
        created_at=datetime.utcnow()
    )
    
    db.add(feedback_event)
    await db.commit()
    await db.refresh(strategy)

    return {"status": "recorded", "action": payload.action, "new_status": strategy.status}

@router.post("/events", response_model=FeedbackEventResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback_event(
    event_data: FeedbackEventCreate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Record a feedback event"""
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
        created_at=datetime.utcnow()
    )
    
    db.add(feedback_event)
    await db.commit()
    await db.refresh(feedback_event)
    
    return feedback_event