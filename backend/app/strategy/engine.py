"""
Strategy Engine with Anti-Repetition Logic
"""

import joblib
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import logger
from app.models.merchant import Merchant
from app.models.discovery import DiscoveryProfile
from app.models.benchmark import BenchmarkScore
from app.models.strategy import StrategyRule

class StrategyEngine:
    
    def __init__(self):
        self.artifacts_dir = settings.ML_ARTIFACTS_PATH / 'strategy'
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        try:
            self.ranker_model = joblib.load(self.artifacts_dir / 'models' / 'xgboost_ranker.joblib')
            self.scaler = joblib.load(self.artifacts_dir / 'preprocessors' / 'strategy_scaler.joblib')
            self.strategy_features = joblib.load(self.artifacts_dir / 'preprocessors' / 'strategy_features.joblib')
            self.strategy_templates = joblib.load(self.artifacts_dir / 'models' / 'strategy_templates.joblib')
            self.models_loaded = True
        except Exception as e:
            logger.error(f"Failed to load Strategy Engine models: {str(e)}")
            self.strategy_templates = {}
            self.models_loaded = False
    
    async def generate_strategies(
        self,
        merchant: Merchant,
        db: AsyncSession,
        limit: int = 5,
        exclude_names: List[str] = None # ✅ NEW: Filter inputs
    ) -> List[Dict[str, Any]]:
        
        if not self.models_loaded: return []
        if exclude_names is None: exclude_names = []
        
        # 1. Context Assembly
        discovery_res = await db.execute(select(DiscoveryProfile).where(DiscoveryProfile.merchant_id == merchant.id))
        discovery = discovery_res.scalar_one_or_none()

        benchmark_res = await db.execute(select(BenchmarkScore).where(BenchmarkScore.merchant_id == merchant.id).order_by(BenchmarkScore.analyzed_at.desc()).limit(1))
        benchmark = benchmark_res.scalar_one_or_none()

        context = {
            'revenue': float(merchant.monthly_revenue or 0),
            'aov': float(merchant.aov or 0),
            'persona': discovery.persona if discovery else "Unknown",
            'benchmark_score': benchmark.overall_score if benchmark else 0,
        }
        
        # 2. Fetch Rules
        rule_result = await db.execute(select(StrategyRule).where(StrategyRule.is_active == True))
        active_rules = rule_result.scalars().all()
        
        # 3. Base ML Score
        features = self._prepare_ranking_features(merchant)
        try:
            X = pd.DataFrame([features])[self.strategy_features].fillna(0)
            X_scaled = self.scaler.transform(X)
            base_ml_score = float(self.ranker_model.predict(X_scaled)[0])
        except:
            base_ml_score = 50.0

        candidates = []
        
        for strategy_name, template in self.strategy_templates.items():
            
            # ✅ FIX: Skip if already generated
            if strategy_name in exclude_names:
                continue

            final_score = base_ml_score
            multiplier = 1.0
            is_filtered = False
            reasons = []

            # Check Eligibility
            if not self._check_eligibility(merchant, discovery, template):
                multiplier *= 0.3
            
            # Apply Rules
            for rule in active_rules:
                if rule.target_strategy_type != "All" and rule.target_strategy_type not in template['type']:
                    continue
                if self._evaluate_condition(rule, context):
                    if rule.action_type == "filter_out":
                        is_filtered = True; break
                    elif rule.action_type == "boost_score":
                        multiplier *= rule.impact_factor
                        reasons.append(f"Matched rule: {rule.rule_name}")

            if is_filtered: continue
            
            final_score *= multiplier
            
            # ✅ ADD JITTER: Random +/- 5% to prevent exact same ordering every time
            jitter = np.random.uniform(0.95, 1.05)
            final_score *= jitter

            candidates.append({
                'strategy_name': strategy_name,
                'strategy_type': template.get('type', 'Growth'),
                'description': template.get('description', ''),
                'priority_score': round(final_score, 2),
                'expected_roi': template.get('expected_roi', 150.0),
                'estimated_revenue': self._estimate_revenue(merchant, template.get('expected_roi', 150)),
                'confidence_score': 0.85 if multiplier >= 1.0 else 0.50,
                'action_steps': template.get('steps', []),
                'estimated_effort': self._estimate_effort_timeline(strategy_name)[0],
                'timeline': self._estimate_effort_timeline(strategy_name)[1],
                'is_eligible': multiplier > 0.3,
                'reasons': reasons
            })
            
        candidates.sort(key=lambda x: x['priority_score'], reverse=True)
        return candidates[:limit]

    # --- Helpers ---
    def _evaluate_condition(self, rule, context):
        val = context.get(rule.condition_metric)
        if val is None: return False
        try:
            if isinstance(val, (int, float)):
                t = float(rule.threshold_value)
                if rule.operator == "gt": return val > t
                if rule.operator == "lt": return val < t
                if rule.operator == "eq": return val == t
            elif isinstance(val, str):
                t = str(rule.threshold_value)
                if rule.operator == "eq": return val.lower() == t.lower()
                if rule.operator == "contains": return t.lower() in val.lower()
        except: return False
        return False

    def _prepare_ranking_features(self, merchant: Merchant) -> Dict[str, float]:
        return {
            'monthly_revenue': float(merchant.monthly_revenue or 0.0),
            'aov': float(merchant.aov or 0.0),
            'repeat_purchase_rate': float(merchant.repeat_purchase_rate or 0.0),
            'avg_open_rate': 0.28,
            'avg_click_rate': 0.12,
            'recipients': int(merchant.email_subscriber_count or 0)
        }
    
    def _check_eligibility(self, m, d, t):
        if 'min_subscribers' in t and (m.email_subscriber_count or 0) < t['min_subscribers']: return False
        if 'min_revenue' in t and (m.monthly_revenue or 0) < t['min_revenue']: return False
        return True
    
    def _estimate_revenue(self, m, roi):
        return round(float(m.monthly_revenue or 0) * 0.1 * (roi / 100), 2)

    def _estimate_effort_timeline(self, n):
        effort_map = {
            'Welcome': ('medium', '1-2 weeks'),
            'Abandoned': ('medium', '1 week'),
            'VIP': ('high', '2-3 weeks'),
            'Win-Back': ('low', '3 days')
        }
        for k, v in effort_map.items():
            if k in n: return v
        return ('medium', '1 week')