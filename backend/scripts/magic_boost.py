"""
Magic Boost Script (Deep Fix v2)
Fixes the Integer/String type mismatch for Foreign Keys
"""
import asyncio
import sys
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.core.database import async_session_factory

async def boost_merchant():
    print("✨ Applying Deep Magic Boost to Merchant 1...")
    
    async with async_session_factory() as db:
        # 1. CLEAN SLATE (Delete old cheap data for Merchant 1)
        print("🧹 Wiping old data for Merchant 1...")
        # Deleting child records first to prevent Foreign Key errors
        await db.execute(text("DELETE FROM feedback_events WHERE merchant_id = 1"))
        await db.execute(text("DELETE FROM strategies WHERE merchant_id = 1"))
        await db.execute(text("DELETE FROM benchmark_scores WHERE merchant_id = 1"))
        await db.execute(text("DELETE FROM discovery_profiles WHERE merchant_id = 1"))
        await db.execute(text("DELETE FROM campaigns WHERE merchant_id = 1"))
        await db.execute(text("DELETE FROM orders WHERE merchant_id = 1"))
        await db.execute(text("DELETE FROM customers WHERE merchant_id = 1"))
        await db.commit()

        # 2. INJECT HIGH VALUE CUSTOMERS
        print("👥 Injecting VIP Customers...")
        customers_data = []
        for i in range(50):
            c_str_id = f"VIP_{i}"
            customers_data.append({
                "cid": c_str_id, 
                "mid": 1, # Integer ID of the merchant
                "email": f"vip_{i}@example.com",
                "fname": "VIP", 
                "lname": f"Customer {i}",
                "country": "US",
                "marketing": True,
                "verified": True,
                "spent": 2000.00,
                "orders": 10,
                "created": datetime.utcnow() - timedelta(days=random.randint(1, 365))
            })
            
        await db.execute(text("""
            INSERT INTO customers (customer_id, merchant_id, email, first_name, last_name, country, accepts_marketing, email_verified, total_spent, order_count, created_at)
            VALUES (:cid, :mid, :email, :fname, :lname, :country, :marketing, :verified, :spent, :orders, :created)
        """), customers_data)
        # ✅ Commit immediately so we can fetch the generated IDs
        await db.commit() 

        # 3. FETCH GENERATED CUSTOMER IDs (The Fix)
        # We need the Internal DB ID (Integer), not the String ID "VIP_0"
        print("🔄 Mapping Customer IDs...")
        id_map = {}
        result = await db.execute(text("SELECT id, customer_id FROM customers WHERE merchant_id = 1"))
        for row in result:
            # row[0] is Integer ID, row[1] is String ID
            id_map[row[1]] = row[0] 

        # 4. INJECT HIGH VALUE ORDERS
        print("🛒 Injecting High-Ticket Orders...")
        orders_data = []
        for i in range(200): 
            price = random.uniform(150.00, 300.00)
            
            # Pick a random VIP customer string ID
            vip_str = f"VIP_{random.randint(0, 49)}"
            # Get the Integer ID from our map
            vip_int_id = id_map.get(vip_str)
            
            if not vip_int_id: continue 

            orders_data.append({
                "oid": f"ORD_BOOST_{i}",
                "num": i + 1000,
                "mid": 1,
                "cid": vip_int_id, # ✅ PASSING INTEGER HERE
                "total": price,
                "sub": price,
                "disc": 0.0,
                "final": price,
                "items": 2,
                "status": "paid",
                "fulfill": "fulfilled",
                "tags": "vip,boost",
                "created": datetime.utcnow() - timedelta(days=random.randint(1, 60))
            })

        await db.execute(text("""
            INSERT INTO orders (order_id, order_number, merchant_id, customer_id, total_price, subtotal_price, discount_amount, final_price, line_items_count, financial_status, fulfillment_status, tags, created_at)
            VALUES (:oid, :num, :mid, :cid, :total, :sub, :disc, :final, :items, :status, :fulfill, :tags, :created)
        """), orders_data)

        # 5. UPDATE MERCHANT SUMMARY
        print("📈 Updating Merchant Profile...")
        await db.execute(text("""
            UPDATE merchants 
            SET monthly_revenue = 45000.00, 
                aov = 225.50,
                total_customers = 50,
                total_orders = 200,
                repeat_purchase_rate = 0.45,
                maturity_stage = 'Scale-Up',
                vertical = 'Beauty',
                shop_name = 'Bravola Luxe Beauty'
            WHERE id = 1
        """))
        
        await db.commit()
        
    print("\n✅ DEEP BOOST COMPLETE!")
    print("👉 Go to Discovery -> Click Analyze (Should be 'Brand Builder')")
    print("👉 Go to Benchmark -> Click Analyze (Scores should be High/Green)")

if __name__ == "__main__":
    asyncio.run(boost_merchant())