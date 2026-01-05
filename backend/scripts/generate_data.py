"""
Big Data Generator for Bravola Mini SaaS
Generates 500 Merchants, 50k Orders, focusing on Beauty & Fashion
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path

# Add parent directory to path to allow imports if needed
sys.path.append(str(Path(__file__).parent.parent))

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Configuration
NUM_MERCHANTS = 500
NUM_CUSTOMERS_PER_MERCHANT = 100
NUM_CAMPAIGNS = 1000
START_DATE = datetime.now() - timedelta(days=730)
END_DATE = datetime.now()

# Industry verticals
VERTICALS = {
    'Fashion': {
        'aov_range': (40, 120),
        'products': ['T-Shirt', 'Jeans', 'Dress', 'Shoes', 'Jacket', 'Accessories'],
        'repeat_rate': 0.35
    },
    'Electronics': {
        'aov_range': (150, 800),
        'products': ['Phone Case', 'Charger', 'Headphones', 'Monitor', 'Cable'],
        'repeat_rate': 0.20
    },
    'Beauty': {
        'aov_range': (60, 150),
        'products': ['Lipstick', 'Foundation', 'Serum', 'Moisturizer', 'Perfume', 'Mascara'],
        'repeat_rate': 0.55
    },
    'Home': {
        'aov_range': (80, 300),
        'products': ['Lamp', 'Rug', 'Pillow', 'Vase', 'Frame'],
        'repeat_rate': 0.25
    }
}

DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'
DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_merchants(n):
    print(f"Generating {n} Merchants...")
    merchants = []
    for i in range(1, n + 1):
        mid = f"MERCH_{i:04d}"
        vertical = np.random.choice(list(VERTICALS.keys()), p=[0.3, 0.2, 0.4, 0.1])
        
        # ✅ FIX: Append Merchant ID to domain to GUARANTEE uniqueness
        # Old: fake.domain_word() -> could repeat
        # New: fake.domain_word() + mid -> unique
        shop_domain = f"{fake.domain_word()}-{mid.lower().replace('_', '')}.myshopify.com"

        merchants.append({
            'merchant_id': mid,
            'shop_name': fake.company(),
            'shop_domain': shop_domain,
            'vertical': vertical,
            'created_at': fake.date_between(start_date='-2y', end_date='-1y'),
            'country': np.random.choice(['US', 'CA', 'UK', 'AU', 'DE']),
            'currency': 'USD',
            'monthly_revenue': 0, 
            'total_customers': 0,
            'total_orders': 0,
            'aov': 0,
            'repeat_purchase_rate': 0,
            'email_subscriber_count': random.randint(100, 50000),
            'maturity_stage': np.random.choice(['Startup', 'Growth', 'Scale-Up', 'Mature'], p=[0.4, 0.3, 0.2, 0.1])
        })
    return pd.DataFrame(merchants)

def generate_customers(merchants_df, customers_per_merchant):
    print("Generating Customers...")
    customers = []
    cust_counter = 1
    
    for _, merchant in merchants_df.iterrows():
        mid = merchant['merchant_id']
        count = random.randint(20, customers_per_merchant * 2)
        
        for _ in range(count):
            customers.append({
                'customer_id': f"CUST_{cust_counter:06d}",
                'merchant_id': mid,
                'email': fake.email(),
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'created_at': fake.date_between(start_date='-2y', end_date='today'),
                'country': merchant['country'],
                'accepts_marketing': random.choice([True, False]),
                'email_verified': random.choice([True, False]),
                'total_spent': 0,
                'order_count': 0
            })
            cust_counter += 1
    return pd.DataFrame(customers)

def generate_orders(customers_df, merchants_df):
    print("Generating Orders (This may take a moment)...")
    orders = []
    order_counter = 1
    
    merch_map = merchants_df.set_index('merchant_id').to_dict('index')
    
    for _, cust in customers_df.iterrows():
        mid = cust['merchant_id']
        vertical = merch_map[mid]['vertical']
        specs = VERTICALS[vertical]
        
        if random.random() > 0.2:
            num_orders = np.random.geometric(p=1.0 - specs['repeat_rate'])
            
            for _ in range(num_orders):
                price = round(random.uniform(*specs['aov_range']), 2)
                product = random.choice(specs['products'])
                
                # Construct dict first to avoid f-string syntax errors
                line_item_data = [{'product_name': product, 'price': price}]
                
                orders.append({
                    'order_id': f"ORD_{order_counter:08d}",
                    'customer_id': cust['customer_id'],
                    'merchant_id': mid,
                    'order_number': order_counter,
                    'created_at': fake.date_between(start_date=cust['created_at'], end_date='today'),
                    'total_price': price,
                    'subtotal_price': price,
                    'discount_amount': 0.0 if random.random() > 0.3 else round(price * 0.1, 2),
                    'final_price': price,
                    'line_items_count': random.randint(1, 5),
                    'line_items': str(line_item_data),
                    'financial_status': 'paid',
                    'fulfillment_status': 'fulfilled',
                    'tags': random.choice(['vip', 'new', 'repeat', ''])
                })
                order_counter += 1
                
    return pd.DataFrame(orders)

def calculate_metrics(merchants_df, orders_df, customers_df):
    print("Calculating Aggregated Metrics...")
    
    cust_stats = orders_df.groupby('customer_id').agg({
        'final_price': 'sum',
        'order_id': 'count'
    }).rename(columns={'final_price': 'total_spent', 'order_id': 'order_count'})
    
    customers_df = customers_df.set_index('customer_id')
    customers_df.update(cust_stats)
    customers_df = customers_df.reset_index()
    
    merch_stats = orders_df.groupby('merchant_id').agg({
        'final_price': 'sum',
        'order_id': 'count'
    }).rename(columns={'final_price': 'monthly_revenue', 'order_id': 'total_orders'})
    
    merch_cust_counts = customers_df.groupby('merchant_id').size().rename('total_customers')
    
    merchants_df = merchants_df.set_index('merchant_id')
    merchants_df.update(merch_stats)
    merchants_df.update(merch_cust_counts)
    
    merchants_df['aov'] = merchants_df['monthly_revenue'] / merchants_df['total_orders']
    merchants_df['monthly_revenue'] = merchants_df['monthly_revenue'] / 24 
    merchants_df = merchants_df.fillna(0).reset_index()
    
    return merchants_df, customers_df

def generate_campaigns(merchants_df):
    print("Generating Campaigns...")
    campaigns = []
    campaign_id = 1
    
    CAMPAIGN_TYPES = [
        'Welcome Series', 'Abandoned Cart', 'Win-Back', 
        'Post-Purchase', 'VIP Segment', 'New Product Launch', 
        'Seasonal Promotion', 'Re-engagement'
    ]
    
    for _, merchant in merchants_df.iterrows():
        num_campaigns = random.randint(1, 5)
        for _ in range(num_campaigns):
            campaign_type = random.choice(CAMPAIGN_TYPES)
            sent_date = fake.date_between(start_date='-6m', end_date='-1d')
            recipients = int(merchant['email_subscriber_count'] * random.uniform(0.3, 1.0))
            
            open_rate = random.uniform(0.15, 0.65)
            click_rate = open_rate * random.uniform(0.1, 0.4)
            conversion_rate = click_rate * random.uniform(0.1, 0.3)
            
            opens = int(recipients * open_rate)
            clicks = int(recipients * click_rate)
            conversions = int(recipients * conversion_rate)
            revenue = round(conversions * merchant['aov'], 2)
            
            campaigns.append({
                'campaign_id': f"CAMP_{campaign_id:06d}",
                'merchant_id': merchant['merchant_id'],
                'campaign_name': f"{campaign_type} - {sent_date.strftime('%b %Y')}",
                'campaign_type': campaign_type,
                'sent_date': sent_date,
                'recipients': recipients,
                'opens': opens,
                'clicks': clicks,
                'conversions': conversions,
                'revenue': revenue,
                'open_rate': round(open_rate, 4),
                'click_rate': round(click_rate, 4),
                'conversion_rate': round(conversion_rate, 4),
                'roi': round(revenue / (recipients * 0.01 + 1), 2),
                'status': 'completed'
            })
            campaign_id += 1
            
    return pd.DataFrame(campaigns)

def main():
    print("🚀 Starting Big Data Generation...")
    
    merchants = generate_merchants(NUM_MERCHANTS)
    customers = generate_customers(merchants, NUM_CUSTOMERS_PER_MERCHANT)
    orders = generate_orders(customers, merchants)
    merchants, customers = calculate_metrics(merchants, orders, customers)
    campaigns = generate_campaigns(merchants)
    
    print(f"💾 Saving to {DATA_DIR}...")
    merchants.to_csv(DATA_DIR / 'merchants.csv', index=False)
    customers.to_csv(DATA_DIR / 'customers.csv', index=False)
    orders.to_csv(DATA_DIR / 'orders.csv', index=False)
    campaigns.to_csv(DATA_DIR / 'campaigns.csv', index=False)
    
    print("✅ DONE! Generated:")
    print(f"   {len(merchants)} Merchants")
    print(f"   {len(customers)} Customers")
    print(f"   {len(orders)} Orders")
    print(f"   {len(campaigns)} Campaigns")

if __name__ == "__main__":
    main()