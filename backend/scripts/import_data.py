import asyncio
import csv
import os
import sys
from datetime import datetime
from sqlalchemy import text
from app.core.database import async_session_factory
from app.core.security import get_password_hash

# CSV Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/raw')

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
        {row[1]: row[0] for row in m_res.all()},
        {row[1]: row[0] for row in c_res.all()}
    )

async def import_all_data():
    async with async_session_factory() as db:
        try:
            # --- 1. IMPORT MERCHANTS ---
            print(f"🚀 Processing Merchants...")
            with open(os.path.join(DATA_DIR, 'merchants.csv'), mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    data = {
                        "m_id_str": row['merchant_id'],
                        "name": row['shop_name'],
                        "domain": row['shop_domain'],
                        "vertical": row['vertical'],
                        "rev": float(row['monthly_revenue'] or 0),
                        "cust": int(row['total_customers'] or 0),
                        "orders": int(row['total_orders'] or 0),
                        "aov": float(row['aov'] or 0),
                        "rpr": float(row['repeat_purchase_rate'] or 0),
                        "subs": int(row['email_subscriber_count'] or 0),
                        "stage": row['maturity_stage'],
                        "ltv": float(row['ltv'] or 0),
                        "cac": float(row['customer_acquisition_cost'] or 0),
                        "created": parse_date(row.get('created_at'))
                    }
                    if i == 0:
                        await db.execute(text("""
                            UPDATE merchants SET 
                                merchant_id=:m_id_str, shop_name=:name, shop_domain=:domain, 
                                vertical=:vertical, monthly_revenue=:rev, total_customers=:cust,
                                total_orders=:orders, aov=:aov, repeat_purchase_rate=:rpr,
                                email_subscriber_count=:subs, maturity_stage=:stage,
                                ltv=:ltv, customer_acquisition_cost=:cac, created_at=:created,
                                shopify_connected=true, klaviyo_connected=true
                            WHERE id = 1
                        """), data)
                    else:
                        data.update({"email": f"m_{i}@test.com", "pw": get_password_hash("pass")})
                        await db.execute(text("""
                            INSERT INTO merchants (email, hashed_password, merchant_id, shop_name, shop_domain, vertical, monthly_revenue, total_customers, total_orders, aov, repeat_purchase_rate, email_subscriber_count, maturity_stage, ltv, customer_acquisition_cost, created_at) 
                            VALUES (:email, :pw, :m_id_str, :name, :domain, :vertical, :rev, :cust, :orders, :aov, :rpr, :subs, :stage, :ltv, :cac, :created) 
                            ON CONFLICT DO NOTHING
                        """), data)
            
            await db.commit()
            m_map, _ = await get_maps(db)

            # --- 2. IMPORT CUSTOMERS ---
            print(f"👥 Processing Customers...")
            with open(os.path.join(DATA_DIR, 'customers.csv'), mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    m_db_id = m_map.get(row['merchant_id'])
                    if m_db_id:
                        await db.execute(text("""
                            INSERT INTO customers (customer_id, merchant_id, email, first_name, last_name, total_spent, order_count, created_at, country) 
                            VALUES (:customer_id, :m_db_id, :email, :first_name, :last_name, :spent, :count, :created, :country) 
                            ON CONFLICT DO NOTHING
                        """), {
                            "customer_id": row['customer_id'], 
                            "m_db_id": m_db_id, 
                            "email": row['email'], 
                            "first_name": row['first_name'], 
                            "last_name": row['last_name'], 
                            "spent": float(row['total_spent'] or 0), 
                            "count": int(row['order_count'] or 0),
                            "created": parse_date(row.get('created_at')),
                            "country": row.get('country', 'US')
                        })
            
            await db.commit()
            m_map, c_map = await get_maps(db)

            # --- 3. IMPORT ORDERS ---
            print(f"📦 Processing Orders...")
            with open(os.path.join(DATA_DIR, 'orders.csv'), mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    m_db_id = m_map.get(row['merchant_id'])
                    c_db_id = c_map.get(row['customer_id'])
                    if m_db_id and c_db_id:
                        # ✅ FIX: Include subtotal_price, discount_amount, final_price, etc.
                        await db.execute(text("""
                            INSERT INTO orders (order_id, customer_id, merchant_id, order_number, total_price, subtotal_price, discount_amount, final_price, line_items_count, financial_status, created_at) 
                            VALUES (:order_id, :c_db_id, :m_db_id, :order_num, :total, :subtotal, :discount, :final, :items, :status, :created) 
                            ON CONFLICT DO NOTHING
                        """), {
                            "order_id": row['order_id'], 
                            "c_db_id": c_db_id, 
                            "m_db_id": m_db_id, 
                            "order_num": int(row['order_number']), 
                            "total": float(row['total_price'] or 0),
                            "subtotal": float(row['subtotal_price'] or row['total_price'] or 0),
                            "discount": float(row['discount_amount'] or 0),
                            "final": float(row['final_price'] or row['total_price'] or 0),
                            "items": int(row['line_items_count'] or 1),
                            "status": row['financial_status'],
                            "created": parse_date(row.get('created_at'))
                        })

            # --- 4. IMPORT CAMPAIGNS ---
            print(f"📧 Processing Campaigns...")
            with open(os.path.join(DATA_DIR, 'campaigns.csv'), mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    m_db_id = m_map.get(row['merchant_id'])
                    if m_db_id:
                        await db.execute(text("""
                            INSERT INTO campaigns (campaign_id, merchant_id, campaign_name, campaign_type, revenue, recipients, opens, clicks, conversions, roi, status, created_at) 
                            VALUES (:campaign_id, :m_db_id, :name, :type, :rev, :recipients, :opens, :clicks, :convs, :roi, :status, :created) 
                            ON CONFLICT DO NOTHING
                        """), {
                            "campaign_id": row['campaign_id'], 
                            "m_db_id": m_db_id, 
                            "name": row['campaign_name'], 
                            "type": row['campaign_type'], 
                            "rev": float(row['revenue'] or 0),
                            "recipients": int(row.get('recipients', 0)),
                            "opens": int(row.get('opens', 0)),
                            "clicks": int(row.get('clicks', 0)),
                            "convs": int(row.get('conversions', 0)),
                            "roi": float(row.get('roi', 0)),
                            "status": row['status'],
                            "created": parse_date(row.get('sent_date'))
                        })

            await db.commit()
            print("✅ ALL DATA IMPORTED SUCCESSFULLY!")

        except Exception as e:
            print(f"❌ Import Failed: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(import_all_data())