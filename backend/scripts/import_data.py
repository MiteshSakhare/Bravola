import asyncio
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

# ✅ FIX: Add project root to system path so we can import 'app'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.core.database import async_session_factory
from app.core.security import get_password_hash

# CSV Paths
DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return None

async def get_maps(db):
    """Fetch maps of string IDs -> internal database IDs"""
    m_res = await db.execute(text("SELECT id, merchant_id FROM merchants"))
    c_res = await db.execute(text("SELECT id, customer_id FROM customers"))
    
    return (
        {row[1]: row[0] for row in m_res.all()}, # merchant_map
        {row[1]: row[0] for row in c_res.all()}  # customer_map
    )

async def import_all_data():
    async with async_session_factory() as db:
        try:
            print("🚀 Starting Data Import...")
            
            # --- 1. IMPORT MERCHANTS ---
            print(f"📦 Importing Merchants...")
            with open(DATA_DIR / 'merchants.csv', mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    await db.execute(text("""
                        INSERT INTO merchants (merchant_id, shop_name, shop_domain, vertical, country, currency, monthly_revenue, total_customers, total_orders, aov, repeat_purchase_rate, email_subscriber_count, maturity_stage, email, hashed_password, is_active, is_verified, created_at) 
                        VALUES (:mid, :name, :domain, :vert, :country, :curr, :rev, :cust, :ords, :aov, :rpr, :subs, :stage, :email, :pwd, :active, :verified, :created) 
                        ON CONFLICT (merchant_id) DO UPDATE SET monthly_revenue = :rev, total_orders = :ords
                    """), {
                        "mid": row['merchant_id'], "name": row['shop_name'], "domain": row['shop_domain'],
                        "vert": row['vertical'], "country": row['country'], "curr": row['currency'],
                        "rev": float(row['monthly_revenue']), "cust": int(row['total_customers']),
                        "ords": int(row['total_orders']), "aov": float(row['aov']),
                        "rpr": float(row['repeat_purchase_rate']), "subs": int(row['email_subscriber_count']),
                        "stage": row['maturity_stage'], "email": f"contact_{row['merchant_id']}@example.com",
                        "pwd": get_password_hash("password"), "active": True, "verified": True,
                        "created": parse_date(row['created_at'])
                    })
            await db.commit()

            # Get ID Maps
            merchant_map, customer_map = await get_maps(db)

            # --- 2. IMPORT CUSTOMERS ---
            print(f"👥 Importing Customers...")
            with open(DATA_DIR / 'customers.csv', mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                for row in reader:
                    m_db_id = merchant_map.get(row['merchant_id'])
                    if not m_db_id: continue
                    
                    batch.append({
                        "cid": row['customer_id'], "mid": m_db_id, "email": row['email'],
                        "fname": row['first_name'], "lname": row['last_name'], "country": row['country'],
                        "marketing": row['accepts_marketing'] == 'True', "verified": row['email_verified'] == 'True',
                        "spent": float(row['total_spent']), "orders": int(row['order_count']),
                        "created": parse_date(row['created_at'])
                    })
                    
                    if len(batch) >= 1000:
                        await db.execute(text("""
                            INSERT INTO customers (customer_id, merchant_id, email, first_name, last_name, country, accepts_marketing, email_verified, total_spent, order_count, created_at)
                            VALUES (:cid, :mid, :email, :fname, :lname, :country, :marketing, :verified, :spent, :orders, :created)
                            ON CONFLICT (customer_id) DO NOTHING
                        """), batch)
                        batch = []
                
                if batch:
                    await db.execute(text("""
                        INSERT INTO customers (customer_id, merchant_id, email, first_name, last_name, country, accepts_marketing, email_verified, total_spent, order_count, created_at)
                        VALUES (:cid, :mid, :email, :fname, :lname, :country, :marketing, :verified, :spent, :orders, :created)
                        ON CONFLICT (customer_id) DO NOTHING
                    """), batch)
            await db.commit()
            
            # Refresh Maps
            merchant_map, customer_map = await get_maps(db)

            # --- 3. IMPORT ORDERS ---
            print(f"🛒 Importing Orders...")
            with open(DATA_DIR / 'orders.csv', mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                for row in reader:
                    m_db_id = merchant_map.get(row['merchant_id'])
                    c_db_id = customer_map.get(row['customer_id'])
                    if not m_db_id or not c_db_id: continue

                    batch.append({
                        "oid": row['order_id'], "num": int(row['order_number']), "mid": m_db_id, "cid": c_db_id,
                        "total": float(row['total_price']), "sub": float(row['subtotal_price']),
                        "disc": float(row['discount_amount']), "final": float(row['final_price']),
                        "items": int(row['line_items_count']), "status": row['financial_status'],
                        "fulfill": row['fulfillment_status'], "tags": row['tags'],
                        "created": parse_date(row['created_at'])
                    })

                    if len(batch) >= 1000:
                        await db.execute(text("""
                            INSERT INTO orders (order_id, order_number, merchant_id, customer_id, total_price, subtotal_price, discount_amount, final_price, line_items_count, financial_status, fulfillment_status, tags, created_at)
                            VALUES (:oid, :num, :mid, :cid, :total, :sub, :disc, :final, :items, :status, :fulfill, :tags, :created)
                            ON CONFLICT (order_id) DO NOTHING
                        """), batch)
                        batch = []
                
                if batch:
                    await db.execute(text("""
                        INSERT INTO orders (order_id, order_number, merchant_id, customer_id, total_price, subtotal_price, discount_amount, final_price, line_items_count, financial_status, fulfillment_status, tags, created_at)
                        VALUES (:oid, :num, :mid, :cid, :total, :sub, :disc, :final, :items, :status, :fulfill, :tags, :created)
                        ON CONFLICT (order_id) DO NOTHING
                    """), batch)
            await db.commit()

            # --- 4. IMPORT CAMPAIGNS ---
            print(f"📧 Importing Campaigns...")
            with open(DATA_DIR / 'campaigns.csv', mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    m_db_id = merchant_map.get(row['merchant_id'])
                    if not m_db_id: continue

                    await db.execute(text("""
                        INSERT INTO campaigns (campaign_id, merchant_id, campaign_name, campaign_type, revenue, recipients, opens, clicks, conversions, roi, status, created_at) 
                        VALUES (:cid, :mid, :name, :type, :rev, :rec, :opens, :clicks, :conv, :roi, :status, :created) 
                        ON CONFLICT (campaign_id) DO NOTHING
                    """), {
                        "cid": row['campaign_id'], "mid": m_db_id, "name": row['campaign_name'],
                        "type": row['campaign_type'], "rev": float(row['revenue'] or 0),
                        "rec": int(row['recipients']), "opens": int(row['opens']),
                        "clicks": int(row['clicks']), "conv": int(row['conversions']),
                        "roi": float(row['roi']), "status": row['status'],
                        "created": parse_date(row['sent_date'])
                    })
            await db.commit()

            print("✅ ALL DATA IMPORTED SUCCESSFULLY!")

        except Exception as e:
            print(f"❌ Import Failed: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(import_all_data())