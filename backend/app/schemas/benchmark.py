"""
Benchmark Score schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class BenchmarkAnalysisRequest(BaseModel):
    force_refresh: bool = False

class PeerComparison(BaseModel):
    metric_name: str
    your_value: float
    peer_p25: float
    peer_p50: float
    peer_p75: float
    your_percentile: float
    score: float
    status: str  # "below", "average", "above"

class BenchmarkScoreResponse(BaseModel):
    id: int
    merchant_id: int
    peer_group_id: int
    peer_group_name: Optional[str] = None
    overall_score: float
    aov_score: float
    ltv_score: float
    repeat_rate_score: float
    engagement_score: float
    aov_percentile: float
    ltv_percentile: float
    repeat_rate_percentile: float
    gap_analysis: Optional[str] = None
    improvement_areas: Optional[str] = None
    peer_benchmarks: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    analyzed_at: datetime
    
    # Updated configuration to silence warnings
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

class BenchmarkAnalysisResponse(BaseModel):
    benchmark: BenchmarkScoreResponse
    peer_comparisons: List[PeerComparison]
    strengths: List[str]
    improvement_opportunities: List[str]
    action_items: List[str]