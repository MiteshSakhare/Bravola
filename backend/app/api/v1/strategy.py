"""
Strategy Engine endpoints (Fixed: Auto-Create Campaign on Implementation)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.strategy import Strategy, StrategyRule
from app.models.discovery import DiscoveryProfile 
from app.models.campaign import Campaign  # ✅ NEW IMPORT
from app.schemas.strategy import StrategyResponse, StrategyRuleCreate, StrategyRuleResponse
from app.strategy.engine import StrategyEngine
from app.integrations.klaviyo_client import KlaviyoClient

router = APIRouter()

# --- RULE MANAGEMENT ---
@router.post("/rules", response_model=StrategyRuleResponse)
async def create_rule(
    rule_in: StrategyRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    rule = StrategyRule(**rule_in.dict())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.get("/rules", response_model=List[StrategyRuleResponse])
async def get_rules(db: AsyncSession = Depends(get_db), current_merchant: Merchant = Depends(get_current_merchant)):
    result = await db.execute(select(StrategyRule))
    return result.scalars().all()

# --- STRATEGY LISTING & GENERATION ---

@router.get("/list", response_model=List[StrategyResponse])
async def list_strategies(
    status_filter: Optional[str] = Query(None),
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    query = select(Strategy).where(Strategy.merchant_id == current_merchant.id)
    if status_filter:
        query = query.where(Strategy.status == status_filter)
    query = query.order_by(desc(Strategy.created_at), desc(Strategy.priority_score)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/generate", response_model=List[StrategyResponse])
async def generate_strategies(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    # Ensure Discovery Profile exists
    result = await db.execute(select(DiscoveryProfile).where(DiscoveryProfile.merchant_id == current_merchant.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Please run 'Discovery Analysis' first.")

    # Get EXISTING strategies to prevent duplicates
    existing_res = await db.execute(
        select(Strategy.strategy_name)
        .where(Strategy.merchant_id == current_merchant.id)
    )
    existing_names = [row[0] for row in existing_res.all()]

    engine = StrategyEngine()
    recommendations = await engine.generate_strategies(
        current_merchant, 
        db, 
        limit=limit, 
        exclude_names=existing_names
    )
    
    if not recommendations:
        return []

    saved_strategies = []
    for rec in recommendations:
        strategy = Strategy(
            merchant_id=current_merchant.id,
            strategy_id=f"STRAT_{uuid.uuid4().hex[:8].upper()}",
            strategy_name=rec['strategy_name'],
            strategy_type=rec['strategy_type'],
            description=rec['description'],
            priority_score=rec['priority_score'],
            expected_roi=rec['expected_roi'],
            estimated_revenue=rec['estimated_revenue'],
            confidence_score=rec['confidence_score'],
            action_steps=json.dumps(rec['action_steps']),
            estimated_effort=rec['estimated_effort'],
            timeline=rec['timeline'],
            is_eligible=rec['is_eligible'],
            status='recommended',
            created_at=datetime.utcnow()
        )
        db.add(strategy)
        saved_strategies.append(strategy)
        
    await db.commit()
    for s in saved_strategies: await db.refresh(s)
    return saved_strategies

# --- IMPLEMENTATION LOGIC ---

@router.post("/{strategy_id}/implement", response_model=StrategyResponse)
async def implement_strategy(
    strategy_id: str, 
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    1. Mark Strategy as Active
    2. Create corresponding Campaign record so it appears in Campaigns Page
    """
    # 1. Fetch Strategy (Supports Int ID or String ID)
    if strategy_id.isdigit():
        query = select(Strategy).where(
            Strategy.id == int(strategy_id),
            Strategy.merchant_id == current_merchant.id
        )
    else:
        query = select(Strategy).where(
            Strategy.strategy_id == strategy_id,
            Strategy.merchant_id == current_merchant.id
        )
        
    result = await db.execute(query)
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    # 2. Update Strategy Status
    strategy.status = "active"
    strategy.implemented_at = datetime.utcnow()
    
    # 3. ✅ CREATE CAMPAIGN RECORD
    # This bridges the gap between Strategy and Campaign dashboards
    campaign = Campaign(
        campaign_id=f"CAMP_{uuid.uuid4().hex[:8].upper()}",
        merchant_id=current_merchant.id,
        campaign_name=f"[Strategy] {strategy.strategy_name}",
        campaign_type=strategy.strategy_type,
        status="active",
        sent_date=datetime.utcnow(),
        # Initialize placeholder metrics
        recipients=current_merchant.email_subscriber_count or 0,
        opens=0,
        clicks=0,
        conversions=0,
        revenue=0.0,
        roi=0.0,
        created_at=datetime.utcnow()
    )
    
    db.add(campaign)
    
    await db.commit()
    await db.refresh(strategy)
    return strategy

@router.post("/{strategy_id}/deploy")
async def deploy_strategy_to_klaviyo(
    strategy_id: str,
    list_id: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    # Fetch Strategy
    if strategy_id.isdigit():
        query = select(Strategy).where(Strategy.id == int(strategy_id), Strategy.merchant_id == current_merchant.id)
    else:
        query = select(Strategy).where(Strategy.strategy_id == strategy_id, Strategy.merchant_id == current_merchant.id)

    result = await db.execute(query)
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    if not current_merchant.klaviyo_api_key:
        raise HTTPException(status_code=400, detail="Klaviyo not connected.")

    klaviyo = KlaviyoClient(current_merchant.klaviyo_api_key)
    
    html_content = f"""
    <div style="font-family: Arial; padding: 20px;">
        <h2>{strategy.strategy_name}</h2>
        <p>{strategy.description}</p>
        <a href="https://{current_merchant.shop_domain}">Shop Now</a>
    </div>
    """

    campaign_id = await klaviyo.create_campaign(
        campaign_name=f"[Bravola] {strategy.strategy_name}",
        subject_line=f"Special: {strategy.strategy_name}",
        list_id=list_id,
        html_content=html_content
    )

    if campaign_id:
        strategy.status = "active"
        strategy.sync_status = "synced"
        strategy.klaviyo_campaign_id = campaign_id
        strategy.implemented_at = datetime.utcnow()
        
        # ✅ Also create local campaign record for synced items
        local_campaign = Campaign(
            campaign_id=f"CAMP_{campaign_id[:8].upper()}", # Use Klaviyo ID prefix if possible
            merchant_id=current_merchant.id,
            campaign_name=f"[Klaviyo] {strategy.strategy_name}",
            campaign_type=strategy.strategy_type,
            status="active",
            sent_date=datetime.utcnow(),
            recipients=current_merchant.email_subscriber_count or 0,
            opens=0, clicks=0, conversions=0, revenue=0.0, roi=0.0,
            created_at=datetime.utcnow()
        )
        db.add(local_campaign)
        
        await db.commit()
        await db.refresh(strategy)
        return {"status": "success", "klaviyo_id": campaign_id}
    else:
        strategy.sync_status = "failed"
        await db.commit()
        raise HTTPException(status_code=502, detail="Failed to create campaign in Klaviyo")