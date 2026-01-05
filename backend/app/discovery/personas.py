"""
Persona definitions and characteristics
"""

from typing import Dict, Any, List
from enum import Enum


class PersonaType(str, Enum):
    """Merchant persona types"""
    DISCOUNT_DISCOUNTER = "Discount Discounter"
    BRAND_BUILDER = "Brand Builder"
    PRODUCT_PUSHER = "Product Pusher"
    LIFECYCLE_MASTER = "Lifecycle Master"
    SEGMENT_SPECIALIST = "Segment Specialist"


class PersonaDefinitions:
    """
    Detailed persona definitions and characteristics
    """
    
    PERSONAS = {
        PersonaType.DISCOUNT_DISCOUNTER: {
            'description': 'Heavy reliance on discounts and promotions to drive sales',
            'key_indicators': [
                'High discount frequency (>30%)',
                'Price-sensitive customer base',
                'Promotional campaign focus',
                'Lower profit margins'
            ],
            'typical_metrics': {
                'discount_frequency': (0.30, 0.60),
                'avg_discount_percent': (15, 35),
                'campaign_types': ['Seasonal Promotion', 'Flash Sale']
            },
            'strengths': [
                'Effective customer acquisition',
                'High conversion on promotions',
                'Strong response to urgency tactics',
                'Large email list growth'
            ],
            'weaknesses': [
                'Lower customer lifetime value',
                'Discount dependency',
                'Reduced brand equity',
                'Margin pressure'
            ],
            'growth_strategies': [
                'Transition to value-based positioning',
                'Build loyalty program',
                'Introduce premium product lines',
                'Segment high-value customers'
            ]
        },
        
        PersonaType.BRAND_BUILDER: {
            'description': 'Focus on building strong brand loyalty and repeat customers',
            'key_indicators': [
                'High repeat purchase rate (>2.5x)',
                'Strong customer loyalty',
                'Above-average LTV',
                'Premium positioning'
            ],
            'typical_metrics': {
                'repeat_purchase_rate': (2.5, 4.0),
                'customer_ltv': 'above_average',
                'brand_mentions': 'high'
            },
            'strengths': [
                'Strong brand equity',
                'Loyal customer base',
                'Word-of-mouth growth',
                'Sustainable revenue'
            ],
            'weaknesses': [
                'Slower customer acquisition',
                'Limited market reach',
                'Higher marketing costs',
                'Competition from cheaper alternatives'
            ],
            'growth_strategies': [
                'Referral program launch',
                'Influencer partnerships',
                'Content marketing expansion',
                'Community building initiatives'
            ]
        },
        
        PersonaType.PRODUCT_PUSHER: {
            'description': 'Wide product catalog with volume-focused approach',
            'key_indicators': [
                'Diverse product offerings',
                'Average engagement metrics',
                'Broad market targeting',
                'Standard marketing practices'
            ],
            'typical_metrics': {
                'product_count': 'high',
                'category_diversity': 'high',
                'avg_engagement': (0.15, 0.30)
            },
            'strengths': [
                'Wide customer appeal',
                'Diversified revenue streams',
                'Resilient to trends',
                'Cross-sell opportunities'
            ],
            'weaknesses': [
                'Lack of differentiation',
                'Lower customer connection',
                'Inventory complexity',
                'Generic positioning'
            ],
            'growth_strategies': [
                'Implement personalization',
                'Product recommendation engine',
                'Category-specific campaigns',
                'Customer segmentation'
            ]
        },
        
        PersonaType.LIFECYCLE_MASTER: {
            'description': 'Sophisticated lifecycle marketing and automation',
            'key_indicators': [
                'High email engagement (>30% open)',
                'Multiple active automations',
                'Strong retention focus',
                'Data-driven approach'
            ],
            'typical_metrics': {
                'campaign_engagement': (0.30, 0.50),
                'automation_count': 'high',
                'retention_rate': 'above_average'
            },
            'strengths': [
                'High email performance',
                'Automated revenue streams',
                'Strong customer retention',
                'Efficient marketing operations'
            ],
            'weaknesses': [
                'Dependency on email channel',
                'Requires ongoing optimization',
                'Complex setup requirements',
                'Potential list fatigue'
            ],
            'growth_strategies': [
                'Multi-channel expansion',
                'Advanced segmentation',
                'Predictive analytics',
                'SMS integration'
            ]
        },
        
        PersonaType.SEGMENT_SPECIALIST: {
            'description': 'Advanced customer segmentation and targeting',
            'key_indicators': [
                'Multiple campaign types',
                'Targeted customer segments',
                'Personalized messaging',
                'High conversion rates'
            ],
            'typical_metrics': {
                'campaign_diversity': 'high',
                'segment_count': (5, 15),
                'personalization_score': 'high'
            },
            'strengths': [
                'Precise targeting',
                'High conversion efficiency',
                'Personalized experience',
                'Optimized spend'
            ],
            'weaknesses': [
                'Operational complexity',
                'Resource intensive',
                'Requires expertise',
                'Scaling challenges'
            ],
            'growth_strategies': [
                'Automation scaling',
                'AI-powered segmentation',
                'Cross-channel orchestration',
                'Predictive modeling'
            ]
        }
    }
    
    @classmethod
    def get_persona_info(cls, persona: str) -> Dict[str, Any]:
        """Get detailed information about a persona"""
        return cls.PERSONAS.get(persona, {})
    
    @classmethod
    def get_all_personas(cls) -> List[str]:
        """Get list of all persona types"""
        return [persona.value for persona in PersonaType]
    
    @classmethod
    def get_growth_strategies(cls, persona: str) -> List[str]:
        """Get growth strategies for a specific persona"""
        persona_info = cls.get_persona_info(persona)
        return persona_info.get('growth_strategies', [])
