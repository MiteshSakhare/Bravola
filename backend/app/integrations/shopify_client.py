"""
Shopify API Integration Client
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.logging import logger


class ShopifyClient:
    """
    Client for interacting with Shopify API
    """
    
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}/admin/api/{settings.SHOPIFY_API_VERSION}"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
    
    async def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/shop.json",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get('shop', {})
        except Exception as e:
            logger.error(f"Error fetching shop info: {str(e)}")
            raise
    
    async def get_orders(
        self,
        limit: int = 250,
        since: Optional[datetime] = None,
        status: str = "any"
    ) -> List[Dict[str, Any]]:
        """
        Fetch orders from Shopify
        
        Args:
            limit: Maximum number of orders to fetch
            since: Fetch orders created after this date
            status: Order status filter (any, open, closed, cancelled)
        """
        try:
            params = {
                "limit": limit,
                "status": status
            }
            
            if since:
                params["created_at_min"] = since.isoformat()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders.json",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json().get('orders', [])
        
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise
    
    async def get_customers(
        self,
        limit: int = 250,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch customers from Shopify
        
        Args:
            limit: Maximum number of customers to fetch
            since: Fetch customers created after this date
        """
        try:
            params = {"limit": limit}
            
            if since:
                params["created_at_min"] = since.isoformat()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers.json",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json().get('customers', [])
        
        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise
    
    async def get_products(
        self,
        limit: int = 250
    ) -> List[Dict[str, Any]]:
        """Fetch products from Shopify"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products.json",
                    headers=self.headers,
                    params={"limit": limit}
                )
                response.raise_for_status()
                return response.json().get('products', [])
        
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise
    
    async def get_order_metrics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate order metrics for the specified period
        
        Args:
            days: Number of days to analyze
        """
        try:
            since = datetime.utcnow() - timedelta(days=days)
            orders = await self.get_orders(limit=250, since=since)
            
            total_orders = len(orders)
            total_revenue = sum(float(order.get('total_price', 0)) for order in orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # Count unique customers
            unique_customers = len(set(
                order.get('customer', {}).get('id') 
                for order in orders 
                if order.get('customer')
            ))
            
            return {
                'total_orders': total_orders,
                'total_revenue': round(total_revenue, 2),
                'average_order_value': round(avg_order_value, 2),
                'unique_customers': unique_customers,
                'period_days': days
            }
        
        except Exception as e:
            logger.error(f"Error calculating order metrics: {str(e)}")
            raise
    
    @staticmethod
    async def verify_webhook(
        data: bytes,
        hmac_header: str,
        secret: str
    ) -> bool:
        """
        Verify Shopify webhook authenticity
        
        Args:
            data: Raw request body
            hmac_header: HMAC from request header
            secret: Shopify webhook secret
        """
        import hmac
        import hashlib
        import base64
        
        computed_hmac = base64.b64encode(
            hmac.new(
                secret.encode('utf-8'),
                data,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return hmac.compare_digest(computed_hmac, hmac_header)
