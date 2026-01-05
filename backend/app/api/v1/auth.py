"""
Authentication endpoints
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.config import settings
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantLogin, MerchantResponse, Token
import uuid

router = APIRouter()


@router.post("/register", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def register(
    merchant_data: MerchantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new merchant
    """
    # Check if email already exists
    result = await db.execute(
        select(Merchant).where(Merchant.email == merchant_data.email)
    )
    existing_merchant = result.scalar_one_or_none()
    
    if existing_merchant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if shop domain already exists
    result = await db.execute(
        select(Merchant).where(Merchant.shop_domain == merchant_data.shop_domain)
    )
    existing_domain = result.scalar_one_or_none()
    
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shop domain already registered"
        )
    
    # Create new merchant
    merchant = Merchant(
        merchant_id=f"MERCH_{uuid.uuid4().hex[:8].upper()}",
        email=merchant_data.email,
        hashed_password=get_password_hash(merchant_data.password),
        shop_name=merchant_data.shop_name,
        shop_domain=merchant_data.shop_domain,
        vertical=merchant_data.vertical,
        country=merchant_data.country,
        currency=merchant_data.currency,
        is_active=True,
        is_verified=False
    )
    
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    
    return merchant


@router.post("/login", response_model=Token)
async def login(
    credentials: MerchantLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token
    """
    # Find merchant by email
    result = await db.execute(
        select(Merchant).where(Merchant.email == credentials.email)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant or not verify_password(credentials.password, merchant.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not merchant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account"
        )
    
    # Create tokens
    access_token = create_access_token(
        subject=merchant.merchant_id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        subject=merchant.merchant_id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        merchant_id = payload.get("sub")
        
        # Verify merchant exists
        result = await db.execute(
            select(Merchant).where(Merchant.merchant_id == merchant_id)
        )
        merchant = result.scalar_one_or_none()
        
        if not merchant or not merchant.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create new tokens
        new_access_token = create_access_token(subject=merchant_id)
        new_refresh_token = create_refresh_token(subject=merchant_id)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
