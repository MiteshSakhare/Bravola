"""
Metric calculations for benchmarking
"""

from typing import Dict, Any, List
import numpy as np


class BenchmarkMetrics:
    """
    Metric calculation utilities for benchmarking
    """
    
    @staticmethod
    def calculate_percentile(
        value: float,
        distribution: List[float]
    ) -> float:
        """
        Calculate percentile rank of value in distribution
        """
        if not distribution:
            return 50.0
        
        sorted_dist = sorted(distribution)
        position = sum(1 for x in sorted_dist if x < value)
        percentile = (position / len(sorted_dist)) * 100
        
        return round(percentile, 2)
    
    @staticmethod
    def calculate_z_score(
        value: float,
        mean: float,
        std: float
    ) -> float:
        """
        Calculate z-score (standard deviations from mean)
        """
        if std == 0:
            return 0.0
        
        z_score = (value - mean) / std
        return round(z_score, 2)
    
    @staticmethod
    def calculate_performance_score(
        value: float,
        p25: float,
        p50: float,
        p75: float
    ) -> float:
        """
        Calculate performance score (0-100) based on percentile position
        """
        if value <= p25:
            if p25 > 0:
                score = 25 * (value / p25)
            else:
                score = 25
        elif value <= p50:
            if (p50 - p25) > 0:
                score = 25 + 25 * ((value - p25) / (p50 - p25))
            else:
                score = 25
        elif value <= p75:
            if (p75 - p50) > 0:
                score = 50 + 25 * ((value - p50) / (p75 - p50))
            else:
                score = 50
        else:
            if p75 > 0:
                score = min(100, 75 + 25 * ((value - p75) / p75))
            else:
                score = 75
        
        return round(score, 2)
    
    @staticmethod
    def calculate_growth_rate(
        current_value: float,
        previous_value: float
    ) -> float:
        """
        Calculate growth rate percentage
        """
        if previous_value == 0:
            return 0.0
        
        growth_rate = ((current_value - previous_value) / previous_value) * 100
        return round(growth_rate, 2)
    
    @staticmethod
    def calculate_compound_score(
        scores: Dict[str, float],
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate weighted compound score from multiple metrics
        """
        if not scores:
            return 0.0
        
        if weights is None:
            # Equal weights
            weights = {k: 1.0 / len(scores) for k in scores.keys()}
        
        compound_score = sum(scores[k] * weights.get(k, 0) for k in scores.keys())
        return round(compound_score, 2)
    
    @staticmethod
    def generate_performance_label(score: float) -> str:
        """
        Generate human-readable performance label
        """
        if score >= 75:
            return "Excellent"
        elif score >= 60:
            return "Above Average"
        elif score >= 40:
            return "Average"
        elif score >= 25:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def calculate_improvement_potential(
        current_score: float,
        target_score: float = 75.0
    ) -> Dict[str, Any]:
        """
        Calculate improvement potential and required change
        """
        gap = target_score - current_score
        potential_pct = (gap / target_score) * 100 if target_score > 0 else 0
        
        return {
            'gap': round(gap, 2),
            'potential_percent': round(potential_pct, 2),
            'difficulty': 'easy' if gap < 15 else 'moderate' if gap < 30 else 'challenging',
            'priority': 'high' if current_score < 40 else 'medium' if current_score < 60 else 'low'
        }
