import asyncio
from sqlalchemy import text
from app.core.database import async_session_factory

async def fix():
    print("🔄 Linking imported data to your Admin Account (ID 1)...")
    async with async_session_factory() as db:
        # 1. Activate your account and give it a cool name
        await db.execute(text("UPDATE merchants SET is_active=True, is_verified=True, shop_name='Bravola Premium Store' WHERE id=1"))
        
        # 2. Link ALL imported data to your account so the UI is full
        await db.execute(text("UPDATE campaigns SET merchant_id=1"))
        await db.execute(text("UPDATE orders SET merchant_id=1"))
        await db.execute(text("UPDATE customers SET merchant_id=1"))
        
        await db.commit()
    print("✅ Success! Dashboard, Campaigns, and Strategy pages are now ready.")

if __name__ == "__main__":
    asyncio.run(fix())