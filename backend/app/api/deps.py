"""
API dependencies
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.merchant import Merchant


async def get_current_merchant(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> Merchant:
    """
    Get current authenticated merchant
    """
    try:
        result = await db.execute(
            select(Merchant).where(Merchant.merchant_id == user_id)
        )
        merchant = result.scalar_one_or_none()
        
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merchant not found"
            )
        
        if not merchant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive merchant"
            )
        
        return merchant
        
    except Exception as e:
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        # Otherwise log it (in production) and return 500
        print(f"Error fetching merchant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving merchant profile"
        )