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
            raise
    
    async def analyze_merchant(
        self,
        merchant: Merchant,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Analyze merchant and generate benchmark scores
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")
        
        logger.info(f"Running Benchmark analysis for merchant {merchant.merchant_id}")
        
        # Extract features
        features = await self._extract_features(merchant, db)
        
        # Prepare feature vector
        X = pd.DataFrame([features])[self.cluster_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict peer group
        cluster_id = int(self.clustering_model.predict(X_scaled)[0])
        cluster_key = f'cluster_{cluster_id}'
        
        # Get peer benchmarks
        peer_benchmarks = self.benchmarks[cluster_key]
        
        # Calculate scores
        aov_score = self._calculate_percentile_score(
            features['aov'],
            peer_benchmarks['aov_p25'],
            peer_benchmarks['aov_p50'],
            peer_benchmarks['aov_p75']
        )
        
        ltv_score = self._calculate_percentile_score(
            features['ltv'],
            peer_benchmarks['ltv_p25'],
            peer_benchmarks['ltv_p50'],
            peer_benchmarks['ltv_p75']
        )
        
        rpr_score = self._calculate_percentile_score(
            features['repeat_purchase_rate'],
            peer_benchmarks['rpr_p25'],
            peer_benchmarks['rpr_p50'],
            peer_benchmarks['rpr_p75']
        )
        
        # Calculate engagement score (campaign performance)
        engagement_score = features['campaign_engagement'] * 100
        
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
        
        logger.info(
            f"Benchmark complete: Cluster {cluster_id}, Overall Score {overall_score:.1f}"
        )
        
        return {
            'peer_group_id': cluster_id,
            'peer_group_name': f"Peer Group {cluster_id}",
            'overall_score': overall_score,
            'aov_score': aov_score,
            'ltv_score': ltv_score,
            'repeat_rate_score': rpr_score,
            'engagement_score': engagement_score,
            'aov_percentile': aov_score,
            'ltv_percentile': ltv_score,
            'repeat_rate_percentile': rpr_score,
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
        
        total_orders = order_stats.total_orders or 1
        total_customers = customer_stats.total_customers or 1
        repeat_purchase_rate = total_orders / total_customers
        
        campaign_engagement = (
            (campaign_stats.avg_open_rate or 0) + (campaign_stats.avg_click_rate or 0)
        ) / 2
        
        return {
            'monthly_revenue': merchant.monthly_revenue,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'aov': float(order_stats.aov or 0),
            'repeat_purchase_rate': repeat_purchase_rate,
            'ltv': merchant.ltv,
            'avg_orders_per_customer': float(customer_stats.avg_orders_per_customer or 0),
            'campaign_engagement': campaign_engagement
        }
    
    def _calculate_percentile_score(
        self,
        value: float,
        p25: float,
        p50: float,
        p75: float
    ) -> float:
        """
        Calculate percentile score (0-100)
        """
        if value <= p25:
            return 25 * (value / p25) if p25 > 0 else 25
        elif value <= p50:
            return 25 + 25 * ((value - p25) / (p50 - p25)) if (p50 - p25) > 0 else 25
        elif value <= p75:
            return 50 + 25 * ((value - p50) / (p75 - p50)) if (p75 - p50) > 0 else 50
        else:
            return min(100, 75 + 25 * ((value - p75) / p75)) if p75 > 0 else 75
    
    def _generate_gap_analysis(
        self,
        features: Dict[str, float],
        benchmarks: Dict[str, float],
        aov_score: float,
        ltv_score: float,
        rpr_score: float
    ) -> Dict[str, Any]:
        """Generate detailed gap analysis"""
        
        gaps = []
        
        if aov_score < 50:
            gap_value = benchmarks['aov_p50'] - features['aov']
            gaps.append({
                'metric': 'Average Order Value',
                'gap': f"${gap_value:.2f}",
                'target': f"${benchmarks['aov_p50']:.2f}",
                'current': f"${features['aov']:.2f}",
                'priority': 'high' if aov_score < 25 else 'medium'
            })
        
        if ltv_score < 50:
            gap_value = benchmarks['ltv_p50'] - features['ltv']
            gaps.append({
                'metric': 'Customer Lifetime Value',
                'gap': f"${gap_value:.2f}",
                'target': f"${benchmarks['ltv_p50']:.2f}",
                'current': f"${features['ltv']:.2f}",
                'priority': 'high' if ltv_score < 25 else 'medium'
            })
        
        if rpr_score < 50:
            gap_value = benchmarks['rpr_p50'] - features['repeat_purchase_rate']
            gaps.append({
                'metric': 'Repeat Purchase Rate',
                'gap': f"{gap_value:.2f}x",
                'target': f"{benchmarks['rpr_p50']:.2f}x",
                'current': f"{features['repeat_purchase_rate']:.2f}x",
                'priority': 'high' if rpr_score < 25 else 'medium'
            })
        
        return {'gaps': gaps}
    
    def _identify_improvement_areas(
        self,
        aov_score: float,
        ltv_score: float,
        rpr_score: float,
        engagement_score: float
    ) -> Dict[str, Any]:
        """Identify key improvement areas"""
        
        areas = []
        
        if aov_score < 50:
            areas.append({
                'area': 'Increase Average Order Value',
                'priority': 'high' if aov_score < 25 else 'medium',
                'tactics': [
                    'Implement product bundling',
                    'Add upsell and cross-sell recommendations',
                    'Create free shipping thresholds',
                    'Offer volume discounts'
                ]
            })
        
        if ltv_score < 50:
            areas.append({
                'area': 'Improve Customer Lifetime Value',
                'priority': 'high' if ltv_score < 25 else 'medium',
                'tactics': [
                    'Launch loyalty program',
                    'Implement subscription model',
                    'Improve customer retention',
                    'Personalize product recommendations'
                ]
            })
        
        if rpr_score < 50:
            areas.append({
                'area': 'Boost Repeat Purchases',
                'priority': 'high' if rpr_score < 25 else 'medium',
                'tactics': [
                    'Create win-back campaigns',
                    'Send post-purchase follow-ups',
                    'Offer repeat customer discounts',
                    'Implement referral program'
                ]
            })
        
        if engagement_score < 30:
            areas.append({
                'area': 'Enhance Email Engagement',
                'priority': 'medium',
                'tactics': [
                    'Segment email lists',
                    'Personalize email content',
                    'Optimize send times',
                    'A/B test subject lines'
                ]
            })
        
        return {'areas': areas}
