"""
Strategy Engine with Orchestrator Pattern
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
    """
    Hybrid Engine: ML Ranker + Rule-Based Orchestrator
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
            # Fallback to empty templates to prevent crash
            self.strategy_templates = {}
            self.models_loaded = False
    
    async def generate_strategies(
        self,
        merchant: Merchant,
        db: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Orchestrator Pipeline:
        1. Context: Gather merchant data (Profile, Benchmarks)
        2. Candidates: Load templates
        3. Rules: Fetch & Apply DB Rules (The Orchestrator)
        4. ML: Re-rank using XGBoost + Rule Multipliers
        """
        if not self.models_loaded:
            return []
        
        # 1. Context Assembly
        # Fetch profiles for context
        discovery_res = await db.execute(select(DiscoveryProfile).where(DiscoveryProfile.merchant_id == merchant.id))
        discovery = discovery_res.scalar_one_or_none()

        benchmark_res = await db.execute(select(BenchmarkScore).where(BenchmarkScore.merchant_id == merchant.id).order_by(BenchmarkScore.analyzed_at.desc()).limit(1))
        benchmark = benchmark_res.scalar_one_or_none()

        # Build the "Context Dictionary" for Rule Evaluation
        context = {
            'revenue': float(merchant.monthly_revenue or 0),
            'aov': float(merchant.aov or 0),
            'total_customers': int(merchant.total_customers or 0),
            'email_subscribers': int(merchant.email_subscriber_count or 0),
            'persona': discovery.persona if discovery else "Unknown",
            'maturity': discovery.maturity_stage if discovery else "Startup",
            'benchmark_score': benchmark.overall_score if benchmark else 0,
            'aov_gap': (100 - benchmark.aov_score) if benchmark else 0,
        }
        
        # 2. Fetch Active Rules from DB (The Orchestrator Layer)
        rule_result = await db.execute(select(StrategyRule).where(StrategyRule.is_active == True))
        active_rules = rule_result.scalars().all()
        
        # 3. ML Baseline Scoring
        features = self._prepare_ranking_features(merchant)
        try:
            X = pd.DataFrame([features])[self.strategy_features].fillna(0)
            X_scaled = self.scaler.transform(X)
            base_ml_score = float(self.ranker_model.predict(X_scaled)[0])
        except Exception:
            base_ml_score = 50.0

        candidates = []
        
        # 4. Evaluate Candidates against Rules
        for strategy_name, template in self.strategy_templates.items():
            
            # Start with ML Score
            final_score = base_ml_score
            
            # --- ORCHESTRATOR LOGIC ---
            multiplier = 1.0
            is_filtered = False
            rule_reasons = []

            # Check Eligibility (Hard Constraints)
            if not self._check_eligibility(merchant, discovery, template):
                # Don't filter completely, just heavily penalize, unless strict
                multiplier *= 0.3
            
            # Apply Dynamic DB Rules
            for rule in active_rules:
                # Does this rule apply to this strategy type?
                if rule.target_strategy_type != "All" and rule.target_strategy_type not in template['type']:
                    continue

                # Evaluate Logic
                if self._evaluate_condition(rule, context):
                    if rule.action_type == "filter_out":
                        is_filtered = True
                        break
                    elif rule.action_type == "boost_score":
                        multiplier *= rule.impact_factor
                        rule_reasons.append(f"Matched rule: {rule.rule_name}")

            if is_filtered:
                continue
            
            final_score *= multiplier
            
            # --- END ORCHESTRATOR ---

            # Calculate Business Impact
            expected_roi = template.get('expected_roi', 150.0)
            estimated_revenue = self._estimate_revenue(merchant, expected_roi)
            
            candidates.append({
                'strategy_name': strategy_name,
                'strategy_type': template.get('type', 'Growth'),
                'description': template.get('description', ''),
                'priority_score': round(final_score, 2),
                'expected_roi': expected_roi,
                'estimated_revenue': estimated_revenue,
                'confidence_score': 0.85 if multiplier >= 1.0 else 0.50,
                'action_steps': template.get('steps', []),
                'estimated_effort': self._estimate_effort_timeline(strategy_name)[0],
                'timeline': self._estimate_effort_timeline(strategy_name)[1],
                'is_eligible': multiplier > 0.3,
                'reasons': rule_reasons + self._generate_default_reasons(discovery, benchmark)
            })
            
        # 5. Sort and Return
        candidates.sort(key=lambda x: x['priority_score'], reverse=True)
        return candidates[:limit]

    def _evaluate_condition(self, rule: StrategyRule, context: Dict[str, Any]) -> bool:
        """
        Helper: Evaluates logic like 'revenue > 1000' or 'persona == Brand Builder'
        """
        metric_val = context.get(rule.condition_metric)
        if metric_val is None:
            return False
            
        try:
            # Numeric comparison
            if isinstance(metric_val, (int, float)):
                threshold = float(rule.threshold_value)
                if rule.operator == "gt": return metric_val > threshold
                if rule.operator == "lt": return metric_val < threshold
                if rule.operator == "eq": return metric_val == threshold
            
            # String comparison
            elif isinstance(metric_val, str):
                threshold = str(rule.threshold_value)
                if rule.operator == "eq": return metric_val.lower() == threshold.lower()
                if rule.operator == "contains": return threshold.lower() in metric_val.lower()
                
        except ValueError:
            return False  # Type mismatch (comparing string to int)
            
        return False

    def _prepare_ranking_features(self, merchant: Merchant) -> Dict[str, float]:
        return {
            'monthly_revenue': float(merchant.monthly_revenue or 0.0),
            'aov': float(merchant.aov or 0.0),
            'repeat_purchase_rate': float(merchant.repeat_purchase_rate or 0.0),
            'avg_open_rate': 0.28, # Placeholder
            'avg_click_rate': 0.12, # Placeholder
            'recipients': int(merchant.email_subscriber_count or 0)
        }
    
    def _check_eligibility(self, merchant: Merchant, discovery: DiscoveryProfile, template: Dict[str, Any]) -> bool:
        if 'min_subscribers' in template:
            if (merchant.email_subscriber_count or 0) < template['min_subscribers']:
                return False
        if 'min_revenue' in template:
            if (merchant.monthly_revenue or 0) < template['min_revenue']:
                return False
        return True
    
    def _estimate_revenue(self, merchant: Merchant, expected_roi: float) -> float:
        revenue = float(merchant.monthly_revenue or 0.0)
        # Conservative estimate: 10% of monthly revenue * ROI factor
        base_impact = revenue * 0.10
        return round(base_impact * (expected_roi / 100), 2)

    def _estimate_effort_timeline(self, strategy_name: str) -> tuple:
        effort_map = {
            'Welcome Series': ('medium', '1-2 weeks'),
            'Abandoned Cart': ('medium', '1 week'),
            'VIP Segment': ('high', '2-3 weeks'),
            'Win-Back': ('low', '3 days')
        }
        # Fuzzy matching key
        for key, val in effort_map.items():
            if key in strategy_name:
                return val
        return ('medium', '1 week')

    def _generate_default_reasons(self, discovery: DiscoveryProfile, benchmark: BenchmarkScore) -> List[str]:
        reasons = []
        if discovery:
            reasons.append(f"Fits {discovery.persona} profile")
        if benchmark and benchmark.overall_score < 50:
            reasons.append("High impact potential")
        return reasons