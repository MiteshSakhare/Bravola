"""
Feedback Engine - Learning from Campaign Results
"""

import json
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import logger
from app.models.feedback import FeedbackEvent
from app.models.campaign import Campaign
from app.models.strategy import Strategy


class FeedbackEngine:
    """
    Feedback Engine for learning from campaign results
    """
    
    def __init__(self):
        logger.info("Feedback Engine initialized")
    
    async def process_campaign_feedback(
        self,
        campaign: Campaign,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process feedback from completed campaign
        """
        logger.info(f"Processing feedback for campaign {campaign.campaign_id}")
        
        # Analyze campaign performance
        performance_category = self._categorize_performance(campaign)
        
        # Create feedback event
        feedback_data = {
            'campaign_type': campaign.campaign_type,
            'performance_category': performance_category,
            'open_rate': campaign.open_rate,
            'click_rate': campaign.click_rate,
            'conversion_rate': campaign.conversion_rate,
            'roi': campaign.roi
        }
        
        # Store insights for model improvement
        insights = self._extract_insights(campaign, performance_category)
        
        logger.info(f"Campaign feedback: {performance_category} performance")
        
        return {
            'performance_category': performance_category,
            'insights': insights,
            'feedback_data': feedback_data
        }
    
    async def process_strategy_feedback(
        self,
        strategy: Strategy,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process feedback from implemented strategy
        """
        logger.info(f"Processing feedback for strategy {strategy.strategy_id}")
        
        if strategy.actual_roi is None or strategy.expected_roi is None:
            return {'status': 'incomplete', 'message': 'Insufficient data'}
        
        # Compare actual vs predicted
        variance = strategy.actual_roi - strategy.expected_roi
        variance_pct = (variance / strategy.expected_roi * 100) if strategy.expected_roi > 0 else 0
        
        # Categorize accuracy
        if abs(variance_pct) < 10:
            accuracy = 'excellent'
        elif abs(variance_pct) < 25:
            accuracy = 'good'
        elif abs(variance_pct) < 50:
            accuracy = 'fair'
        else:
            accuracy = 'poor'
        
        logger.info(
            f"Strategy feedback: {accuracy} prediction "
            f"(variance: {variance_pct:.1f}%)"
        )
        
        return {
            'accuracy': accuracy,
            'variance': variance,
            'variance_percent': variance_pct,
            'actual_roi': strategy.actual_roi,
            'expected_roi': strategy.expected_roi,
            'learning_opportunity': abs(variance_pct) > 25
        }
    
    def _categorize_performance(self, campaign: Campaign) -> str:
        """Categorize campaign performance"""
        
        # Performance thresholds
        if campaign.roi > 300:
            return 'excellent'
        elif campaign.roi > 150:
            return 'good'
        elif campaign.roi > 75:
            return 'average'
        else:
            return 'poor'
    
    def _extract_insights(
        self,
        campaign: Campaign,
        performance_category: str
    ) -> Dict[str, Any]:
        """Extract actionable insights from campaign"""
        
        insights = {
            'what_worked': [],
            'what_didnt': [],
            'recommendations': []
        }
        
        # Analyze metrics
        if campaign.open_rate > 0.30:
            insights['what_worked'].append("Strong subject line and sender reputation")
        elif campaign.open_rate < 0.15:
            insights['what_didnt'].append("Low open rate - improve subject lines")
            insights['recommendations'].append("A/B test subject lines")
        
        if campaign.click_rate > 0.15:
            insights['what_worked'].append("Compelling email content and CTAs")
        elif campaign.click_rate < 0.05:
            insights['what_didnt'].append("Low engagement - content not resonating")
            insights['recommendations'].append("Improve email design and offers")
        
        if campaign.conversion_rate > 0.10:
            insights['what_worked'].append("Effective offer and landing page")
        elif campaign.conversion_rate < 0.03:
            insights['what_didnt'].append("Low conversion - friction in purchase process")
            insights['recommendations'].append("Optimize checkout flow")
        
        return insights
