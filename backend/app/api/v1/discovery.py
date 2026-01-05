"""
Discovery Engine endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
import json
import traceback

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.discovery import DiscoveryProfile
from app.schemas.discovery import (
    DiscoveryProfileResponse,
    DiscoveryAnalysisRequest,
    DiscoveryAnalysisResponse,
    PersonaInsight,
    MaturityInsight
)
from app.discovery.engine import DiscoveryEngine

router = APIRouter()

@router.post("/analyze", response_model=DiscoveryAnalysisResponse)
async def analyze_merchant(
    request: DiscoveryAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Run discovery analysis on current merchant
    """
    try:
        # 1. Load Data
        stmt = (
            select(Merchant)
            .where(Merchant.id == current_merchant.id)
            .options(
                selectinload(Merchant.orders),
                selectinload(Merchant.customers),
                selectinload(Merchant.campaigns)
            )
        )
        result = await db.execute(stmt)
        loaded_merchant = result.scalar_one()

        # 2. Run AI Analysis
        engine = DiscoveryEngine()
        analysis_result = await engine.analyze_merchant(loaded_merchant, db)
        
        if not analysis_result:
            raise ValueError("Discovery Engine returned empty result")

        # ✅ FIX: Remove conflicting keys that cause "multiple values" error
        # We set 'last_analyzed_at' manually below, so remove it from the dict if present
        analysis_result.pop('last_analyzed_at', None)
        analysis_result.pop('merchant_id', None) 
        analysis_result.pop('id', None)

        # 3. Database Update
        result = await db.execute(
            select(DiscoveryProfile).where(
                DiscoveryProfile.merchant_id == current_merchant.id
            )
        )
        existing_profile = result.scalar_one_or_none()
        
        if existing_profile:
            # Update existing
            for key, value in analysis_result.items():
                if hasattr(existing_profile, key):
                    setattr(existing_profile, key, value)
            existing_profile.last_analyzed_at = datetime.utcnow()
            profile_response = existing_profile
        else:
            # Create new
            profile_response = DiscoveryProfile(
                merchant_id=current_merchant.id,
                **analysis_result,
                last_analyzed_at=datetime.utcnow()
            )
            db.add(profile_response)
            
        await db.commit()
        await db.refresh(profile_response)
        
        # 4. Format Response
        def safe_json(data):
            if not data: return {}
            if isinstance(data, dict): return data
            try: return json.loads(data)
            except: return {}

        persona_chars = safe_json(profile_response.persona_characteristics)
        maturity_inds = safe_json(profile_response.maturity_indicators)
        
        return DiscoveryAnalysisResponse(
            profile=profile_response,
            persona_insight=PersonaInsight(
                persona=profile_response.persona or "Unknown",
                confidence=profile_response.persona_confidence or 0.0,
                characteristics=persona_chars.get('characteristics', []),
                strengths=persona_chars.get('strengths', []),
                opportunities=persona_chars.get('opportunities', [])
            ),
            maturity_insight=MaturityInsight(
                stage=profile_response.maturity_stage or "Unknown",
                confidence=profile_response.maturity_confidence or 0.0,
                indicators=maturity_inds.get('indicators', []),
                next_stage_requirements=maturity_inds.get('next_stage', [])
            ),
            recommendations=[
                "Generate personalized growth strategies now"
            ]
        )

    except Exception as e:
        print(f"DISCOVERY ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/profile", response_model=DiscoveryProfileResponse)
async def get_discovery_profile(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    result = await db.execute(
        select(DiscoveryProfile).where(
            DiscoveryProfile.merchant_id == current_merchant.id
        )
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Discovery profile not found"
        )
    return profile