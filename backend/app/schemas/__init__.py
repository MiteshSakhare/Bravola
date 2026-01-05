"""
Pydantic schemas for request/response validation
"""

from app.schemas.merchant import (
    MerchantCreate,
    MerchantUpdate,
    MerchantResponse,
    MerchantLogin,
    Token
)
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse
from app.schemas.discovery import DiscoveryProfileResponse, DiscoveryAnalysisRequest
from app.schemas.benchmark import BenchmarkScoreResponse, BenchmarkAnalysisRequest
from app.schemas.feedback import FeedbackEventCreate, FeedbackEventResponse

__all__ = [
    "MerchantCreate",
    "MerchantUpdate",
    "MerchantResponse",
    "MerchantLogin",
    "Token",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "StrategyCreate",
    "StrategyUpdate",
    "StrategyResponse",
    "DiscoveryProfileResponse",
    "DiscoveryAnalysisRequest",
    "BenchmarkScoreResponse",
    "BenchmarkAnalysisRequest",
    "FeedbackEventCreate",
    "FeedbackEventResponse",
]
