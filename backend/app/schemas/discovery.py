"""
Discovery Profile schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class DiscoveryAnalysisRequest(BaseModel):
    force_refresh: bool = False
    model_config = ConfigDict(protected_namespaces=())

class PersonaInsight(BaseModel):
    persona: str
    confidence: float
    characteristics: List[str]
    strengths: List[str]
    opportunities: List[str]

class MaturityInsight(BaseModel):
    stage: str
    confidence: float
    indicators: List[str]
    next_stage_requirements: List[str]

class DiscoveryProfileResponse(BaseModel):
    id: int
    merchant_id: int
    persona: str
    maturity_stage: str
    persona_confidence: float
    maturity_confidence: float
    key_features: Optional[str] = None
    persona_characteristics: Optional[str] = None
    maturity_indicators: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_analyzed_at: datetime
    
    # Updated configuration to support ORM and silence warnings
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

class DiscoveryAnalysisResponse(BaseModel):
    profile: DiscoveryProfileResponse
    persona_insight: PersonaInsight
    maturity_insight: MaturityInsight
    recommendations: List[str]