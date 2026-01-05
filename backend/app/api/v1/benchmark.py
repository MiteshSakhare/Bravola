"""
Benchmark Engine endpoints (Fixed)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import traceback
import json

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
    try:
        # ✅ FIX 1: Eager Load relationships to prevent Greenlet errors
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

        # Initialize benchmark engine
        engine = BenchmarkEngine()
        
        # Check for existing recent analysis to avoid re-calculation if not forced
        if not request.force_refresh:
            result = await db.execute(
                select(BenchmarkScore)
                .where(BenchmarkScore.merchant_id == current_merchant.id)
                .order_by(desc(BenchmarkScore.analyzed_at))
                .limit(1)
            )
            existing_score = result.scalar_one_or_none()
            if existing_score:
                # If we have a recent score, we can reuse it, but we still
                # need to build the response object. For simplicity/safety,
                # we'll re-run analysis or reconstruct the response here.
                # Let's just re-run to ensure fresh comparisons.
                pass 

        # ✅ FIX 2: Run Analysis with the fully loaded merchant object
        analysis_result = await engine.analyze_merchant(loaded_merchant, db)
        
        # Save to DB
        score = BenchmarkScore(
            merchant_id=current_merchant.id,
            peer_group_id=analysis_result['peer_group_id'],
            peer_group_name=analysis_result['peer_group_name'],
            overall_score=analysis_result['overall_score'],
            aov_score=analysis_result['aov_score'],
            ltv_score=analysis_result['ltv_score'],
            repeat_rate_score=analysis_result['repeat_rate_score'],
            engagement_score=analysis_result['engagement_score'],
            aov_percentile=analysis_result['aov_percentile'],
            ltv_percentile=analysis_result['ltv_percentile'],
            repeat_rate_percentile=analysis_result['repeat_rate_percentile'],
            gap_analysis=analysis_result['gap_analysis'],
            improvement_areas=analysis_result['improvement_areas'],
            peer_benchmarks=analysis_result['peer_benchmarks'],
            model_version=analysis_result['model_version'],
            analyzed_at=analysis_result['analyzed_at']
        )
        
        db.add(score)
        await db.commit()
        await db.refresh(score)
        
        # Build peer comparisons for response
        peer_benchmarks = json.loads(score.peer_benchmarks or "{}")
        
        # Comparison logic helpers
        def get_stat(score_val):
            if score_val > 60: return "above"
            if score_val < 40: return "below"
            return "average"

        comparisons = [
            PeerComparison(
                metric_name="Average Order Value",
                your_value=float(loaded_merchant.aov or 0.0),
                peer_p25=peer_benchmarks.get('aov_p25', 0),
                peer_p50=peer_benchmarks.get('aov_p50', 0),
                peer_p75=peer_benchmarks.get('aov_p75', 0),
                your_percentile=score.aov_percentile,
                score=score.aov_score,
                status=get_stat(score.aov_score)
            ),
            PeerComparison(
                metric_name="Customer Lifetime Value",
                your_value=float(loaded_merchant.ltv or 0.0),
                peer_p25=peer_benchmarks.get('ltv_p25', 0),
                peer_p50=peer_benchmarks.get('ltv_p50', 0),
                peer_p75=peer_benchmarks.get('ltv_p75', 0),
                your_percentile=score.ltv_percentile,
                score=score.ltv_score,
                status=get_stat(score.ltv_score)
            ),
            PeerComparison(
                metric_name="Repeat Purchase Rate",
                your_value=float(loaded_merchant.repeat_purchase_rate or 0.0),
                peer_p25=peer_benchmarks.get('rpr_p25', 0),
                peer_p50=peer_benchmarks.get('rpr_p50', 0),
                peer_p75=peer_benchmarks.get('rpr_p75', 0),
                your_percentile=score.repeat_rate_percentile,
                score=score.repeat_rate_score,
                status=get_stat(score.repeat_rate_score)
            )
        ]
        
        # Generate insights strings
        strengths = [f"Your {c.metric_name} is strong" for c in comparisons if c.status == "above"]
        improvements = [f"Opportunity to improve {c.metric_name}" for c in comparisons if c.status == "below"]
        
        if not strengths: strengths.append("Room for improvement across metrics")
        if not improvements: improvements.append("Maintaining excellent performance")

        actions = []
        if improvements:
            actions.append(f"Focus on boosting {comparisons[0].metric_name}")
        else:
            actions.append("Maintain current strategies")

        return BenchmarkAnalysisResponse(
            benchmark=score,
            peer_comparisons=comparisons,
            strengths=strengths,
            improvement_opportunities=improvements,
            action_items=actions
        )

    except Exception as e:
        print(f"BENCHMARK ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Benchmark analysis failed: {str(e)}")


@router.get("/scores", response_model=List[BenchmarkScoreResponse])
async def get_benchmark_scores(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant),
    limit: int = 10
):
    result = await db.execute(
        select(BenchmarkScore)
        .where(BenchmarkScore.merchant_id == current_merchant.id)
        .order_by(desc(BenchmarkScore.analyzed_at))
        .limit(limit)
    )
    scores = result.scalars().all()
    return scores