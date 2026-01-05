"""
Local ML Training Pipeline for Bravola Mini SaaS
Trains Discovery, Benchmark, and Strategy models on synthetic data
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, silhouette_score
import xgboost as xgb

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class BravolaMLTrainer:
    """Master ML training pipeline"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data' / 'raw'
        self.artifacts_dir = Path(__file__).parent.parent.parent / 'ml_artifacts'
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.artifacts_dir / 'discovery' / 'models').mkdir(parents=True, exist_ok=True)
        (self.artifacts_dir / 'discovery' / 'preprocessors').mkdir(parents=True, exist_ok=True)
        (self.artifacts_dir / 'benchmark' / 'models').mkdir(parents=True, exist_ok=True)
        (self.artifacts_dir / 'benchmark' / 'preprocessors').mkdir(parents=True, exist_ok=True)
        (self.artifacts_dir / 'strategy' / 'models').mkdir(parents=True, exist_ok=True)
        (self.artifacts_dir / 'strategy' / 'preprocessors').mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*70)
        print("🤖 BRAVOLA ML TRAINING PIPELINE")
        print("="*70 + "\n")
    
    def load_data(self):
        """Load all synthetic data"""
        print("📂 Loading synthetic data...")
        
        self.merchants = pd.read_csv(self.data_dir / 'merchants.csv')
        self.customers = pd.read_csv(self.data_dir / 'customers.csv')
        self.orders = pd.read_csv(self.data_dir / 'orders.csv')
        self.campaigns = pd.read_csv(self.data_dir / 'campaigns.csv')
        
        print(f"   ✅ Merchants: {len(self.merchants)}")
        print(f"   ✅ Customers: {len(self.customers)}")
        print(f"   ✅ Orders: {len(self.orders)}")
        print(f"   ✅ Campaigns: {len(self.campaigns)}\n")
    
    def create_merchant_features(self):
        """Create feature matrix for merchants"""
        print("🔧 Engineering merchant features...")
        
        # Aggregate order metrics per merchant
        order_features = self.orders.groupby('merchant_id').agg({
            'order_id': 'count',
            'final_price': ['mean', 'sum', 'std'],
            'discount_amount': lambda x: (x > 0).mean(),
            'line_items_count': 'mean'
        }).reset_index()
        
        # Flatten MultiIndex columns if necessary (renaming directly)
        order_features.columns = [
            'merchant_id', 'total_orders', 'aov', 'total_revenue', 
            'order_value_std', 'discount_frequency', 'avg_items_per_order'
        ]
        
        # Customer metrics
        customer_features = self.customers.groupby('merchant_id').agg({
            'customer_id': 'count',
            'order_count': 'mean',
            'total_spent': 'mean',
            'accepts_marketing': 'mean'
        }).reset_index()
        
        customer_features.columns = [
            'merchant_id', 'total_customers', 'avg_orders_per_customer',
            'avg_customer_ltv', 'marketing_opt_in_rate'
        ]
        
        # Campaign metrics
        campaign_features = self.campaigns.groupby('merchant_id').agg({
            'campaign_id': 'count',
            'open_rate': 'mean',
            'click_rate': 'mean',
            'conversion_rate': 'mean',
            'roi': 'mean'
        }).reset_index()
        
        campaign_features.columns = [
            'merchant_id', 'total_campaigns', 'avg_open_rate', 
            'avg_click_rate', 'avg_conversion_rate', 'avg_roi'
        ]
        
        # Merge all features
        # Note: Using suffixes=('_old', '') ensures that if merchants.csv already has these columns,
        # we prioritize the newly calculated ones (Right side) and rename the old ones to avoid KeyErrors.
        features = self.merchants.merge(order_features, on='merchant_id', how='left', suffixes=('_old', ''))
        features = features.merge(customer_features, on='merchant_id', how='left', suffixes=('_old', ''))
        features = features.merge(campaign_features, on='merchant_id', how='left', suffixes=('_old', ''))
        
        # Fill missing values
        features = features.fillna(0)
        
        # Calculate derived features
        features['repeat_purchase_rate'] = (
            features['total_orders'] / features['total_customers']
        ).clip(upper=10)
        
        features['revenue_per_customer'] = (
            features['total_revenue'] / features['total_customers']
        )
        
        features['campaign_engagement'] = (
            features['avg_open_rate'] + features['avg_click_rate']
        ) / 2
        
        print(f"   ✅ Created {len(features)} feature vectors with {len(features.columns)} features\n")
        
        self.merchant_features = features
        return features
    
    def train_discovery_engine(self):
        """Train Discovery Engine - Persona & Maturity Classification"""
        print("="*70)
        print("🔍 TRAINING DISCOVERY ENGINE")
        print("="*70 + "\n")
        
        # Define feature columns
        feature_cols = [
            'monthly_revenue', 'total_customers', 'total_orders', 'aov',
            'repeat_purchase_rate', 'email_subscriber_count', 'ltv',
            'customer_acquisition_cost', 'order_value_std', 'discount_frequency',
            'avg_items_per_order', 'avg_orders_per_customer', 'marketing_opt_in_rate',
            'total_campaigns', 'avg_open_rate', 'avg_click_rate', 
            'avg_conversion_rate', 'campaign_engagement'
        ]
        
        # Ensure columns exist (handle missing columns by filling 0)
        missing_cols = [col for col in feature_cols if col not in self.merchant_features.columns]
        for col in missing_cols:
            self.merchant_features[col] = 0
            
        X = self.merchant_features[feature_cols].fillna(0)
        
        # Encode target labels
        maturity_encoder = LabelEncoder()
        y_maturity = maturity_encoder.fit_transform(self.merchant_features['maturity_stage'])
        
        # Generate persona labels based on behavior patterns
        personas = []
        for _, row in self.merchant_features.iterrows():
            if row['discount_frequency'] > 0.3:
                persona = 'Discount Discounter'
            elif row['campaign_engagement'] > 0.3:
                persona = 'Lifecycle Master'
            elif row['avg_orders_per_customer'] > 3:
                persona = 'Brand Builder'
            elif row['total_campaigns'] > 3:
                persona = 'Segment Specialist'
            else:
                persona = 'Product Pusher'
            personas.append(persona)
        
        persona_encoder = LabelEncoder()
        y_persona = persona_encoder.fit_transform(personas)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_mat_train, y_mat_test = train_test_split(
            X_scaled, y_maturity, test_size=0.2, random_state=42, stratify=y_maturity
        )
        
        _, _, y_per_train, y_per_test = train_test_split(
            X_scaled, y_persona, test_size=0.2, random_state=42, stratify=y_persona
        )
        
        # Train Maturity Classifier
        print("📊 Training Maturity Stage Classifier...")
        maturity_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        maturity_model.fit(X_train, y_mat_train)
        
        mat_score = maturity_model.score(X_test, y_mat_test)
        print(f"   ✅ Maturity Model Accuracy: {mat_score:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(maturity_model, X_scaled, y_maturity, cv=5)
        print(f"   ✅ Cross-validation Score: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
        
        # Train Persona Classifier
        print("\n📊 Training Persona Classifier...")
        persona_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        persona_model.fit(X_train, y_per_train)
        
        per_score = persona_model.score(X_test, y_per_test)
        print(f"   ✅ Persona Model Accuracy: {per_score:.3f}")
        
        # Feature importance
        print("\n📈 Top 5 Important Features:")
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': maturity_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head().iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # Save models
        print("\n💾 Saving Discovery models...")
        joblib.dump(
            maturity_model,
            self.artifacts_dir / 'discovery' / 'models' / 'maturity_classifier.joblib'
        )
        joblib.dump(
            persona_model,
            self.artifacts_dir / 'discovery' / 'models' / 'persona_classifier.joblib'
        )
        joblib.dump(
            scaler,
            self.artifacts_dir / 'discovery' / 'preprocessors' / 'feature_scaler.joblib'
        )
        joblib.dump(
            maturity_encoder,
            self.artifacts_dir / 'discovery' / 'preprocessors' / 'maturity_encoder.joblib'
        )
        joblib.dump(
            persona_encoder,
            self.artifacts_dir / 'discovery' / 'preprocessors' / 'persona_encoder.joblib'
        )
        joblib.dump(
            feature_cols,
            self.artifacts_dir / 'discovery' / 'preprocessors' / 'feature_columns.joblib'
        )
        
        print("   ✅ Models saved successfully\n")
    
    def train_benchmark_engine(self):
        """Train Benchmark Engine - Peer Clustering"""
        print("="*70)
        print("📊 TRAINING BENCHMARK ENGINE")
        print("="*70 + "\n")
        
        # Features for clustering
        cluster_features = [
            'monthly_revenue', 'total_customers', 'total_orders', 'aov',
            'repeat_purchase_rate', 'ltv', 'avg_orders_per_customer',
            'campaign_engagement'
        ]
        
        # Ensure columns exist
        missing_cols = [col for col in cluster_features if col not in self.merchant_features.columns]
        for col in missing_cols:
            self.merchant_features[col] = 0
            
        X = self.merchant_features[cluster_features].fillna(0)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine optimal number of clusters (use 5 peer groups)
        n_clusters = 5
        
        print(f"📊 Training K-Means with {n_clusters} clusters...")
        kmeans = KMeans(
            n_clusters=n_clusters,
            init='k-means++',
            n_init=10,
            max_iter=300,
            random_state=42
        )
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Calculate silhouette score
        sil_score = silhouette_score(X_scaled, cluster_labels)
        print(f"   ✅ Silhouette Score: {sil_score:.3f}")
        
        # Analyze clusters
        print("\n📈 Cluster Statistics:")
        self.merchant_features['cluster'] = cluster_labels
        
        for i in range(n_clusters):
            cluster_data = self.merchant_features[self.merchant_features['cluster'] == i]
            print(f"\n   Cluster {i} (n={len(cluster_data)}):")
            print(f"      Avg Revenue: ${cluster_data['monthly_revenue'].mean():,.0f}")
            print(f"      Avg AOV: ${cluster_data['aov'].mean():.2f}")
            if 'ltv' in cluster_data.columns:
                 print(f"      Avg LTV: ${cluster_data['ltv'].mean():.2f}")
            print(f"      Verticals: {cluster_data['vertical'].value_counts().head(3).to_dict()}")
        
        # Save models
        print("\n💾 Saving Benchmark models...")
        joblib.dump(
            kmeans,
            self.artifacts_dir / 'benchmark' / 'models' / 'peer_clustering.joblib'
        )
        joblib.dump(
            scaler,
            self.artifacts_dir / 'benchmark' / 'preprocessors' / 'cluster_scaler.joblib'
        )
        joblib.dump(
            cluster_features,
            self.artifacts_dir / 'benchmark' / 'preprocessors' / 'cluster_features.joblib'
        )
        
        # Calculate and save percentile benchmarks per cluster
        benchmarks = {}
        for i in range(n_clusters):
            cluster_data = self.merchant_features[self.merchant_features['cluster'] == i]
            benchmarks[f'cluster_{i}'] = {
                'aov_p25': cluster_data['aov'].quantile(0.25),
                'aov_p50': cluster_data['aov'].quantile(0.50),
                'aov_p75': cluster_data['aov'].quantile(0.75),
                'ltv_p25': cluster_data['ltv'].quantile(0.25) if 'ltv' in cluster_data else 0,
                'ltv_p50': cluster_data['ltv'].quantile(0.50) if 'ltv' in cluster_data else 0,
                'ltv_p75': cluster_data['ltv'].quantile(0.75) if 'ltv' in cluster_data else 0,
                'rpr_p25': cluster_data['repeat_purchase_rate'].quantile(0.25),
                'rpr_p50': cluster_data['repeat_purchase_rate'].quantile(0.50),
                'rpr_p75': cluster_data['repeat_purchase_rate'].quantile(0.75),
            }
        
        joblib.dump(
            benchmarks,
            self.artifacts_dir / 'benchmark' / 'models' / 'percentile_benchmarks.joblib'
        )
        
        print("   ✅ Models and benchmarks saved successfully\n")
    
    def train_strategy_engine(self):
        """Train Strategy Engine - XGBoost Ranker"""
        print("="*70)
        print("🎯 TRAINING STRATEGY ENGINE")
        print("="*70 + "\n")
        
        # Create strategy training data from campaign performance
        print("📊 Creating strategy training dataset...")
        
        # Define available strategies
        strategies = [
            'Welcome Series', 'Abandoned Cart', 'Win-Back', 'Post-Purchase',
            'VIP Segment', 'New Product Launch', 'Seasonal Promotion', 'Re-engagement'
        ]
        
        # Merge campaign performance with merchant features
        # Ensure we only use existing columns
        merge_cols = ['merchant_id', 'maturity_stage', 'vertical', 'monthly_revenue', 
                      'aov', 'repeat_purchase_rate', 'avg_open_rate', 'avg_click_rate', 'cluster']
        merge_cols = [c for c in merge_cols if c in self.merchant_features.columns]
        
        strategy_data = self.campaigns.merge(
            self.merchant_features[merge_cols],
            on='merchant_id'
        )
        
        # Create features for ranking
        feature_cols = [
            'monthly_revenue', 'aov', 'repeat_purchase_rate',
            'avg_open_rate', 'avg_click_rate', 'recipients'
        ]
        
        # Ensure columns exist
        for col in feature_cols:
            if col not in strategy_data.columns:
                strategy_data[col] = 0

        X = strategy_data[feature_cols].fillna(0)
        
        # Target is ROI (normalized)
        y = strategy_data['roi'].clip(lower=0, upper=1000)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train XGBoost Ranker
        print("📊 Training XGBoost Strategy Ranker...")
        
        strategy_model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        strategy_model.fit(X_train, y_train)
        
        # Evaluate
        train_score = strategy_model.score(X_train, y_train)
        test_score = strategy_model.score(X_test, y_test)
        
        print(f"   ✅ Training R²: {train_score:.3f}")
        print(f"   ✅ Test R²: {test_score:.3f}")
        
        # Feature importance
        print("\n📈 Strategy Ranking Feature Importance:")
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': strategy_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # Create strategy templates with rules
        strategy_templates = {
            'Welcome Series': {
                'min_maturity': ['Startup', 'Growth'],
                'min_subscribers': 100,
                'expected_roi': 150,
                'description': 'Automated welcome email sequence for new subscribers'
            },
            'Abandoned Cart': {
                'min_aov': 30,
                'expected_roi': 250,
                'description': 'Recover abandoned carts with reminder emails'
            },
            'Win-Back': {
                'min_customers': 200,
                'expected_roi': 180,
                'description': 'Re-engage inactive customers'
            },
            'Post-Purchase': {
                'min_orders': 100,
                'expected_roi': 140,
                'description': 'Cross-sell and upsell after purchase'
            },
            'VIP Segment': {
                'min_ltv': 200,
                'min_maturity': ['Scale-Up', 'Mature'],
                'expected_roi': 300,
                'description': 'Exclusive offers for high-value customers'
            },
            'New Product Launch': {
                'min_subscribers': 500,
                'expected_roi': 160,
                'description': 'Announce new products to engaged audience'
            },
            'Seasonal Promotion': {
                'expected_roi': 200,
                'description': 'Holiday and seasonal campaigns'
            },
            'Re-engagement': {
                'min_subscribers': 300,
                'expected_roi': 120,
                'description': 'Win back unengaged subscribers'
            }
        }
        
        # Save models
        print("\n💾 Saving Strategy models...")
        joblib.dump(
            strategy_model,
            self.artifacts_dir / 'strategy' / 'models' / 'xgboost_ranker.joblib'
        )
        joblib.dump(
            scaler,
            self.artifacts_dir / 'strategy' / 'preprocessors' / 'strategy_scaler.joblib'
        )
        joblib.dump(
            feature_cols,
            self.artifacts_dir / 'strategy' / 'preprocessors' / 'strategy_features.joblib'
        )
        joblib.dump(
            strategy_templates,
            self.artifacts_dir / 'strategy' / 'models' / 'strategy_templates.joblib'
        )
        
        print("   ✅ Models saved successfully\n")
    
    def save_metadata(self):
        """Save training metadata"""
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'num_merchants': len(self.merchants),
            'num_orders': len(self.orders),
            'num_campaigns': len(self.campaigns),
            'models': {
                'discovery': {
                    'maturity_classifier': 'RandomForestClassifier',
                    'persona_classifier': 'RandomForestClassifier'
                },
                'benchmark': {
                    'peer_clustering': 'KMeans'
                },
                'strategy': {
                    'ranker': 'XGBRegressor'
                }
            }
        }
        
        joblib.dump(metadata, self.artifacts_dir / 'training_metadata.joblib')
        print("💾 Training metadata saved\n")
    
    def run(self):
        """Execute full training pipeline"""
        try:
            self.load_data()
            self.create_merchant_features()
            self.train_discovery_engine()
            self.train_benchmark_engine()
            self.train_strategy_engine()
            self.save_metadata()
            
            print("="*70)
            print("✨ TRAINING COMPLETE!")
            print("="*70)
            print(f"\n📁 Models saved to: {self.artifacts_dir}")
            print("\nNext step: Run 'make test-ml' to test inference\n")
            
        except Exception as e:
            print(f"\n❌ Error during training: {str(e)}")
            raise


def main():
    trainer = BravolaMLTrainer()
    trainer.run()


if __name__ == "__main__":
    main()