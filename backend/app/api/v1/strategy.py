"""
Strategy Engine endpoints with Orchestration & Deployment
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json
import uuid

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.strategy import Strategy, StrategyRule
from app.models.discovery import DiscoveryProfile 
from app.schemas.strategy import StrategyResponse, StrategyRuleCreate, StrategyRuleResponse
from app.strategy.engine import StrategyEngine
from app.integrations.klaviyo_client import KlaviyoClient

router = APIRouter()

# --- RULE MANAGEMENT (ADMIN) ---
@router.post("/rules", response_model=StrategyRuleResponse)
async def create_rule(
    rule_in: StrategyRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Create a new Orchestrator Rule (Logic injection)"""
    rule = StrategyRule(**rule_in.dict())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.get("/rules", response_model=List[StrategyRuleResponse])
async def get_rules(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    result = await db.execute(select(StrategyRule))
    return result.scalars().all()

# --- STRATEGY GENERATION & LISTING ---

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
    query = query.order_by(desc(Strategy.priority_score)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/generate", response_model=List[StrategyResponse])
async def generate_strategies(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    # (Keeping your existing logic, but simplified for brevity in this snippet)
    # Ensure Discovery Profile exists
    result = await db.execute(select(DiscoveryProfile).where(DiscoveryProfile.merchant_id == current_merchant.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Run Discovery Analysis first")

    engine = StrategyEngine()
    recommendations = await engine.generate_strategies(current_merchant, db, limit=limit)
    
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
            status='recommended'
        )
        db.add(strategy)
        saved_strategies.append(strategy)
        
    await db.commit()
    for s in saved_strategies: await db.refresh(s)
    return saved_strategies

# --- EXECUTION (THE DEPLOY BUTTON) ---

@router.post("/{strategy_id}/deploy")
async def deploy_strategy_to_klaviyo(
    strategy_id: str,
    list_id: str = Body(..., embed=True), # Frontend must send {"list_id": "X"}
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Push Strategy to Klaviyo as a Draft Campaign
    """
    # 1. Fetch Strategy
    result = await db.execute(
        select(Strategy).where(
            Strategy.strategy_id == strategy_id,
            Strategy.merchant_id == current_merchant.id
        )
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    if not current_merchant.klaviyo_api_key:
        raise HTTPException(status_code=400, detail="Klaviyo not connected. Please go to Settings.")

    # 2. Init Client
    klaviyo = KlaviyoClient(current_merchant.klaviyo_api_key)
    
    # 3. Generate Content (Simple Template)
    # In production, use Jinja2 to render nice HTML templates
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Special Offer: {strategy.strategy_name}</h2>
        <p>{strategy.description}</p>
        <p>Because you are a valued customer, we have a special offer for you.</p>
        <div style="margin: 20px 0;">
            <a href="https://{current_merchant.shop_domain}" style="background-color: #000; color: #fff; padding: 10px 20px; text-decoration: none;">Shop Now</a>
        </div>
        <p><small>Powered by Bravola AI</small></p>
    </div>
    """

    # 4. Push to Klaviyo
    campaign_id = await klaviyo.create_campaign(
        campaign_name=f"[Bravola] {strategy.strategy_name} - {uuid.uuid4().hex[:4]}",
        subject_line=f"Exclusive: {strategy.strategy_name}",
        list_id=list_id,
        html_content=html_content
    )

    # 5. Update Database
    if campaign_id:
        strategy.status = "active"
        strategy.sync_status = "synced"
        strategy.klaviyo_campaign_id = campaign_id
        strategy.implemented_at = uuid.uuid1().time # current time
        
        await db.commit()
        await db.refresh(strategy)
        
        return {
            "status": "success", 
            "message": "Campaign created in Klaviyo", 
            "klaviyo_id": campaign_id
        }
    else:
        strategy.sync_status = "failed"
        await db.commit()
        raise HTTPException(status_code=502, detail="Failed to create campaign in Klaviyo")