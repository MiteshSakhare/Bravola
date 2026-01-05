"""
Script to restore Admin Login (ID 1)
Sets Merchant 1 to 'admin@bravola.com' / 'password'
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.core.database import async_session_factory
from app.core.security import get_password_hash

async def restore_admin():
    print("🔧 Restoring Admin Account (ID 1)...")
    
    async with async_session_factory() as db:
        # 1. Force Merchant ID 1 to be the Admin
        new_hash = get_password_hash("password")
        
        await db.execute(text(f"""
            UPDATE merchants 
            SET email = 'admin@bravola.com',
                hashed_password = :pwd,
                shop_name = 'Bravola HQ',
                shop_domain = 'admin.myshopify.com',
                is_active = True,
                is_verified = True
            WHERE id = 1
        """), {"pwd": new_hash})
        
        # 2. Ensure all data is linked to this admin (Just in case)
        print("🔗 Linking data to Admin...")
        await db.execute(text("UPDATE campaigns SET merchant_id=1"))
        await db.execute(text("UPDATE orders SET merchant_id=1"))
        await db.execute(text("UPDATE customers SET merchant_id=1"))
        
        await db.commit()
        
    print("\n✅ LOGIN RESTORED!")
    print("------------------------------------------------")
    print("📧 Email:    admin@bravola.com")
    print("🔑 Password: password")
    print("------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(restore_admin())