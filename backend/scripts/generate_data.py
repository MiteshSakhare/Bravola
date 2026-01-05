"""
Synthetic Data Generator for Bravola Mini SaaS
Generates realistic Shopify merchant, customer, order, and campaign data
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Configuration
NUM_MERCHANTS = 100
NUM_CUSTOMERS_PER_MERCHANT = 50
NUM_ORDERS_PER_CUSTOMER = (1, 20)  # Range
NUM_CAMPAIGNS = 200
START_DATE = datetime.now() - timedelta(days=730)  # 2 years of data
END_DATE = datetime.now()

# Industry verticals and their characteristics
VERTICALS = {
    'Fashion': {
        'aov_range': (40, 120),
        'products': ['T-Shirt', 'Jeans', 'Dress', 'Shoes', 'Jacket', 'Accessories'],
        'price_range': (15, 200),
        'repeat_rate': 0.35
    },
    'Electronics': {
        'aov_range': (150, 800),
        'products': ['Phone', 'Laptop', 'Tablet', 'Headphones', 'Smartwatch', 'Camera'],
        'price_range': (50, 2000),
        'repeat_rate': 0.15
    },
    'Beauty': {
        'aov_range': (30, 90),
        'products': ['Moisturizer', 'Serum', 'Lipstick', 'Perfume', 'Skincare Set'],
        'price_range': (10, 150),
        'repeat_rate': 0.45
    },
    'Home': {
        'aov_range': (60, 200),
        'products': ['Lamp', 'Cushion', 'Rug', 'Candle', 'Vase', 'Wall Art'],
        'price_range': (20, 500),
        'repeat_rate': 0.25
    },
    'Fitness': {
        'aov_range': (40, 150),
        'products': ['Yoga Mat', 'Dumbbells', 'Protein Powder', 'Resistance Bands'],
        'price_range': (15, 300),
        'repeat_rate': 0.40
    },
    'Food': {
        'aov_range': (25, 80),
        'products': ['Coffee', 'Tea', 'Snacks', 'Supplements', 'Organic Food'],
        'price_range': (10, 100),
        'repeat_rate': 0.55
    }
}

# Maturity stages
MATURITY_STAGES = ['Startup', 'Growth', 'Scale-Up', 'Mature']

# Persona types
PERSONAS = [
    'Discount Discounter',
    'Brand Builder',
    'Product Pusher',
    'Lifecycle Master',
    'Segment Specialist'
]


def generate_merchants(num_merchants):
    """Generate synthetic merchant data"""
    print(f"📊 Generating {num_merchants} merchants...")
    
    merchants = []
    for i in range(num_merchants):
        vertical = random.choice(list(VERTICALS.keys()))
        vertical_data = VERTICALS[vertical]
        
        # Business metrics vary by maturity
        maturity = random.choice(MATURITY_STAGES)
        
        if maturity == 'Startup':
            monthly_revenue = random.uniform(1000, 10000)
            total_customers = random.randint(10, 200)
        elif maturity == 'Growth':
            monthly_revenue = random.uniform(10000, 50000)
            total_customers = random.randint(200, 1000)
        elif maturity == 'Scale-Up':
            monthly_revenue = random.uniform(50000, 200000)
            total_customers = random.randint(1000, 5000)
        else:  # Mature
            monthly_revenue = random.uniform(200000, 1000000)
            total_customers = random.randint(5000, 20000)
        
        merchant = {
            'merchant_id': f"MERCH_{i+1:04d}",
            'shop_name': fake.company(),
            'shop_domain': f"{fake.domain_word()}.myshopify.com",
            'vertical': vertical,
            'created_at': fake.date_between(start_date='-5y', end_date='-6m'),
            'monthly_revenue': round(monthly_revenue, 2),
            'total_customers': total_customers,
            'total_orders': int(total_customers * random.uniform(1.2, 3.5)),
            'aov': round(random.uniform(*vertical_data['aov_range']), 2),
            'repeat_purchase_rate': round(vertical_data['repeat_rate'] * random.uniform(0.8, 1.2), 3),
            'email_subscriber_count': int(total_customers * random.uniform(0.3, 0.8)),
            'maturity_stage': maturity,
            'country': random.choice(['US', 'CA', 'UK', 'AU', 'DE']),
            'currency': random.choice(['USD', 'CAD', 'GBP', 'AUD', 'EUR']),
        }
        
        # Calculate derived metrics
        merchant['ltv'] = round(merchant['aov'] * (1 + merchant['repeat_purchase_rate'] * 2), 2)
        merchant['customer_acquisition_cost'] = round(merchant['aov'] * random.uniform(0.2, 0.5), 2)
        
        merchants.append(merchant)
    
    df = pd.DataFrame(merchants)
    print(f"✅ Generated {len(df)} merchants")
    return df


def generate_customers(merchants_df, num_customers_per_merchant):
    """Generate synthetic customer data"""
    print(f"👥 Generating customers ({num_customers_per_merchant} per merchant)...")
    
    customers = []
    customer_id = 1
    
    for _, merchant in merchants_df.iterrows():
        for _ in range(num_customers_per_merchant):
            first_order_date = fake.date_between(
                start_date=merchant['created_at'],
                end_date=END_DATE
            )
            
            customer = {
                'customer_id': f"CUST_{customer_id:06d}",
                'merchant_id': merchant['merchant_id'],
                'email': fake.email(),
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'created_at': first_order_date,
                # 'total_spent': 0,  # Will calculate from orders
                # 'order_count': 0,  # Will calculate from orders
                'country': merchant['country'],
                'accepts_marketing': random.choice([True, False]),
                'email_verified': random.choice([True, True, True, False]),  # 75% verified
            }
            
            customers.append(customer)
            customer_id += 1
    
    df = pd.DataFrame(customers)
    print(f"✅ Generated {len(df)} customers")
    return df


def generate_orders(customers_df, merchants_df):
    """Generate synthetic order data"""
    print(f"🛒 Generating orders...")
    
    orders = []
    order_id = 1
    
    # Create merchant lookup for vertical data
    merchant_lookup = merchants_df.set_index('merchant_id').to_dict('index')
    
    for _, customer in customers_df.iterrows():
        merchant = merchant_lookup[customer['merchant_id']]
        vertical_data = VERTICALS[merchant['vertical']]
        
        # Determine number of orders based on repeat rate
        num_orders = random.randint(*NUM_ORDERS_PER_CUSTOMER)
        if not customer['accepts_marketing']:
            num_orders = max(1, int(num_orders * 0.7))  # Fewer orders
        
        customer_start_date = customer['created_at']
        
        for order_num in range(num_orders):
            # Orders spread over time
            days_offset = random.randint(0, (END_DATE.date() - customer_start_date).days)
            order_date = customer_start_date + timedelta(days=days_offset)
            
            # Generate order value
            num_items = random.randint(1, 5)
            line_items = []
            total_price = 0
            
            for _ in range(num_items):
                product_name = random.choice(vertical_data['products'])
                quantity = random.randint(1, 3)
                price = round(random.uniform(*vertical_data['price_range']), 2)
                line_total = round(price * quantity, 2)
                
                line_items.append({
                    'product_name': product_name,
                    'quantity': quantity,
                    'price': price,
                    'total': line_total
                })
                total_price += line_total
            
            # Apply discount occasionally
            discount_amount = 0
            if random.random() < 0.20:  # 20% of orders have discount
                discount_amount = round(total_price * random.uniform(0.05, 0.25), 2)
            
            order = {
                'order_id': f"ORD_{order_id:08d}",
                'customer_id': customer['customer_id'],
                'merchant_id': customer['merchant_id'],
                'order_number': order_id,
                'created_at': order_date,
                'total_price': round(total_price, 2),
                'subtotal_price': round(total_price, 2),
                'discount_amount': discount_amount,
                'final_price': round(total_price - discount_amount, 2),
                'line_items_count': num_items,
                'line_items': str(line_items),
                'financial_status': random.choice(['paid', 'paid', 'paid', 'pending', 'refunded']),
                'fulfillment_status': random.choice(['fulfilled', 'fulfilled', 'partial', 'unfulfilled']),
                'tags': ','.join(random.sample(['repeat', 'high-value', 'first-time', 'discount'], k=random.randint(0, 2))),
            }
            
            orders.append(order)
            order_id += 1
    
    df = pd.DataFrame(orders)
    
    # Update customer totals
    customer_totals = df.groupby('customer_id').agg({
        'final_price': 'sum',
        'order_id': 'count'
    }).reset_index()
    customer_totals.columns = ['customer_id', 'total_spent', 'order_count']
    
    print(f"✅ Generated {len(df)} orders")
    return df, customer_totals


def generate_campaigns(merchants_df):
    """Generate synthetic marketing campaign data"""
    print(f"📧 Generating campaigns...")
    
    campaigns = []
    campaign_id = 1
    
    CAMPAIGN_TYPES = [
        'Welcome Series',
        'Abandoned Cart',
        'Win-Back',
        'Post-Purchase',
        'VIP Segment',
        'New Product Launch',
        'Seasonal Promotion',
        'Re-engagement'
    ]
    
    for _, merchant in merchants_df.iterrows():
        # Each merchant has 1-5 campaigns
        num_campaigns = random.randint(1, 5)
        
        for _ in range(num_campaigns):
            campaign_type = random.choice(CAMPAIGN_TYPES)
            sent_date = fake.date_between(start_date='-6m', end_date='-1d')
            
            # Recipients based on merchant size
            recipients = int(merchant['email_subscriber_count'] * random.uniform(0.3, 1.0))
            
            # Performance metrics vary by campaign type
            if campaign_type in ['Welcome Series', 'Post-Purchase']:
                open_rate = random.uniform(0.35, 0.65)
                click_rate = random.uniform(0.15, 0.35)
                conversion_rate = random.uniform(0.05, 0.15)
            elif campaign_type in ['Abandoned Cart', 'Win-Back']:
                open_rate = random.uniform(0.25, 0.45)
                click_rate = random.uniform(0.10, 0.25)
                conversion_rate = random.uniform(0.08, 0.20)
            else:
                open_rate = random.uniform(0.15, 0.35)
                click_rate = random.uniform(0.05, 0.15)
                conversion_rate = random.uniform(0.02, 0.08)
            
            opens = int(recipients * open_rate)
            clicks = int(opens * (click_rate / open_rate))
            conversions = int(clicks * (conversion_rate / click_rate)) if clicks > 0 else 0
            
            revenue = round(conversions * merchant['aov'] * random.uniform(0.8, 1.2), 2)
            
            campaign = {
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
                'roi': round((revenue / (recipients * 0.01)) if recipients > 0 else 0, 2),  # $0.01 cost per email
                'status': random.choice(['completed', 'completed', 'completed', 'active']),
            }
            
            campaigns.append(campaign)
            campaign_id += 1
    
    df = pd.DataFrame(campaigns)
    print(f"✅ Generated {len(df)} campaigns")
    return df


def save_data(merchants_df, customers_df, orders_df, campaigns_df):
    """Save all generated data to CSV files"""
    print(f"\n💾 Saving data to CSV files...")
    
    # Create data directory
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save datasets
    merchants_df.to_csv(data_dir / 'merchants.csv', index=False)
    customers_df.to_csv(data_dir / 'customers.csv', index=False)
    orders_df.to_csv(data_dir / 'orders.csv', index=False)
    campaigns_df.to_csv(data_dir / 'campaigns.csv', index=False)
    
    print(f"✅ Saved to {data_dir}")
    print(f"   - merchants.csv ({len(merchants_df)} rows)")
    print(f"   - customers.csv ({len(customers_df)} rows)")
    print(f"   - orders.csv ({len(orders_df)} rows)")
    print(f"   - campaigns.csv ({len(campaigns_df)} rows)")


def print_summary(merchants_df, customers_df, orders_df, campaigns_df):
    """Print data summary statistics"""
    print("\n" + "="*60)
    print("📊 DATA GENERATION SUMMARY")
    print("="*60)
    
    print(f"\n🏢 Merchants: {len(merchants_df)}")
    print(f"   Verticals: {merchants_df['vertical'].value_counts().to_dict()}")
    print(f"   Maturity: {merchants_df['maturity_stage'].value_counts().to_dict()}")
    print(f"   Avg Revenue: ${merchants_df['monthly_revenue'].mean():,.2f}")
    print(f"   Avg AOV: ${merchants_df['aov'].mean():.2f}")
    
    print(f"\n👥 Customers: {len(customers_df)}")
    print(f"   Marketing Opt-in: {customers_df['accepts_marketing'].sum()} ({customers_df['accepts_marketing'].mean()*100:.1f}%)")
    
    print(f"\n🛒 Orders: {len(orders_df)}")
    print(f"   Total GMV: ${orders_df['final_price'].sum():,.2f}")
    print(f"   Avg Order Value: ${orders_df['final_price'].mean():.2f}")
    print(f"   With Discounts: {(orders_df['discount_amount'] > 0).sum()} ({(orders_df['discount_amount'] > 0).mean()*100:.1f}%)")
    
    print(f"\n📧 Campaigns: {len(campaigns_df)}")
    print(f"   Avg Open Rate: {campaigns_df['open_rate'].mean()*100:.2f}%")
    print(f"   Avg Click Rate: {campaigns_df['click_rate'].mean()*100:.2f}%")
    print(f"   Avg Conversion: {campaigns_df['conversion_rate'].mean()*100:.2f}%")
    print(f"   Total Revenue: ${campaigns_df['revenue'].sum():,.2f}")
    
    print("\n" + "="*60)


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🚀 BRAVOLA SYNTHETIC DATA GENERATOR")
    print("="*60 + "\n")
    
    # Generate all data
    merchants_df = generate_merchants(NUM_MERCHANTS)
    customers_df = generate_customers(merchants_df, NUM_CUSTOMERS_PER_MERCHANT)
    orders_df, customer_totals = generate_orders(customers_df, merchants_df)
    
    # Update customer totals
    customers_df = customers_df.merge(customer_totals, on='customer_id', how='left')
    customers_df['total_spent'] = customers_df['total_spent'].fillna(0)
    customers_df['order_count'] = customers_df['order_count'].fillna(0).astype(int)
    
    campaigns_df = generate_campaigns(merchants_df)
    
    # Save data
    save_data(merchants_df, customers_df, orders_df, campaigns_df)
    
    # Print summary
    print_summary(merchants_df, customers_df, orders_df, campaigns_df)
    
    print("\n✨ Data generation complete!")
    print("Next step: Run 'make train' to train ML models\n")


if __name__ == "__main__":
    main()
