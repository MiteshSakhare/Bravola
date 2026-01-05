"""
Strategy ranking and prioritization logic
"""

from typing import Dict, Any, List, Tuple
import numpy as np


class StrategyRanker:
    """
    Utilities for ranking and prioritizing strategies
    """
    
    @staticmethod
    def calculate_priority_score(
        base_score: float,
        context_factors: Dict[str, Any]
    ) -> float:
        """
        Calculate priority score with context adjustments
        """
        score = base_score
        
        # Apply context multipliers
        if context_factors.get('performance_gap', 0) > 30:
            score *= 1.2  # Boost for underperforming merchants
        
        if context_factors.get('growth_stage') == 'high_growth':
            score *= 1.15  # Boost for growth stage
        
        if context_factors.get('resource_availability') == 'high':
            score *= 1.1  # Boost if resources available
        
        # Penalize if not eligible
        if not context_factors.get('is_eligible', True):
            score *= 0.3
        
        # Cap at reasonable maximum
        return min(score, 100.0)
    
    @staticmethod
    def rank_strategies(
        strategies: List[Dict[str, Any]],
        ranking_criteria: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank strategies based on multiple criteria
        """
        if ranking_criteria is None:
            ranking_criteria = {
                'expected_roi': 0.4,
                'confidence_score': 0.3,
                'ease_of_implementation': 0.2,
                'strategic_fit': 0.1
            }
        
        for strategy in strategies:
            # Calculate composite ranking score
            ranking_score = 0
            
            # Expected ROI component
            roi_normalized = min(strategy.get('expected_roi', 0) / 300, 1.0)
            ranking_score += roi_normalized * ranking_criteria['expected_roi']
            
            # Confidence component
            ranking_score += strategy.get('confidence_score', 0) * ranking_criteria['confidence_score']
            
            # Ease of implementation (inverse of effort)
            effort_map = {'low': 1.0, 'medium': 0.6, 'high': 0.3}
            effort_score = effort_map.get(strategy.get('estimated_effort', 'medium'), 0.6)
            ranking_score += effort_score * ranking_criteria['ease_of_implementation']
            
            # Strategic fit (eligibility)
            fit_score = 1.0 if strategy.get('is_eligible', True) else 0.3
            ranking_score += fit_score * ranking_criteria['strategic_fit']
            
            strategy['ranking_score'] = round(ranking_score * 100, 2)
        
        # Sort by ranking score
        strategies.sort(key=lambda x: x.get('ranking_score', 0), reverse=True)
        
        return strategies
    
    @staticmethod
    def calculate_portfolio_score(
        selected_strategies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate overall portfolio score for selected strategies
        """
        if not selected_strategies:
            return {
                'total_expected_roi': 0,
                'avg_confidence': 0,
                'total_estimated_revenue': 0,
                'risk_level': 'unknown',
                'diversity_score': 0
            }
        
        total_roi = sum(s.get('expected_roi', 0) for s in selected_strategies)
        avg_confidence = np.mean([s.get('confidence_score', 0) for s in selected_strategies])
        total_revenue = sum(s.get('estimated_revenue', 0) for s in selected_strategies)
        
        # Calculate risk level
        low_confidence_count = sum(1 for s in selected_strategies if s.get('confidence_score', 0) < 0.6)
        risk_level = 'high' if low_confidence_count > 2 else 'medium' if low_confidence_count > 0 else 'low'
        
        # Calculate diversity (unique strategy types)
        strategy_types = set(s.get('strategy_type', '') for s in selected_strategies)
        diversity_score = len(strategy_types) / max(len(selected_strategies), 1)
        
        return {
            'total_expected_roi': round(total_roi, 2),
            'avg_confidence': round(avg_confidence, 3),
            'total_estimated_revenue': round(total_revenue, 2),
            'risk_level': risk_level,
            'diversity_score': round(diversity_score, 2),
            'strategy_count': len(selected_strategies)
        }
    
    @staticmethod
    def filter_strategies_by_constraints(
        strategies: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter strategies based on business constraints
        """
        filtered = []
        
        for strategy in strategies:
            # Check effort constraint
            if 'max_effort' in constraints:
                effort_levels = {'low': 1, 'medium': 2, 'high': 3}
                strategy_effort = effort_levels.get(strategy.get('estimated_effort', 'medium'), 2)
                max_effort = effort_levels.get(constraints['max_effort'], 3)
                
                if strategy_effort > max_effort:
                    continue
            
            # Check timeline constraint
            if 'max_timeline_weeks' in constraints:
                # Extract weeks from timeline string
                timeline = strategy.get('timeline', '1-2 weeks')
                # Simple parsing (assumes format like "1-2 weeks")
                try:
                    max_weeks = int(timeline.split()[0].split('-')[-1])
                    if max_weeks > constraints['max_timeline_weeks']:
                        continue
                except:
                    pass
            
            # Check minimum ROI
            if 'min_roi' in constraints:
                if strategy.get('expected_roi', 0) < constraints['min_roi']:
                    continue
            
            # Check eligibility requirement
            if constraints.get('eligible_only', True):
                if not strategy.get('is_eligible', True):
                    continue
            
            filtered.append(strategy)
        
        return filtered
