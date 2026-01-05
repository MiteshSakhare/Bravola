"""
Merchant management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.order import Order
from app.models.customer import Customer
from app.schemas.merchant import MerchantResponse, MerchantUpdate, MerchantIntegrationUpdate

router = APIRouter()

@router.get("/me", response_model=MerchantResponse)
async def read_user_me(current_merchant: Merchant = Depends(get_current_merchant)):
    # ✅ FIX: Convert None to False to prevent "ResponseValidationError" crash
    if current_merchant.shopify_connected is None:
        current_merchant.shopify_connected = False
    if current_merchant.klaviyo_connected is None:
        current_merchant.klaviyo_connected = False
        
    return current_merchant

@router.put("/me", response_model=MerchantResponse)
async def update_merchant(
    merchant_in: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    update_data = merchant_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_merchant, field, value)
    
    db.add(current_merchant)
    await db.commit()
    await db.refresh(current_merchant)
    return current_merchant

@router.put("/me/integrations", response_model=MerchantResponse)
async def update_integrations(
    integration_data: MerchantIntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Connect Shopify and Klaviyo by saving credentials
    """
    if integration_data.shopify_access_token:
        current_merchant.shopify_access_token = integration_data.shopify_access_token
        current_merchant.shopify_connected = True
        current_merchant.shop_domain = integration_data.shopify_shop_domain

    if integration_data.klaviyo_api_key:
        current_merchant.klaviyo_api_key = integration_data.klaviyo_api_key
        current_merchant.klaviyo_connected = True
        
    await db.commit()
    await db.refresh(current_merchant)
    return current_merchant

@router.get("/me/metrics")
async def get_merchant_metrics(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    # Get order metrics
    order_result = await db.execute(
        select(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.final_price).label('total_revenue'),
            func.avg(Order.final_price).label('avg_order_value')
        ).where(Order.merchant_id == current_merchant.id)
    )
    order_stats = order_result.one()
    
    # Get customer metrics
    customer_result = await db.execute(
        select(
            func.count(Customer.id).label('total_customers'),
            func.avg(Customer.order_count).label('avg_orders_per_customer')
        ).where(Customer.merchant_id == current_merchant.id)
    )
    customer_stats = customer_result.one()
    
    return {
        "total_orders": order_stats.total_orders or 0,
        "total_revenue": float(order_stats.total_revenue or 0),
        "average_order_value": float(order_stats.avg_order_value or 0),
        "total_customers": customer_stats.total_customers or 0,
        "avg_orders_per_customer": float(customer_stats.avg_orders_per_customer or 0),
        "repeat_purchase_rate": current_merchant.repeat_purchase_rate,
        "customer_lifetime_value": current_merchant.ltv
    }

@router.post("/me/sync")
async def sync_merchant_data(
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """
    Trigger data sync from Shopify/Klaviyo
    """
    return {"status": "Sync started"}