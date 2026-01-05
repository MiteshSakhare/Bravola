"""
Benchmark Engine - Peer Comparison and Scoring
"""

import joblib
import json
import numpy as np
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.core.logging import logger
from app.models.merchant import Merchant
from app.models.order import Order
from app.models.customer import Customer
from app.models.campaign import Campaign


class BenchmarkEngine:
    """
    Benchmark Engine for peer comparison and performance scoring
    """
    
    def __init__(self):
        self.artifacts_dir = settings.ML_ARTIFACTS_PATH / 'benchmark'
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load trained models and benchmarks"""
        try:
            # Load clustering model
            self.clustering_model = joblib.load(
                self.artifacts_dir / 'models' / 'peer_clustering.joblib'
            )
            
            # Load preprocessors
            self.scaler = joblib.load(
                self.artifacts_dir / 'preprocessors' / 'cluster_scaler.joblib'
            )
            self.cluster_features = joblib.load(
                self.artifacts_dir / 'preprocessors' / 'cluster_features.joblib'
            )
            
            # Load percentile benchmarks
            self.benchmarks = joblib.load(
                self.artifacts_dir / 'models' / 'percentile_benchmarks.joblib'
            )
            
            self.models_loaded = True
            logger.info("Benchmark Engine models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Benchmark Engine models: {str(e)}")
            # Set flag to false, will raise runtime error if used
            self.models_loaded = False
    
    async def analyze_merchant(
        self,
        merchant: Merchant,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Analyze merchant and generate benchmark scores
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded - Run training first")
        
        logger.info(f"Running Benchmark analysis for merchant {merchant.merchant_id}")
        
        # 1. Extract features
        features = await self._extract_features(merchant, db)
        
        # 2. Prepare feature vector for ML
        # Create DataFrame
        df = pd.DataFrame([features])
        
        # Ensure all expected columns exist (fill missing with 0)
        for col in self.cluster_features:
            if col not in df.columns:
                df[col] = 0.0
                
        # Select features in correct order and scale
        X = df[self.cluster_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # 3. Predict peer group
        cluster_id = int(self.clustering_model.predict(X_scaled)[0])
        cluster_key = f'cluster_{cluster_id}'
        
        # 4. Get peer benchmarks (fallback to cluster 0 if key missing)
        peer_benchmarks = self.benchmarks.get(cluster_key, self.benchmarks.get('cluster_0', {}))
        
        # 5. Calculate scores
        aov_score = self._calculate_percentile_score(
            features['aov'],
            peer_benchmarks.get('aov_p25', 0),
            peer_benchmarks.get('aov_p50', 0),
            peer_benchmarks.get('aov_p75', 0)
        )
        
        ltv_score = self._calculate_percentile_score(
            features['ltv'],
            peer_benchmarks.get('ltv_p25', 0),
            peer_benchmarks.get('ltv_p50', 0),
            peer_benchmarks.get('ltv_p75', 0)
        )
        
        rpr_score = self._calculate_percentile_score(
            features['repeat_purchase_rate'],
            peer_benchmarks.get('rpr_p25', 0),
            peer_benchmarks.get('rpr_p50', 0),
            peer_benchmarks.get('rpr_p75', 0)
        )
        
        # Calculate engagement score (campaign performance)
        engagement_score = min(100, features['campaign_engagement'] * 100)
        
        # Overall score
        overall_score = (aov_score + ltv_score + rpr_score) / 3
        
        # Gap analysis
        gap_analysis = self._generate_gap_analysis(
            features, peer_benchmarks, aov_score, ltv_score, rpr_score
        )
        
        # Improvement areas
        improvement_areas = self._identify_improvement_areas(
            aov_score, ltv_score, rpr_score, engagement_score
        )
        
        return {
            'peer_group_id': cluster_id,
            'peer_group_name': f"Peer Group {cluster_id}",
            'overall_score': round(overall_score, 1),
            'aov_score': round(aov_score, 1),
            'ltv_score': round(ltv_score, 1),
            'repeat_rate_score': round(rpr_score, 1),
            'engagement_score': round(engagement_score, 1),
            'aov_percentile': round(aov_score, 1), # Using score as proxy for percentile
            'ltv_percentile': round(ltv_score, 1),
            'repeat_rate_percentile': round(rpr_score, 1),
            'gap_analysis': json.dumps(gap_analysis),
            'improvement_areas': json.dumps(improvement_areas),
            'peer_benchmarks': json.dumps(peer_benchmarks),
            'model_version': settings.MODEL_VERSION,
            'analyzed_at': datetime.utcnow()
        }
    
    async def _extract_features(
        self,
        merchant: Merchant,
        db: AsyncSession
    ) -> Dict[str, float]:
        """Extract features for clustering"""
        
        # Order metrics
        order_result = await db.execute(
            select(
                func.count(Order.id).label('total_orders'),
                func.avg(Order.final_price).label('aov')
            ).where(Order.merchant_id == merchant.id)
        )
        order_stats = order_result.one()
        
        # Customer metrics
        customer_result = await db.execute(
            select(
                func.count(Customer.id).label('total_customers'),
                func.avg(Customer.order_count).label('avg_orders_per_customer')
            ).where(Customer.merchant_id == merchant.id)
        )
        customer_stats = customer_result.one()
        
        # Campaign engagement
        campaign_result = await db.execute(
            select(
                func.avg(Campaign.open_rate).label('avg_open_rate'),
                func.avg(Campaign.click_rate).label('avg_click_rate')
            ).where(Campaign.merchant_id == merchant.id)
        )
        campaign_stats = campaign_result.one()
        
        # Safe extraction with defaults
        total_orders = float(order_stats.total_orders or 0)
        total_customers = float(customer_stats.total_customers or 1) # Prevent div/0
        
        repeat_purchase_rate = total_orders / total_customers if total_customers > 0 else 0
        
        campaign_engagement = (
            (float(campaign_stats.avg_open_rate or 0)) + 
            (float(campaign_stats.avg_click_rate or 0))
        ) / 2
        
        return {
            'monthly_revenue': float(merchant.monthly_revenue or 0),
            'total_customers': float(total_customers),
            'total_orders': float(total_orders),
            'aov': float(order_stats.aov or 0),
            'repeat_purchase_rate': float(repeat_purchase_rate),
            'ltv': float(merchant.ltv or 0),
            'avg_orders_per_customer': float(customer_stats.avg_orders_per_customer or 0),
            'campaign_engagement': float(campaign_engagement)
        }
    
    def _calculate_percentile_score(self, value, p25, p50, p75):
        if value <= p25:
            return 25 * (value / p25) if p25 > 0 else 25
        elif value <= p50:
            return 25 + 25 * ((value - p25) / (p50 - p25)) if (p50 - p25) > 0 else 25
        elif value <= p75:
            return 50 + 25 * ((value - p50) / (p75 - p50)) if (p75 - p50) > 0 else 50
        else:
            return min(100, 75 + 25 * ((value - p75) / p75)) if p75 > 0 else 75
    
    def _generate_gap_analysis(self, features, benchmarks, aov_s, ltv_s, rpr_s):
        gaps = []
        # Simple gap analysis
        if aov_s < 50:
            gap = benchmarks.get('aov_p50', 0) - features['aov']
            gaps.append({'metric': 'AOV', 'gap': round(gap, 2)})
        return {'gaps': gaps}
    
    def _identify_improvement_areas(self, aov_s, ltv_s, rpr_s, eng_s):
        areas = []
        if aov_s < 50:
            areas.append({'area': 'Increase AOV', 'tactics': ['Bundles', 'Upsells']})
        if ltv_s < 50:
            areas.append({'area': 'Boost LTV', 'tactics': ['Loyalty', 'Retention']})
        return {'areas': areas}