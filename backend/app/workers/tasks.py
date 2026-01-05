import asyncio
from asgiref.sync import async_to_sync
from .celery_app import celery_app
from app.core.logging import logger
from app.integrations.shopify_client import ShopifyClient

# ✅ FIX: Import from the new application package
from app.ml.trainer import BravolaMLTrainer 
from app.ml.monitoring.drift import check_model_drift
from app.ml.feature_store import FeatureStore

@celery_app.task(name="tasks.sync_merchant_data", bind=True, max_retries=3)
def sync_merchant_data(self, merchant_id: int, shop_domain: str, token: str):
    """
    Background Task: Ingests Shopify data without blocking the user dashboard.
    """
    logger.info(f"🔄 [Async] Syncing {shop_domain} (ID: {merchant_id})...")
    
    async def _sync():
        client = ShopifyClient(shop_domain, token)
        
        # 1. Fetch Orders
        orders = await client.get_orders(limit=200)
        
        # 2. Invalidate Cache so the Dashboard updates immediately
        await FeatureStore.invalidate_cache(merchant_id)
        
        logger.info(f"Synced {len(orders)} orders for {shop_domain}")
        return len(orders)

    try:
        # Run async code inside the synchronous Celery worker
        count = async_to_sync(_sync)()
        return f"Synced {count} orders for {merchant_id}"
    except Exception as exc:
        logger.error(f"Sync failed for {merchant_id}: {exc}")
        # Exponential Backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task(name="tasks.auto_retrain_pipeline")
def auto_retrain_pipeline():
    """
    The Self-Healing Loop:
    1. Checks for Model Drift.
    2. If Drift > 15%, triggers auto-retraining.
    """
    logger.info("🕵️ [Auto-ML] Checking model health...")
    
    # Run async drift check synchronously
    drift_detected = async_to_sync(check_model_drift)(threshold=0.15)
    
    if drift_detected:
        logger.warning("⚠️ Drift Detected! Triggering Auto-Retraining...")
        try:
            trainer = BravolaMLTrainer()
            trainer.run()
            logger.info("✅ Auto-Retraining Complete.")
        except Exception as e:
            logger.error(f"❌ Retraining Failed: {e}")
    else:
        logger.info("✅ Model health is good. No retraining needed.")