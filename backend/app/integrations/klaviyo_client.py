"""
Klaviyo API Integration Client - Two-Way Sync Enabled
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.logging import logger


class KlaviyoClient:
    """
    Client for interacting with Klaviyo API (Read & Write)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://a.klaviyo.com/api"
        # API Revision is mandatory for Klaviyo's new API
        self.headers = {
            "Authorization": f"Klaviyo-API-Key {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "revision": settings.KLAVIYO_API_VERSION
        }
    
    async def validate_connection(self) -> bool:
        """Check if API Key is valid"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/lists", headers=self.headers)
                return response.status_code == 200
        except Exception:
            return False

    # --- READ METHODS (Analysis) ---

    async def get_lists(self) -> List[Dict[str, Any]]:
        """Get all subscriber lists (for targeting)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/lists",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching lists: {str(e)}")
            return []

    async def get_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent campaigns"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/campaigns",
                    headers=self.headers,
                    params={"page[size]": limit}
                )
                response.raise_for_status()
                return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching campaigns: {str(e)}")
            return []

    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Get ROI metrics for the Feedback Loop"""
        try:
            async with httpx.AsyncClient() as client:
                # 1. Get the message ID associated with campaign
                response = await client.get(
                    f"{self.base_url}/campaigns/{campaign_id}/relationships/campaign-messages",
                    headers=self.headers
                )
                if response.status_code != 200:
                    return {}
                
                messages = response.json().get('data', [])
                if not messages:
                    return {}

                message_id = messages[0]['id']
                
                # 2. Get metrics for that message
                metrics_response = await client.get(
                    f"{self.base_url}/campaign-messages/{message_id}",
                    headers=self.headers,
                    params={"fields[campaign-message]": "opens,clicks,conversions,revenue"}
                )
                
                if metrics_response.status_code == 200:
                    attrs = metrics_response.json().get('data', {}).get('attributes', {})
                    return {
                        'opens': attrs.get('opens', 0),
                        'clicks': attrs.get('clicks', 0),
                        'conversions': attrs.get('conversions', 0),
                        'revenue': attrs.get('revenue', {}).get('amount', 0.0)
                    }
                return {}
        except Exception as e:
            logger.error(f"Metric fetch error: {e}")
            return {}

    # --- WRITE METHODS (The Execution Bridge) ---

    async def create_campaign(
        self,
        campaign_name: str,
        subject_line: str,
        list_id: str,
        html_content: str
    ) -> Optional[str]:
        """
        Create a new Email Campaign in Klaviyo.
        Returns the Campaign ID if successful.
        """
        url = f"{self.base_url}/campaigns"
        
        # 1. Construct Payload (Klaviyo API v2024 structure)
        payload = {
            "data": {
                "type": "campaign",
                "attributes": {
                    "name": campaign_name,
                    "audiences": {
                        "included": [list_id]
                    },
                    "send_strategy": {
                        "method": "static",
                        "options_static": {
                            "datetime": (datetime.utcnow() + timedelta(days=1)).isoformat()
                        }
                    },
                    "campaign_messages": {
                        "data": [
                            {
                                "type": "campaign-message",
                                "attributes": {
                                    "channel": "email",
                                    "label": campaign_name,
                                    "content": {
                                        "subject": subject_line,
                                        "from_email": "marketing@bravola.ai", # In prod, fetch from merchant settings
                                        "from_label": "Bravola AI",
                                        "reply_to_email": "support@bravola.ai",
                                        "html_body": html_content
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code in [200, 201, 202]:
                    data = response.json()
                    campaign_id = data.get('data', {}).get('id')
                    logger.info(f"✅ Created Klaviyo Campaign: {campaign_id}")
                    return campaign_id
                else:
                    logger.error(f"❌ Klaviyo Creation Failed: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating Klaviyo campaign: {str(e)}")
            return None