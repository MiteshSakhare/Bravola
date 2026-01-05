"""
Strategy Engine endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import traceback
import json
import uuid

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.strategy import Strategy
from app.models.discovery import DiscoveryProfile 
from app.schemas.strategy import StrategyResponse
from app.strategy.engine import StrategyEngine

router = APIRouter()

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
    try:
        # Check if discovery profile exists
        result = await db.execute(
            select(DiscoveryProfile).where(DiscoveryProfile.merchant_id == current_merchant.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, 
                detail="Please run 'Discovery Analysis' before generating strategies."
            )

        # Initialize Engine
        engine = StrategyEngine()
        
        # Generate strategies
        recommendations = await engine.generate_strategies(current_merchant, db, limit=limit)
        
        # Save to Database with CORRECT column mapping
        saved_strategies = []
        for rec in recommendations:
            strategy = Strategy(
                merchant_id=current_merchant.id,
                strategy_id=f"STRAT_{uuid.uuid4().hex[:8].upper()}",
                
                # ✅ MAPPED: 'strategy_name' (Model) matches 'strategy_name' (Engine)
                strategy_name=rec.get('strategy_name', 'Unnamed Strategy'),
                
                # ✅ MAPPED: 'strategy_type' (Model)
                strategy_type=rec.get('strategy_type', 'Growth'),
                
                description=rec.get('description', ''),
                
                priority_score=rec.get('priority_score', 0.0),
                
                # ✅ FIXED: 'expected_roi' (Model) instead of 'roi_estimate'
                expected_roi=rec.get('expected_roi', 0.0),
                
                # ✅ ADDED: 'estimated_revenue' (Model)
                estimated_revenue=rec.get('estimated_revenue', 0.0),
                
                # ✅ ADDED: 'confidence_score' (Model)
                confidence_score=rec.get('confidence_score', 0.0),
                
                # ✅ FIXED: 'action_steps' (Model) instead of 'action_plan'
                action_steps=json.dumps(rec.get('action_steps', [])),
                
                # ✅ FIXED: 'estimated_effort' (Model) instead of 'difficulty'
                estimated_effort=rec.get('estimated_effort', 'medium'),
                
                # ✅ FIXED: 'timeline' (Model) instead of 'time_to_implement'
                timeline=rec.get('timeline', '2 weeks'),
                
                # ✅ ADDED: 'is_eligible' (Model)
                is_eligible=rec.get('is_eligible', True),
                
                status='recommended'
            )
            db.add(strategy)
            saved_strategies.append(strategy)
            
        await db.commit()
        
        # Refresh to return valid IDs
        for s in saved_strategies:
            await db.refresh(s)
            
        return saved_strategies
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"STRATEGY GENERATION ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")

@router.post("/{strategy_id}/implement", response_model=StrategyResponse)
async def implement_strategy(
    strategy_id: int, 
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.merchant_id == current_merchant.id
        )
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    strategy.status = "active"
    await db.commit()
    await db.refresh(strategy)
    return strategy

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    result = await db.execute(
        select(Strategy).where(
            Strategy.strategy_id == strategy_id,
            Strategy.merchant_id == current_merchant.id
        )
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.post("/{strategy_id}/deploy")
async def deploy_strategy_to_klaviyo(
    strategy_id: str,
    list_id: str,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    return {"status": "deployed", "platform": "klaviyo"}