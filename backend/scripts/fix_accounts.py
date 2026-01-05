import asyncio
from sqlalchemy import text
from app.core.database import async_session_factory

async def fix():
    print("Opening database session...")
    async with async_session_factory() as db:
        # This makes every merchant active so you don't get 'Inactive Account'
        await db.execute(text("UPDATE merchants SET is_active=True, is_verified=True"))
        
        # This lists all your users so you know exactly which email to use
        res = await db.execute(text("SELECT id, email, shop_name FROM merchants LIMIT 10"))
        print("\n--- Available Accounts ---")
        for r in res.all():
            print(f"ID: {r[0]} | Email: {r[1]} | Shop: {r[2]}")
        
        await db.commit()
    print("\n✅ All accounts activated and verified.")

if __name__ == "__main__":
    asyncio.run(fix())