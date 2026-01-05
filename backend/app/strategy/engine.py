"""
Strategy Engine - Personalized Growth Strategy Generation
"""

import joblib
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.core.logging import logger
from app.models.merchant import Merchant
from app.models.discovery import DiscoveryProfile
from app.models.benchmark import BenchmarkScore


class StrategyEngine:
    """
    Strategy Engine for generating personalized growth strategies
    """
    
    def __init__(self):
        self.artifacts_dir = settings.ML_ARTIFACTS_PATH / 'strategy'
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load trained models and templates"""
        try:
            self.ranker_model = joblib.load(self.artifacts_dir / 'models' / 'xgboost_ranker.joblib')
            self.scaler = joblib.load(self.artifacts_dir / 'preprocessors' / 'strategy_scaler.joblib')
            self.strategy_features = joblib.load(self.artifacts_dir / 'preprocessors' / 'strategy_features.joblib')
            self.strategy_templates = joblib.load(self.artifacts_dir / 'models' / 'strategy_templates.joblib')
            self.models_loaded = True
            logger.info("Strategy Engine models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Strategy Engine models: {str(e)}")
            # Don't raise here, allow partial loading or fail gracefully later
            # raise e 
    
    async def generate_strategies(
        self,
        merchant: Merchant,
        db: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized growth strategies
        """
        if not self.models_loaded:
            # Fallback if models failed to load
            logger.warning("Models not loaded, returning empty strategy list")
            return []
        
        logger.info(f"Generating strategies for merchant {merchant.merchant_id}")
        
        # Get discovery profile
        discovery_result = await db.execute(
            select(DiscoveryProfile).where(DiscoveryProfile.merchant_id == merchant.id)
        )
        discovery = discovery_result.scalar_one_or_none()
        
        # Get benchmark scores
        benchmark_result = await db.execute(
            select(BenchmarkScore)
            .where(BenchmarkScore.merchant_id == merchant.id)
            .order_by(BenchmarkScore.analyzed_at.desc())
            .limit(1)
        )
        benchmark = benchmark_result.scalar_one_or_none()
        
        # Prepare feature vector for ranking
        features = self._prepare_ranking_features(merchant)
        X = pd.DataFrame([features])[self.strategy_features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Get base ROI prediction
        try:
            base_roi_score = self.ranker_model.predict(X_scaled)[0]
        except Exception:
            base_roi_score = 50.0  # Default fallback score
        
        # Score all strategies
        strategy_scores = []
        
        for strategy_name, template in self.strategy_templates.items():
            is_eligible = self._check_eligibility(merchant, discovery, template)
            
            priority_score = self._calculate_priority_score(
                base_roi_score, template, merchant, discovery, benchmark, is_eligible
            )
            
            action_steps = self._generate_action_steps(strategy_name, merchant)
            effort, timeline = self._estimate_effort_timeline(strategy_name, merchant)
            
            strategy_scores.append({
                'strategy_name': strategy_name,
                'strategy_type': strategy_name,
                'description': template['description'],
                'priority_score': priority_score,
                'expected_roi': template['expected_roi'],
                'estimated_revenue': self._estimate_revenue(merchant, template['expected_roi']),
                'confidence_score': 0.75 if is_eligible else 0.45,
                'action_steps': action_steps,
                'estimated_effort': effort,
                'timeline': timeline,
                'is_eligible': is_eligible,
                'reasons': self._generate_reasons(strategy_name, merchant, discovery, benchmark, is_eligible)
            })
        
        strategy_scores.sort(key=lambda x: x['priority_score'], reverse=True)
        return strategy_scores[:limit]
    
    def _prepare_ranking_features(self, merchant: Merchant) -> Dict[str, float]:
        """Prepare features for strategy ranking"""
        # ✅ FIX: Added 'or 0.0' to prevent crashes on NULL values
        return {
            'monthly_revenue': float(merchant.monthly_revenue or 0.0),
            'aov': float(merchant.aov or 0.0),
            'repeat_purchase_rate': float(merchant.repeat_purchase_rate or 0.0),
            'avg_open_rate': 0.28,
            'avg_click_rate': 0.12,
            'recipients': int(merchant.email_subscriber_count or 0)
        }
    
    def _check_eligibility(self, merchant: Merchant, discovery: DiscoveryProfile, template: Dict[str, Any]) -> bool:
        if 'min_maturity' in template:
            if discovery and discovery.maturity_stage not in template['min_maturity']:
                return False
        
        # ✅ FIX: Safety checks for numeric comparisons
        if 'min_subscribers' in template:
            if (merchant.email_subscriber_count or 0) < template['min_subscribers']:
                return False
        
        if 'min_aov' in template:
            if (merchant.aov or 0.0) < template['min_aov']:
                return False
        
        if 'min_customers' in template:
            if (merchant.total_customers or 0) < template['min_customers']:
                return False
        
        if 'min_orders' in template:
            if (merchant.total_orders or 0) < template['min_orders']:
                return False
        
        if 'min_ltv' in template:
            if (merchant.ltv or 0.0) < template['min_ltv']:
                return False
        
        return True
    
    def _calculate_priority_score(self, base_score: float, template: Dict[str, Any], merchant: Merchant, discovery: DiscoveryProfile, benchmark: BenchmarkScore, is_eligible: bool) -> float:
        score = base_score
        score *= (template['expected_roi'] / 100)
        
        if benchmark and benchmark.overall_score < 50:
            score *= 1.2
        
        if discovery:
            persona_boosts = {
                'Discount Discounter': ['Seasonal Promotion', 'VIP Segment'],
                'Brand Builder': ['Post-Purchase', 'VIP Segment'],
                'Product Pusher': ['New Product Launch'],
                'Lifecycle Master': ['Welcome Series', 'Re-engagement'],
                'Segment Specialist': ['VIP Segment', 'Abandoned Cart']
            }
            strategy_name = template.get('description', '').split()[0]
            if discovery.persona in persona_boosts:
                for boost_strategy in persona_boosts[discovery.persona]:
                    if boost_strategy in strategy_name:
                        score *= 1.15
        
        if not is_eligible:
            score *= 0.3
        
        return round(score, 2)
    
    def _generate_action_steps(self, strategy_name: str, merchant: Merchant) -> List[str]:
        action_map = {
            'Welcome Series': ['Create 3-email welcome sequence', 'Set up automation triggers', 'Design templates', 'Add exclusive discount'],
            'Abandoned Cart': ['Set up cart tracking', 'Create 2-3 reminder emails', 'Add urgency elements', 'Include recovery incentive'],
            'Win-Back': ['Identify inactive customers', 'Create win-back offer', 'Design email series', 'Track reactivation'],
            'Post-Purchase': ['Set up automation', 'Request feedback', 'Recommend products', 'Offer loyalty points'],
            'VIP Segment': ['Define VIP criteria', 'Create exclusive benefits', 'Design premium campaigns', 'Implement rewards'],
            'New Product Launch': ['Build anticipation', 'Create launch sequence', 'Segment audience', 'Offer early-bird discount'],
            'Seasonal Promotion': ['Plan campaign calendar', 'Create themed templates', 'Segment by history', 'Design offers'],
            'Re-engagement': ['Identify unengaged subscribers', 'Create re-engagement email', 'Offer return incentive', 'Clean list']
        }
        return action_map.get(strategy_name, ['Define objectives', 'Create plan', 'Design assets', 'Launch'])
    
    def _estimate_effort_timeline(self, strategy_name: str, merchant: Merchant) -> tuple:
        effort_map = {
            'Welcome Series': ('medium', '1-2 weeks'),
            'Abandoned Cart': ('medium', '1-2 weeks'),
            'Win-Back': ('low', '3-5 days'),
            'Post-Purchase': ('medium', '1-2 weeks'),
            'VIP Segment': ('high', '2-3 weeks'),
            'New Product Launch': ('medium', '1-2 weeks'),
            'Seasonal Promotion': ('low', '3-5 days'),
            'Re-engagement': ('low', '2-4 days')
        }
        return effort_map.get(strategy_name, ('medium', '1 week'))
    
    def _estimate_revenue(self, merchant: Merchant, expected_roi: float) -> float:
        # ✅ FIX: Handle NULL monthly_revenue safely
        revenue = float(merchant.monthly_revenue or 0.0)
        roi_multiplier = expected_roi / 150
        base_estimate = revenue * 0.1
        return round(base_estimate * roi_multiplier, 2)
    
    def _generate_reasons(self, strategy_name: str, merchant: Merchant, discovery: DiscoveryProfile, benchmark: BenchmarkScore, is_eligible: bool) -> List[str]:
        reasons = []
        if is_eligible: reasons.append("✓ All eligibility criteria met")
        else: reasons.append("⚠ Some requirements not yet met")
        
        if discovery:
            reasons.append(f"Aligned with '{discovery.persona}' persona")
            reasons.append(f"Suitable for '{discovery.maturity_stage}' stage")
            
        if benchmark and benchmark.overall_score < 50:
            reasons.append("Can help close performance gaps vs peers")
            
        return reasons