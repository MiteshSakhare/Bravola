"""
Discovery Engine - Merchant Persona and Maturity Classification
"""

import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
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


class DiscoveryEngine:
    """
    Discovery Engine for classifying merchants into personas and maturity stages
    """
    
    def __init__(self):
        self.artifacts_dir = settings.ML_ARTIFACTS_PATH / 'discovery'
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load trained models and preprocessors"""
        try:
            # Load models
            self.maturity_model = joblib.load(
                self.artifacts_dir / 'models' / 'maturity_classifier.joblib'
            )
            self.persona_model = joblib.load(
                self.artifacts_dir / 'models' / 'persona_classifier.joblib'
            )
            
            # Load preprocessors
            self.scaler = joblib.load(
                self.artifacts_dir / 'preprocessors' / 'feature_scaler.joblib'
            )
            self.maturity_encoder = joblib.load(
                self.artifacts_dir / 'preprocessors' / 'maturity_encoder.joblib'
            )
            self.persona_encoder = joblib.load(
                self.artifacts_dir / 'preprocessors' / 'persona_encoder.joblib'
            )
            self.feature_columns = joblib.load(
                self.artifacts_dir / 'preprocessors' / 'feature_columns.joblib'
            )
            
            self.models_loaded = True
            logger.info("Discovery Engine models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Discovery Engine models: {str(e)}")
            raise
    
    async def analyze_merchant(
        self,
        merchant: Merchant,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Analyze merchant and classify persona and maturity
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")
        
        logger.info(f"Running Discovery analysis for merchant {merchant.merchant_id}")
        
        # Extract features
        features = await self._extract_features(merchant, db)
        
        # Prepare feature vector
        X = pd.DataFrame([features])[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict maturity
        maturity_pred = self.maturity_model.predict(X_scaled)[0]
        maturity_proba = self.maturity_model.predict_proba(X_scaled)[0]
        maturity_label = self.maturity_encoder.inverse_transform([maturity_pred])[0]
        maturity_confidence = float(max(maturity_proba))
        
        # Predict persona
        persona_pred = self.persona_model.predict(X_scaled)[0]
        persona_proba = self.persona_model.predict_proba(X_scaled)[0]
        persona_label = self.persona_encoder.inverse_transform([persona_pred])[0]
        persona_confidence = float(max(persona_proba))
        
        # Get feature importance
        key_features = self._get_key_features(features)
        
        # Get persona characteristics
        persona_chars = self._get_persona_characteristics(persona_label, features)
        
        # Get maturity indicators
        maturity_inds = self._get_maturity_indicators(maturity_label, features)
        
        logger.info(
            f"Discovery complete: {persona_label} ({persona_confidence:.2f}), "
            f"{maturity_label} ({maturity_confidence:.2f})"
        )
        
        return {
            'persona': persona_label,
            'maturity_stage': maturity_label,
            'persona_confidence': persona_confidence,
            'maturity_confidence': maturity_confidence,
            'key_features': json.dumps(key_features),
            'persona_characteristics': json.dumps(persona_chars),
            'maturity_indicators': json.dumps(maturity_inds),
            'model_version': settings.MODEL_VERSION,
            'last_analyzed_at': datetime.utcnow()
        }
    
    async def _extract_features(
        self,
        merchant: Merchant,
        db: AsyncSession
    ) -> Dict[str, float]:
        """
        Extract feature vector from merchant data
        """
        # Order metrics
        order_result = await db.execute(
            select(
                func.count(Order.id).label('total_orders'),
                func.avg(Order.final_price).label('aov'),
                func.sum(Order.final_price).label('total_revenue'),
                func.stddev(Order.final_price).label('order_value_std'),
                func.avg(Order.line_items_count).label('avg_items_per_order')
            ).where(Order.merchant_id == merchant.id)
        )
        order_stats = order_result.one()
        
        # Discount frequency
        discount_result = await db.execute(
            select(func.count(Order.id))
            .where(Order.merchant_id == merchant.id, Order.discount_amount > 0)
        )
        orders_with_discount = discount_result.scalar() or 0
        total_orders = order_stats.total_orders or 1
        discount_frequency = orders_with_discount / total_orders
        
        # Customer metrics
        customer_result = await db.execute(
            select(
                func.count(Customer.id).label('total_customers'),
                func.avg(Customer.order_count).label('avg_orders_per_customer'),
                func.avg(Customer.total_spent).label('avg_customer_ltv')
            ).where(Customer.merchant_id == merchant.id)
        )
        customer_stats = customer_result.one()
        
        # Marketing opt-in rate
        marketing_result = await db.execute(
            select(func.count(Customer.id))
            .where(Customer.merchant_id == merchant.id, Customer.accepts_marketing == True)
        )
        marketing_customers = marketing_result.scalar() or 0
        total_customers = customer_stats.total_customers or 1
        marketing_opt_in_rate = marketing_customers / total_customers
        
        # Campaign metrics
        campaign_result = await db.execute(
            select(
                func.count(Campaign.id).label('total_campaigns'),
                func.avg(Campaign.open_rate).label('avg_open_rate'),
                func.avg(Campaign.click_rate).label('avg_click_rate'),
                func.avg(Campaign.conversion_rate).label('avg_conversion_rate')
            ).where(Campaign.merchant_id == merchant.id)
        )
        campaign_stats = campaign_result.one()
        
        # Calculate derived features
        repeat_purchase_rate = (total_orders / total_customers) if total_customers > 0 else 0
        campaign_engagement = (
            (campaign_stats.avg_open_rate or 0) + (campaign_stats.avg_click_rate or 0)
        ) / 2
        
        return {
            'monthly_revenue': merchant.monthly_revenue,
            'total_customers': customer_stats.total_customers or 0,
            'total_orders': total_orders,
            'aov': float(order_stats.aov or 0),
            'repeat_purchase_rate': repeat_purchase_rate,
            'email_subscriber_count': merchant.email_subscriber_count,
            'ltv': merchant.ltv,
            'customer_acquisition_cost': merchant.customer_acquisition_cost,
            'order_value_std': float(order_stats.order_value_std or 0),
            'discount_frequency': discount_frequency,
            'avg_items_per_order': float(order_stats.avg_items_per_order or 0),
            'avg_orders_per_customer': float(customer_stats.avg_orders_per_customer or 0),
            'marketing_opt_in_rate': marketing_opt_in_rate,
            'total_campaigns': campaign_stats.total_campaigns or 0,
            'avg_open_rate': float(campaign_stats.avg_open_rate or 0),
            'avg_click_rate': float(campaign_stats.avg_click_rate or 0),
            'avg_conversion_rate': float(campaign_stats.avg_conversion_rate or 0),
            'campaign_engagement': campaign_engagement,
        }
    
    def _get_key_features(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Get top contributing features"""
        # Get feature importances
        importances = self.maturity_model.feature_importances_
        
        # Sort features by importance
        feature_importance = sorted(
            zip(self.feature_columns, importances),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'top_features': [
                {
                    'name': name,
                    'value': features.get(name, 0),
                    'importance': float(imp)
                }
                for name, imp in feature_importance
            ]
        }
    
    def _get_persona_characteristics(
        self,
        persona: str,
        features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Get characteristics for the identified persona"""
        
        persona_definitions = {
            'Discount Discounter': {
                'characteristics': [
                    'High discount frequency in campaigns',
                    'Price-sensitive customer base',
                    'Focus on promotional strategies'
                ],
                'strengths': [
                    'Effective at acquiring new customers',
                    'High conversion on promotional campaigns'
                ],
                'opportunities': [
                    'Build brand loyalty beyond discounts',
                    'Increase average order value',
                    'Develop VIP segment programs'
                ]
            },
            'Brand Builder': {
                'characteristics': [
                    'High repeat purchase rate',
                    'Strong customer loyalty',
                    'Above-average customer lifetime value'
                ],
                'strengths': [
                    'Strong brand equity',
                    'Loyal customer base',
                    'Sustainable revenue growth'
                ],
                'opportunities': [
                    'Expand customer acquisition',
                    'Launch referral programs',
                    'Increase market share'
                ]
            },
            'Product Pusher': {
                'characteristics': [
                    'Focus on product variety',
                    'Broad catalog management',
                    'Average engagement metrics'
                ],
                'strengths': [
                    'Diverse product offerings',
                    'Wide market appeal'
                ],
                'opportunities': [
                    'Improve customer segmentation',
                    'Personalize marketing messages',
                    'Optimize product recommendations'
                ]
            },
            'Lifecycle Master': {
                'characteristics': [
                    'High campaign engagement',
                    'Sophisticated email marketing',
                    'Strong retention focus'
                ],
                'strengths': [
                    'Effective lifecycle campaigns',
                    'High email engagement',
                    'Data-driven marketing'
                ],
                'opportunities': [
                    'Scale successful campaigns',
                    'Test advanced automation',
                    'Expand to new channels'
                ]
            },
            'Segment Specialist': {
                'characteristics': [
                    'Multiple active campaigns',
                    'Targeted customer segments',
                    'Personalized approach'
                ],
                'strengths': [
                    'Advanced segmentation',
                    'Personalized customer experience',
                    'High conversion rates'
                ],
                'opportunities': [
                    'Automate segmentation',
                    'Implement predictive modeling',
                    'Cross-channel campaigns'
                ]
            }
        }
        
        return persona_definitions.get(persona, {
            'characteristics': ['Standard e-commerce approach'],
            'strengths': ['Balanced business model'],
            'opportunities': ['Focus on key growth areas']
        })
    
    def _get_maturity_indicators(
        self,
        maturity: str,
        features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Get indicators and next steps for maturity stage"""
        
        maturity_definitions = {
            'Startup': {
                'indicators': [
                    f"Monthly revenue: ${features['monthly_revenue']:,.0f}",
                    f"Total customers: {features['total_customers']:.0f}",
                    'Building initial customer base',
                    'Establishing market presence'
                ],
                'next_stage': [
                    'Reach $10,000+ monthly revenue',
                    'Build customer base to 200+',
                    'Achieve positive unit economics',
                    'Implement basic email automation'
                ]
            },
            'Growth': {
                'indicators': [
                    f"Monthly revenue: ${features['monthly_revenue']:,.0f}",
                    f"Total customers: {features['total_customers']:.0f}",
                    'Scaling customer acquisition',
                    'Optimizing conversion funnels'
                ],
                'next_stage': [
                    'Reach $50,000+ monthly revenue',
                    'Scale to 1,000+ customers',
                    'Implement advanced segmentation',
                    'Build retention programs'
                ]
            },
            'Scale-Up': {
                'indicators': [
                    f"Monthly revenue: ${features['monthly_revenue']:,.0f}",
                    f"Total customers: {features['total_customers']:.0f}",
                    'Rapid growth phase',
                    'Sophisticated marketing operations'
                ],
                'next_stage': [
                    'Reach $200,000+ monthly revenue',
                    'Build multi-channel presence',
                    'Implement predictive analytics',
                    'Scale operations efficiently'
                ]
            },
            'Mature': {
                'indicators': [
                    f"Monthly revenue: ${features['monthly_revenue']:,.0f}",
                    f"Total customers: {features['total_customers']:.0f}",
                    'Established market position',
                    'Focus on optimization and innovation'
                ],
                'next_stage': [
                    'Maintain market leadership',
                    'Innovate new product lines',
                    'Expand to new markets',
                    'Optimize lifetime value'
                ]
            }
        }
        
        return maturity_definitions.get(maturity, {
            'indicators': ['Standard business metrics'],
            'next_stage': ['Continue growth trajectory']
        })
