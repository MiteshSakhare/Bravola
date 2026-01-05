from fastapi import APIRouter
from app.api.v1 import (
    auth, 
    merchants, 
    discovery, 
    benchmark, 
    strategy, 
    feedback, 
    campaigns,
    webhooks # ✅ Added Webhooks
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
api_router.include_router(benchmark.router, prefix="/benchmark", tags=["Benchmark"])
api_router.include_router(strategy.router, prefix="/strategy", tags=["Strategy"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
# ✅ Expose the Webhooks URL
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])