"""
Strategy and Rules schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- Rule Schemas ---
class StrategyRuleBase(BaseModel):
    rule_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    condition_metric: str
    operator: str
    threshold_value: str
    action_type: str
    target_strategy_type: str
    impact_factor: float = 1.0
    is_active: bool = True

class StrategyRuleCreate(StrategyRuleBase):
    pass

class StrategyRuleResponse(StrategyRuleBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Strategy Schemas ---
class StrategyBase(BaseModel):
    strategy_name: str = Field(..., min_length=1, max_length=255)
    strategy_type: str = Field(..., min_length=1, max_length=100)
    description: str
    expected_roi: float = Field(default=0.0, ge=0)
    estimated_revenue: float = Field(default=0.0, ge=0)

class StrategyCreate(StrategyBase):
    priority_score: float = Field(default=0.0, ge=0, le=100)
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    action_steps: Optional[str] = None
    required_resources: Optional[str] = None
    estimated_effort: Optional[str] = "medium"
    timeline: Optional[str] = None
    is_eligible: bool = True

class StrategyUpdate(BaseModel):
    status: Optional[str] = None
    sync_status: Optional[str] = None # New field
    klaviyo_campaign_id: Optional[str] = None # New field
    actual_roi: Optional[float] = None
    actual_revenue: Optional[float] = None
    implemented_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class StrategyResponse(StrategyBase):
    id: int
    strategy_id: str
    merchant_id: int
    priority_score: float
    confidence_score: float
    action_steps: Optional[str] = None
    required_resources: Optional[str] = None
    estimated_effort: str
    timeline: Optional[str] = None
    status: str
    is_eligible: bool
    
    # Execution Tracking
    implemented_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_roi: Optional[float] = None
    actual_revenue: Optional[float] = None
    
    # Sync Status
    sync_status: Optional[str] = "pending"
    klaviyo_campaign_id: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class StrategyRecommendation(BaseModel):
    strategy_name: str
    strategy_type: str
    description: str
    priority_score: float
    expected_roi: float
    estimated_revenue: float
    confidence_score: float
    action_steps: List[str]
    estimated_effort: str
    timeline: str
    is_eligible: bool
    reasons: List[str]