"""
Machine learning feedback and model improvement
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime, timedelta


class FeedbackLearning:
    """
    Utilities for learning from feedback and improving models
    """
    
    @staticmethod
    def calculate_prediction_accuracy(
        predictions: List[float],
        actuals: List[float]
    ) -> Dict[str, float]:
        """
        Calculate prediction accuracy metrics
        """
        if not predictions or not actuals or len(predictions) != len(actuals):
            return {
                'mae': 0,
                'rmse': 0,
                'mape': 0,
                'accuracy_score': 0
            }
        
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Mean Absolute Error
        mae = np.mean(np.abs(predictions - actuals))
        
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actuals - predictions) / np.maximum(actuals, 1))) * 100
        
        # Accuracy score (percentage within 20% tolerance)
        tolerance = 0.20
        within_tolerance = np.abs((predictions - actuals) / np.maximum(actuals, 1)) <= tolerance
        accuracy_score = np.mean(within_tolerance) * 100
        
        return {
            'mae': round(float(mae), 2),
            'rmse': round(float(rmse), 2),
            'mape': round(float(mape), 2),
            'accuracy_score': round(float(accuracy_score), 2)
        }
    
    @staticmethod
    def identify_systematic_errors(
        feedback_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify systematic errors in predictions
        """
        if not feedback_events:
            return {'errors': [], 'patterns': []}
        
        errors = []
        
        # Calculate bias (consistent over/under prediction)
        variances = [e.get('variance', 0) for e in feedback_events if e.get('variance') is not None]
        if variances:
            mean_variance = np.mean(variances)
            if abs(mean_variance) > 10:
                bias_direction = 'over' if mean_variance > 0 else 'under'
                errors.append({
                    'type': 'systematic_bias',
                    'description': f'Consistent {bias_direction}-prediction',
                    'magnitude': abs(mean_variance),
                    'recommendation': f'Adjust model baseline by {abs(mean_variance):.1f}'
                })
        
        # Identify strategy-specific errors
        strategy_performance = {}
        for event in feedback_events:
            strategy_type = event.get('strategy_type')
            if strategy_type:
                if strategy_type not in strategy_performance:
                    strategy_performance[strategy_type] = []
                strategy_performance[strategy_type].append(event.get('variance', 0))
        
        for strategy_type, variances in strategy_performance.items():
            avg_variance = np.mean(variances)
            if abs(avg_variance) > 15:
                errors.append({
                    'type': 'strategy_specific',
                    'strategy': strategy_type,
                    'variance': avg_variance,
                    'recommendation': f'Recalibrate {strategy_type} predictions'
                })
        
        return {
            'errors': errors,
            'total_events': len(feedback_events),
            'avg_variance': round(float(np.mean([abs(v) for v in variances])), 2) if variances else 0
        }
    
    @staticmethod
    def generate_model_update_suggestions(
        accuracy_metrics: Dict[str, float],
        systematic_errors: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate suggestions for model improvements
        """
        suggestions = []
        
        # Check overall accuracy
        if accuracy_metrics.get('accuracy_score', 0) < 60:
            suggestions.append({
                'priority': 'high',
                'component': 'overall_model',
                'action': 'Retrain model with updated data',
                'reason': f"Accuracy only {accuracy_metrics['accuracy_score']:.1f}%"
            })
        
        # Check MAPE
        if accuracy_metrics.get('mape', 0) > 30:
            suggestions.append({
                'priority': 'high',
                'component': 'prediction_variance',
                'action': 'Add uncertainty quantification',
                'reason': f"High prediction variance (MAPE: {accuracy_metrics['mape']:.1f}%)"
            })
        
        # Check for systematic errors
        if systematic_errors.get('errors'):
            for error in systematic_errors['errors']:
                suggestions.append({
                    'priority': 'medium',
                    'component': error['type'],
                    'action': error.get('recommendation', 'Review and adjust'),
                    'reason': error.get('description', 'Systematic error detected')
                })
        
        # General improvement if accuracy is moderate
        if 60 <= accuracy_metrics.get('accuracy_score', 0) < 80:
            suggestions.append({
                'priority': 'low',
                'component': 'feature_engineering',
                'action': 'Explore additional features',
                'reason': 'Moderate accuracy - room for improvement'
            })
        
        return suggestions
