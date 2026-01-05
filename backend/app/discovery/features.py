"""
Feature engineering for Discovery Engine
"""

from typing import Dict, Any, List
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.merchant import Merchant
from app.models.order import Order
from app.models.customer import Customer
from app.models.campaign import Campaign


class DiscoveryFeatureExtractor:
    """
    Extract and engineer features for discovery analysis
    """
    
    @staticmethod
    async def extract_all_features(
        merchant: Merchant,
        db: AsyncSession
    ) -> Dict[str, float]:
        """
        Extract comprehensive feature set for merchant
        """
        features = {}
        
        # Basic merchant features
        features.update(DiscoveryFeatureExtractor._get_merchant_features(merchant))
        
        # Order-based features
        order_features = await DiscoveryFeatureExtractor._extract_order_features(
            merchant.id, db
        )
        features.update(order_features)
        
        # Customer-based features
        customer_features = await DiscoveryFeatureExtractor._extract_customer_features(
            merchant.id, db
        )
        features.update(customer_features)
        
        # Campaign-based features
        campaign_features = await DiscoveryFeatureExtractor._extract_campaign_features(
            merchant.id, db
        )
        features.update(campaign_features)
        
        # Derived features
        derived_features = DiscoveryFeatureExtractor._calculate_derived_features(features)
        features.update(derived_features)
        
        return features
    
    @staticmethod
    def _get_merchant_features(merchant: Merchant) -> Dict[str, float]:
        """Extract features from merchant model"""
        return {
            'monthly_revenue': merchant.monthly_revenue,
            'total_customers': merchant.total_customers,
            'total_orders': merchant.total_orders,
            'aov': merchant.aov,
            'repeat_purchase_rate': merchant.repeat_purchase_rate,
            'email_subscriber_count': merchant.email_subscriber_count,
            'ltv': merchant.ltv,
            'customer_acquisition_cost': merchant.customer_acquisition_cost,
        }
    
    @staticmethod
    async def _extract_order_features(
        merchant_id: int,
        db: AsyncSession
    ) -> Dict[str, float]:
        """Extract order-based features"""
        
        # Order statistics
        order_result = await db.execute(
            select(
                func.count(Order.id).label('order_count'),
                func.avg(Order.final_price).label('avg_price'),
                func.stddev(Order.final_price).label('std_price'),
                func.min(Order.final_price).label('min_price'),
                func.max(Order.final_price).label('max_price'),
                func.avg(Order.line_items_count).label('avg_items'),
                func.sum(Order.discount_amount).label('total_discounts')
            ).where(Order.merchant_id == merchant_id)
        )
        stats = order_result.one()
        
        # Discount frequency
        discount_result = await db.execute(
            select(func.count(Order.id))
            .where(Order.merchant_id == merchant_id, Order.discount_amount > 0)
        )
        discount_orders = discount_result.scalar() or 0
        total_orders = stats.order_count or 1
        
        return {
            'order_value_std': float(stats.std_price or 0),
            'min_order_value': float(stats.min_price or 0),
            'max_order_value': float(stats.max_price or 0),
            'avg_items_per_order': float(stats.avg_items or 0),
            'discount_frequency': discount_orders / total_orders,
            'total_discount_amount': float(stats.total_discounts or 0)
        }
    
    @staticmethod
    async def _extract_customer_features(
        merchant_id: int,
        db: AsyncSession
    ) -> Dict[str, float]:
        """Extract customer-based features"""
        
        # Customer statistics
        customer_result = await db.execute(
            select(
                func.count(Customer.id).label('customer_count'),
                func.avg(Customer.order_count).label('avg_orders'),
                func.avg(Customer.total_spent).label('avg_spent'),
                func.stddev(Customer.total_spent).label('std_spent')
            ).where(Customer.merchant_id == merchant_id)
        )
        stats = customer_result.one()
        
        # Marketing opt-in rate
        marketing_result = await db.execute(
            select(func.count(Customer.id))
            .where(Customer.merchant_id == merchant_id, Customer.accepts_marketing == True)
        )
        marketing_customers = marketing_result.scalar() or 0
        total_customers = stats.customer_count or 1
        
        # Email verification rate
        verified_result = await db.execute(
            select(func.count(Customer.id))
            .where(Customer.merchant_id == merchant_id, Customer.email_verified == True)
        )
        verified_customers = verified_result.scalar() or 0
        
        return {
            'avg_orders_per_customer': float(stats.avg_orders or 0),
            'avg_customer_value': float(stats.avg_spent or 0),
            'customer_value_std': float(stats.std_spent or 0),
            'marketing_opt_in_rate': marketing_customers / total_customers,
            'email_verification_rate': verified_customers / total_customers
        }
    
    @staticmethod
    async def _extract_campaign_features(
        merchant_id: int,
        db: AsyncSession
    ) -> Dict[str, float]:
        """Extract campaign-based features"""
        
        # Campaign statistics
        campaign_result = await db.execute(
            select(
                func.count(Campaign.id).label('campaign_count'),
                func.avg(Campaign.open_rate).label('avg_open'),
                func.avg(Campaign.click_rate).label('avg_click'),
                func.avg(Campaign.conversion_rate).label('avg_conversion'),
                func.avg(Campaign.roi).label('avg_roi'),
                func.sum(Campaign.revenue).label('total_revenue')
            ).where(Campaign.merchant_id == merchant_id)
        )
        stats = campaign_result.one()
        
        # Campaign diversity (count of different types)
        type_result = await db.execute(
            select(func.count(func.distinct(Campaign.campaign_type)))
            .where(Campaign.merchant_id == merchant_id)
        )
        campaign_types = type_result.scalar() or 0
        
        avg_open = float(stats.avg_open or 0)
        avg_click = float(stats.avg_click or 0)
        
        return {
            'total_campaigns': stats.campaign_count or 0,
            'avg_open_rate': avg_open,
            'avg_click_rate': avg_click,
            'avg_conversion_rate': float(stats.avg_conversion or 0),
            'avg_campaign_roi': float(stats.avg_roi or 0),
            'campaign_revenue': float(stats.total_revenue or 0),
            'campaign_diversity': campaign_types,
            'campaign_engagement': (avg_open + avg_click) / 2
        }
    
    @staticmethod
    def _calculate_derived_features(features: Dict[str, float]) -> Dict[str, float]:
        """Calculate derived features from base features"""
        
        derived = {}
        
        # Revenue concentration
        if features.get('total_customers', 0) > 0:
            derived['revenue_per_customer'] = (
                features.get('monthly_revenue', 0) / features['total_customers']
            )
        else:
            derived['revenue_per_customer'] = 0
        
        # Order efficiency
        if features.get('aov', 0) > 0:
            derived['items_per_dollar'] = (
                features.get('avg_items_per_order', 0) / features['aov']
            )
        else:
            derived['items_per_dollar'] = 0
        
        # Customer quality score
        derived['customer_quality_score'] = (
            features.get('marketing_opt_in_rate', 0) * 0.3 +
            features.get('repeat_purchase_rate', 0) * 0.4 +
            features.get('email_verification_rate', 0) * 0.3
        )
        
        # Marketing sophistication score
        derived['marketing_sophistication'] = (
            features.get('campaign_diversity', 0) * 0.3 +
            features.get('campaign_engagement', 0) * 0.4 +
            min(features.get('total_campaigns', 0) / 10, 1) * 0.3
        )
        
        return derived
