"""
Benchmark Engine endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.benchmark import BenchmarkScore
from app.schemas.benchmark import (
    BenchmarkScoreResponse,
    BenchmarkAnalysisRequest,
    BenchmarkAnalysisResponse,
    PeerComparison
)
from app.benchmark.engine import BenchmarkEngine
import json

router = APIRouter()


@router.post("/analyze", response_model=BenchmarkAnalysisResponse)
async def analyze_benchmark(
    request: BenchmarkAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Run benchmark analysis on current merchant
    """
    # Initialize benchmark engine
    engine = BenchmarkEngine()
    
    # Check for existing recent analysis
    result = await db.execute(
        select(BenchmarkScore)
        .where(BenchmarkScore.merchant_id == current_merchant.id)
        .order_by(desc(BenchmarkScore.analyzed_at))
        .limit(1)
    )
    existing_score = result.scalar_one_or_none()
    
    if existing_score and not request.force_refresh:
        score_response = existing_score
    else:
        # Run new analysis
        analysis_result = await engine.analyze_merchant(current_merchant, db)
        
        if existing_score:
            # Update existing
            for key, value in analysis_result.items():
                setattr(existing_score, key, value)
            score_response = existing_score
        else:
            # Create new score
            score = BenchmarkScore(
                merchant_id=current_merchant.id,
                **analysis_result
            )
            db.add(score)
            score_response = score
        
        await db.commit()
        await db.refresh(score_response)
    
    # Build peer comparisons
    peer_benchmarks = json.loads(score_response.peer_benchmarks) if score_response.peer_benchmarks else {}
    
    comparisons = [
        PeerComparison(
            metric_name="Average Order Value",
            your_value=current_merchant.aov,
            peer_p25=peer_benchmarks.get('aov_p25', 0),
            peer_p50=peer_benchmarks.get('aov_p50', 0),
            peer_p75=peer_benchmarks.get('aov_p75', 0),
            your_percentile=score_response.aov_percentile,
            score=score_response.aov_score,
            status="above" if score_response.aov_score > 60 else "average" if score_response.aov_score > 40 else "below"
        ),
        PeerComparison(
            metric_name="Customer Lifetime Value",
            your_value=current_merchant.ltv,
            peer_p25=peer_benchmarks.get('ltv_p25', 0),
            peer_p50=peer_benchmarks.get('ltv_p50', 0),
            peer_p75=peer_benchmarks.get('ltv_p75', 0),
            your_percentile=score_response.ltv_percentile,
            score=score_response.ltv_score,
            status="above" if score_response.ltv_score > 60 else "average" if score_response.ltv_score > 40 else "below"
        ),
        PeerComparison(
            metric_name="Repeat Purchase Rate",
            your_value=current_merchant.repeat_purchase_rate,
            peer_p25=peer_benchmarks.get('rpr_p25', 0),
            peer_p50=peer_benchmarks.get('rpr_p50', 0),
            peer_p75=peer_benchmarks.get('rpr_p75', 0),
            your_percentile=score_response.repeat_rate_percentile,
            score=score_response.repeat_rate_score,
            status="above" if score_response.repeat_rate_score > 60 else "average" if score_response.repeat_rate_score > 40 else "below"
        )
    ]
    
    # Generate insights
    strengths = []
    improvements = []
    actions = []
    
    for comp in comparisons:
        if comp.status == "above":
            strengths.append(f"Your {comp.metric_name} is above peer average")
        elif comp.status == "below":
            improvements.append(f"Opportunity to improve {comp.metric_name}")
            actions.append(f"Focus on strategies to increase {comp.metric_name}")
    
    if not strengths:
        strengths.append("Room for improvement across all metrics")
    
    return BenchmarkAnalysisResponse(
        benchmark=score_response,
        peer_comparisons=comparisons,
        strengths=strengths,
        improvement_opportunities=improvements,
        action_items=actions
    )


@router.get("/scores", response_model=List[BenchmarkScoreResponse])
async def get_benchmark_scores(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant),
    limit: int = 10
):
    """
    Get benchmark score history
    """
    result = await db.execute(
        select(BenchmarkScore)
        .where(BenchmarkScore.merchant_id == current_merchant.id)
        .order_by(desc(BenchmarkScore.analyzed_at))
        .limit(limit)
    )
    scores = result.scalars().all()
    
    return scores
