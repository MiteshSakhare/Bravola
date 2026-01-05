"""
Feature store with Redis Caching for ML features
"""

from typing import Dict, Any, List
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import logger
from app.models.merchant import Merchant

# Initialize Async Redis Client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class FeatureStore:
    """
    Centralized feature storage with Read-Through Caching
    """
    
    @staticmethod
    async def get_merchant_features(
        merchant_id: int,
        db: AsyncSession,
        feature_set: str = "all"
    ) -> Dict[str, Any]:
        """
        Get features with Caching Strategy (Cache -> DB -> Cache)
        """
        cache_key = f"features:{merchant_id}:{feature_set}"
        
        # 1. 🚀 FAST PATH: Try Cache First
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                # logger.debug(f"✅ Cache Hit for merchant {merchant_id}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Redis error (skipping cache): {e}")

        # 2. 🐢 SLOW PATH: Fetch from DB (Cache Miss)
        try:
            result = await db.execute(
                select(Merchant).where(Merchant.id == merchant_id)
            )
            merchant = result.scalar_one_or_none()
            
            if not merchant:
                return {}
            
            # Construct Feature Vector
            features = {
                'merchant_id': merchant.merchant_id,
                'monthly_revenue': float(merchant.monthly_revenue or 0),
                'total_customers': int(merchant.total_customers or 0),
                'total_orders': int(merchant.total_orders or 0),
                'aov': float(merchant.aov or 0),
                'repeat_purchase_rate': float(merchant.repeat_purchase_rate or 0),
                'ltv': float(merchant.ltv or 0),
                'email_subscriber_count': int(merchant.email_subscriber_count or 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # 3. 💾 SAVE: Store in Cache for 1 Hour (3600 seconds)
            try:
                await redis_client.setex(cache_key, 3600, json.dumps(features))
            except Exception as e:
                logger.warning(f"Failed to write to Redis: {e}")
            
            return features
        
        except Exception as e:
            logger.error(f"Error retrieving features from DB: {str(e)}")
            return {}
    
    @staticmethod
    async def invalidate_cache(merchant_id: int):
        """
        Call this when new data arrives (e.g., via Webhook) to force a refresh.
        """
        try:
            pattern = f"features:{merchant_id}:*"
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
                logger.info(f"🗑️ Invalidated cache for merchant {merchant_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")

    @staticmethod
    async def store_computed_features(
        merchant_id: int,
        features: Dict[str, Any],
        db: AsyncSession
    ) -> bool:
        """Store computed features (Logging for now)"""
        try:
            logger.info(f"Computing features for merchant {merchant_id}: {len(features)} items")
            return True
        except Exception as e:
            logger.error(f"Error storing features: {str(e)}")
            return False

    @staticmethod
    def validate_features(features: Dict[str, Any], required_features: List[str]) -> bool:
        """Validate presence of required features"""
        missing = [f for f in required_features if f not in features]
        if missing:
            logger.warning(f"Missing required features: {missing}")
            return False
        return True