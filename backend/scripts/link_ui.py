import asyncio
import sys
from pathlib import Path

# ✅ FIX: Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.core.database import async_session_factory

async def fix():
    print("🔄 Linking imported data to your Admin Account (ID 1)...")
    async with async_session_factory() as db:
        # 1. Activate your account and give it a cool name
        await db.execute(text("UPDATE merchants SET is_active=True, is_verified=True, shop_name='Bravola Premium Store' WHERE id=1"))
        
        # 2. Link ALL imported data to your account so the UI is full
        # We reassign all data to merchant_id=1 so you see it in the dashboard
        await db.execute(text("UPDATE campaigns SET merchant_id=1"))
        await db.execute(text("UPDATE orders SET merchant_id=1"))
        await db.execute(text("UPDATE customers SET merchant_id=1"))
        # Update derived tables if any exist
        await db.execute(text("UPDATE strategies SET merchant_id=1"))
        await db.execute(text("UPDATE discovery_profiles SET merchant_id=1"))
        await db.execute(text("UPDATE benchmark_scores SET merchant_id=1"))
        
        await db.commit()
    print("✅ Success! Dashboard, Campaigns, and Strategy pages are now ready.")

if __name__ == "__main__":
    asyncio.run(fix())