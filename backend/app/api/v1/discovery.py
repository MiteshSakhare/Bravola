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
        # ✅ FINAL FIX: Eagerly load all relationships upfront.
        # This prevents the 'greenlet_spawn' error by fetching data 
        # BEFORE the synchronous engine tries to access it.
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
        # Overwrite current_merchant with the fully loaded version
        loaded_merchant = result.scalar_one()

        # Initialize discovery engine
        engine = DiscoveryEngine()
        
        # 1. Run analysis using the LOADED merchant
        analysis_result = await engine.analyze_merchant(loaded_merchant, db)
        
        if not analysis_result:
            raise ValueError("Discovery Engine returned empty result")

        # Cleanup fields to prevent database errors
        for forbidden in ['id', 'merchant_id', 'created_at', 'updated_at']:
            if forbidden in analysis_result:
                del analysis_result[forbidden]

        # 2. Database Operation - Robust Upsert Logic
        try:
            # Check for existing profile
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
                await db.commit()
            else:
                # Insert new
                profile = DiscoveryProfile(
                    merchant_id=current_merchant.id,
                    **analysis_result,
                    last_analyzed_at=datetime.utcnow()
                )
                db.add(profile)
                await db.commit()
                profile_response = profile

        except Exception:
            # Race condition handler: If insert fails, try update again
            await db.rollback()
            result = await db.execute(
                select(DiscoveryProfile).where(
                    DiscoveryProfile.merchant_id == current_merchant.id
                )
            )
            profile_response = result.scalar_one()
            
            for key, value in analysis_result.items():
                if hasattr(profile_response, key):
                    setattr(profile_response, key, value)
            profile_response.last_analyzed_at = datetime.utcnow()
            await db.commit()
        
        await db.refresh(profile_response)
        
        # 3. Build Response
        def safe_json(data):
            if not data: return {}
            if isinstance(data, dict): return data
            try: return json.loads(data)
            except: return {}

        persona_chars = safe_json(profile_response.persona_characteristics)
        maturity_inds = safe_json(profile_response.maturity_indicators)
        
        persona_insight = PersonaInsight(
            persona=profile_response.persona or "Unknown",
            confidence=profile_response.persona_confidence or 0.0,
            characteristics=persona_chars.get('characteristics', []),
            strengths=persona_chars.get('strengths', []),
            opportunities=persona_chars.get('opportunities', [])
        )
        
        maturity_insight = MaturityInsight(
            stage=profile_response.maturity_stage or "Unknown",
            confidence=profile_response.maturity_confidence or 0.0,
            indicators=maturity_inds.get('indicators', []),
            next_stage_requirements=maturity_inds.get('next_stage', [])
        )
        
        recommendations = [
            f"Your business is classified as '{profile_response.persona}' persona",
            f"You're in the '{profile_response.maturity_stage}' stage",
            "Generate personalized growth strategies now"
        ]
        
        return DiscoveryAnalysisResponse(
            profile=profile_response,
            persona_insight=persona_insight,
            maturity_insight=maturity_insight,
            recommendations=recommendations
        )

    except Exception as e:
        # Log the full error for debugging but return a clean 500
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
            detail="Discovery profile not found. Run analysis first."
        )
    
    return profile