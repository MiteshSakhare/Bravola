"""
Webhook Endpoints for Real-Time Data Ingestion
"""
from fastapi import APIRouter, Header, Request, HTTPException, status, Depends
from typing import Optional
import hmac
import hashlib
import base64
import json

from app.core.config import settings
from app.core.logging import logger
from app.workers.tasks import sync_merchant_data

router = APIRouter()

async def verify_shopify_webhook(
    request: Request, 
    x_shopify_hmac_sha256: str = Header(None)
):
    """
    Security Middleware: Verifies that the webhook actually came from Shopify.
    Prevents hackers from faking order data.
    """
    if not x_shopify_hmac_sha256:
        raise HTTPException(status_code=401, detail="Missing HMAC header")
        
    data = await request.body()
    secret = settings.SHOPIFY_API_SECRET
    
    # Create the HMAC signature
    digest = hmac.new(
        secret.encode('utf-8'),
        data,
        hashlib.sha256
    ).digest()
    
    # Encode to base64 to match Shopify's format
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    
    if not hmac.compare_digest(computed_hmac, x_shopify_hmac_sha256):
        logger.warning(f"⚠️ Security Alert: Invalid Webhook HMAC. Computed: {computed_hmac}, Received: {x_shopify_hmac_sha256}")
        raise HTTPException(status_code=401, detail="Invalid HMAC Signature")
    
    return True

@router.post("/shopify/orders")
async def handle_order_webhook(
    request: Request,
    x_shopify_shop_domain: str = Header(None),
    verified: bool = Depends(verify_shopify_webhook)
):
    """
    Real-Time Trigger: Receives 'orders/create' or 'orders/updated'
    """
    try:
        payload = await request.json()
        order_id = payload.get('id', 'unknown')
        
        logger.info(f"⚡ Webhook received: Order {order_id} from {x_shopify_shop_domain}")
        
        # In a real scenario, you'd look up the merchant_id based on the shop_domain
        # For now, we pass 0 or look it up inside the task
        
        # Fire and Forget: Send to Celery Background Worker
        sync_merchant_data.delay(
            merchant_id=0, # The worker will resolve the ID via domain
            shop_domain=x_shopify_shop_domain,
            token="lookup_internal" 
        )
        
        return {"status": "received", "processing": "background"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Return 200 anyway to prevent Shopify from retrying indefinitely
        return {"status": "error", "message": "Logged"}