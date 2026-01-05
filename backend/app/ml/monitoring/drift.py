import joblib
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.database import async_session_factory
from app.models.feedback import FeedbackEvent

async def check_model_drift(threshold: float = 0.15) -> bool:
    """
    Compares Training Baseline vs. Real-World Variance.
    Triggers TRUE if the model performance degrades.
    """
    try:
        metadata_path = settings.ML_ARTIFACTS_PATH / 'training_metadata.joblib'
        if not metadata_path.exists():
            return False

        metadata = joblib.load(metadata_path)
        
        # 1. Get Baseline Metrics from last training run
        # If we don't have a baseline, assume 85% accuracy
        baseline_acc = metadata.get('metrics', {}).get('accuracy', 0.85)
        
        # 2. Get Real-World Performance from DB
        async with async_session_factory() as db:
            # We look at the average 'variance' recorded in FeedbackEvents
            # variance = (Actual - Predicted)
            # Low variance means high accuracy.
            result = await db.execute(
                select(func.avg(FeedbackEvent.variance))
                .where(FeedbackEvent.variance.isnot(None))
                # Only look at recent events to detect *current* drift
                .order_by(FeedbackEvent.created_at.desc())
                .limit(100)
            )
            avg_variance = result.scalar()
            
            if avg_variance is None:
                # Not enough data yet to determine drift
                return False
                
            # Convert variance to an accuracy proxy (simple approximation)
            # If avg variance is 0.1 (10% off), accuracy is ~0.9
            current_acc = 1.0 - abs(float(avg_variance))
        
        # 3. Calculate Drift Percentage
        drift = (baseline_acc - current_acc) / baseline_acc
        
        logger.info(f"📉 Drift Check: Baseline={baseline_acc:.2f}, Current={current_acc:.2f}, Drift={drift:.2%}")
        
        if drift > threshold:
            logger.warning(f"⚠️ Model Drift Detected! ({drift:.2%} degradation)")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Drift check failed: {e}")
        return False