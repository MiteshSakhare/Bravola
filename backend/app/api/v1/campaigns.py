"""
Campaign endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, field_validator

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.campaign import Campaign

router = APIRouter()

class CampaignSchema(BaseModel):
    id: int
    campaign_id: str
    # ✅ FIX: Renamed 'name' to 'campaign_name' to match DB model
    campaign_name: str
    status: str
    sent_date: Optional[datetime] = None
    open_rate: float = 0.0
    click_rate: float = 0.0
    revenue: float = 0.0
    
    @field_validator('open_rate', 'click_rate', 'revenue', mode='before')
    @classmethod
    def set_numeric_defaults(cls, v):
        return v or 0.0
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[CampaignSchema]) 
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Get all campaigns for the current merchant
    """
    result = await db.execute(
        select(Campaign)
        .where(Campaign.merchant_id == current_merchant.id)
        .order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    
    # Return Pydantic models
    return [CampaignSchema.model_validate(c) for c in campaigns]

@router.get("/{campaign_id}", response_model=Optional[CampaignSchema])
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    result = await db.execute(
        select(Campaign).where(
            Campaign.campaign_id == campaign_id,
            Campaign.merchant_id == current_merchant.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if campaign:
        return CampaignSchema.model_validate(campaign)
    return None