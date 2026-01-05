"""
Script to create a test user for login
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.merchant import Merchant
from sqlalchemy import select

async def create_test_user():
    async with async_session_factory() as session:
        print("🔍 Checking for existing test user...")
        
        # Check if user exists
        result = await session.execute(
            select(Merchant).where(Merchant.email == "m_1@test.com")
        )
        user = result.scalar_one_or_none()

        if user:
            print("⚠️ User 'm_1@test.com' already exists. Resetting password...")
            user.hashed_password = get_password_hash("password")
            user.is_active = True
        else:
            print("🆕 Creating new user 'm_1@test.com'...")
            user = Merchant(
                merchant_id="MERCH_TEST_001",
                email="m_1@test.com",
                hashed_password=get_password_hash("password"),
                shop_name="Bravola Test Shop",
                shop_domain="test.myshopify.com",
                vertical="Fashion",
                country="US",
                currency="USD",
                is_active=True,
                is_verified=True,
                # Set defaults for required fields to avoid crashes
                monthly_revenue=50000.0,
                total_customers=1000,
                total_orders=5000,
                aov=120.0,
                email_subscriber_count=800
            )
            session.add(user)
        
        await session.commit()
        print("\n✅ SUCCESS! User created/updated.")
        print("------------------------------------------------")
        print("📧 Email:    m_1@test.com")
        print("🔑 Password: password")
        print("------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(create_test_user())