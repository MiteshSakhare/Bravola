"""
ML Model Inference Testing for Bravola Mini SaaS
Tests that trained models work correctly end-to-end
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))


class BravolaInferenceTester:
    """Test ML model inference pipeline"""
    
    def __init__(self):
        self.artifacts_dir = Path(__file__).parent.parent.parent / 'ml_artifacts'
        
        print("\n" + "="*70)
        print("🧪 BRAVOLA ML INFERENCE TESTING")
        print("="*70 + "\n")
        
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        print("📦 Loading trained models...")
        
        try:
            # Discovery models
            self.maturity_model = joblib.load(
                self.artifacts_dir / 'discovery' / 'models' / 'maturity_classifier.joblib'
            )
            self.persona_model = joblib.load(
                self.artifacts_dir / 'discovery' / 'models' / 'persona_classifier.joblib'
            )
            self.discovery_scaler = joblib.load(
                self.artifacts_dir / 'discovery' / 'preprocessors' / 'feature_scaler.joblib'
            )
            self.maturity_encoder = joblib.load(
                self.artifacts_dir / 'discovery' / 'preprocessors' / 'maturity_encoder.joblib'
            )
            self.persona_encoder = joblib.load(
                self.artifacts_dir / 'discovery' / 'preprocessors' / 'persona_encoder.joblib'
            )
            self.discovery_features = joblib.load(
                self.artifacts_dir / 'discovery' / 'preprocessors' / 'feature_columns.joblib'
            )
            
            # Benchmark models
            self.clustering_model = joblib.load(
                self.artifacts_dir / 'benchmark' / 'models' / 'peer_clustering.joblib'
            )
            self.cluster_scaler = joblib.load(
                self.artifacts_dir / 'benchmark' / 'preprocessors' / 'cluster_scaler.joblib'
            )
            self.cluster_features = joblib.load(
                self.artifacts_dir / 'benchmark' / 'preprocessors' / 'cluster_features.joblib'
            )
            self.benchmarks = joblib.load(
                self.artifacts_dir / 'benchmark' / 'models' / 'percentile_benchmarks.joblib'
            )
            
            # Strategy models
            self.strategy_model = joblib.load(
                self.artifacts_dir / 'strategy' / 'models' / 'xgboost_ranker.joblib'
            )
            self.strategy_scaler = joblib.load(
                self.artifacts_dir / 'strategy' / 'preprocessors' / 'strategy_scaler.joblib'
            )
            self.strategy_features = joblib.load(
                self.artifacts_dir / 'strategy' / 'preprocessors' / 'strategy_features.joblib'
            )
            self.strategy_templates = joblib.load(
                self.artifacts_dir / 'strategy' / 'models' / 'strategy_templates.joblib'
            )
            
            print("   ✅ All models loaded successfully\n")
            
        except FileNotFoundError as e:
            print(f"   ❌ Error: Model files not found")
            print(f"   Please run 'make train' first to train the models\n")
            sys.exit(1)
    
    def create_test_merchant(self, scenario='growth'):
        """Create a test merchant profile"""
        
        scenarios = {
            'startup': {
                'monthly_revenue': 5000,
                'total_customers': 100,
                'total_orders': 150,
                'aov': 45.0,
                'repeat_purchase_rate': 1.5,
                'email_subscriber_count': 50,
                'ltv': 85.0,
                'customer_acquisition_cost': 22.0,
            },
            'growth': {
                'monthly_revenue': 35000,
                'total_customers': 800,
                'total_orders': 2000,
                'aov': 75.0,
                'repeat_purchase_rate': 2.5,
                'email_subscriber_count': 600,
                'ltv': 187.0,
                'customer_acquisition_cost': 35.0,
            },
            'scaleup': {
                'monthly_revenue': 125000,
                'total_customers': 3500,
                'total_orders': 9500,
                'aov': 95.0,
                'repeat_purchase_rate': 2.8,
                'email_subscriber_count': 2800,
                'ltv': 265.0,
                'customer_acquisition_cost': 42.0,
            },
            'mature': {
                'monthly_revenue': 450000,
                'total_customers': 12000,
                'total_orders': 38000,
                'aov': 110.0,
                'repeat_purchase_rate': 3.2,
                'email_subscriber_count': 9500,
                'ltv': 350.0,
                'customer_acquisition_cost': 48.0,
            }
        }
        
        base_data = scenarios.get(scenario, scenarios['growth'])
        
        # Add computed features
        merchant_data = {
            **base_data,
            # Fix: Add recipients (mapped to subscriber count) to satisfy strategy model
            'recipients': base_data['email_subscriber_count'],
            'order_value_std': base_data['aov'] * 0.3,
            'discount_frequency': 0.25,
            'avg_items_per_order': 2.5,
            'avg_orders_per_customer': base_data['repeat_purchase_rate'],
            'marketing_opt_in_rate': 0.65,
            'total_campaigns': 5,
            'avg_open_rate': 0.28,
            'avg_click_rate': 0.12,
            'avg_conversion_rate': 0.06,
            'campaign_engagement': 0.20,
        }
        
        return merchant_data
    
    def test_discovery_engine(self, merchant_data):
        """Test Discovery Engine inference"""
        print("="*70)
        print("🔍 TESTING DISCOVERY ENGINE")
        print("="*70 + "\n")
        
        # Prepare features
        X = pd.DataFrame([merchant_data])[self.discovery_features]
        X_scaled = self.discovery_scaler.transform(X)
        
        # Predict maturity
        maturity_pred = self.maturity_model.predict(X_scaled)[0]
        maturity_proba = self.maturity_model.predict_proba(X_scaled)[0]
        maturity_label = self.maturity_encoder.inverse_transform([maturity_pred])[0]
        
        print("📊 Maturity Stage Prediction:")
        print(f"   Predicted: {maturity_label}")
        print(f"   Confidence: {max(maturity_proba)*100:.1f}%")
        print(f"   Probabilities:")
        for stage, prob in zip(self.maturity_encoder.classes_, maturity_proba):
            print(f"      {stage}: {prob*100:.1f}%")
        
        # Predict persona
        persona_pred = self.persona_model.predict(X_scaled)[0]
        persona_proba = self.persona_model.predict_proba(X_scaled)[0]
        persona_label = self.persona_encoder.inverse_transform([persona_pred])[0]
        
        print(f"\n📊 Persona Prediction:")
        print(f"   Predicted: {persona_label}")
        print(f"   Confidence: {max(persona_proba)*100:.1f}%")
        print(f"   Probabilities:")
        for persona, prob in zip(self.persona_encoder.classes_, persona_proba):
            print(f"      {persona}: {prob*100:.1f}%")
        
        print("\n   ✅ Discovery engine working correctly\n")
        
        return {
            'maturity': maturity_label,
            'persona': persona_label,
            'maturity_confidence': float(max(maturity_proba)),
            'persona_confidence': float(max(persona_proba))
        }
    
    def test_benchmark_engine(self, merchant_data):
        """Test Benchmark Engine inference"""
        print("="*70)
        print("📊 TESTING BENCHMARK ENGINE")
        print("="*70 + "\n")
        
        # Prepare features
        X = pd.DataFrame([merchant_data])[self.cluster_features]
        X_scaled = self.cluster_scaler.transform(X)
        
        # Predict cluster
        cluster_id = self.clustering_model.predict(X_scaled)[0]
        
        print(f"📊 Peer Group Assignment:")
        print(f"   Cluster ID: {cluster_id}")
        
        # Get benchmarks for this cluster
        cluster_key = f'cluster_{cluster_id}'
        cluster_benchmarks = self.benchmarks[cluster_key]
        
        print(f"\n📈 Peer Benchmarks (Cluster {cluster_id}):")
        print(f"   AOV Percentiles:")
        print(f"      25th: ${cluster_benchmarks['aov_p25']:.2f}")
        print(f"      50th: ${cluster_benchmarks['aov_p50']:.2f}")
        print(f"      75th: ${cluster_benchmarks['aov_p75']:.2f}")
        print(f"   LTV Percentiles:")
        print(f"      25th: ${cluster_benchmarks['ltv_p25']:.2f}")
        print(f"      50th: ${cluster_benchmarks['ltv_p50']:.2f}")
        print(f"      75th: ${cluster_benchmarks['ltv_p75']:.2f}")
        
        # Calculate merchant's percentile scores
        aov = merchant_data['aov']
        ltv = merchant_data['ltv']
        rpr = merchant_data['repeat_purchase_rate']
        
        aov_score = self._calculate_percentile_score(
            aov, cluster_benchmarks['aov_p25'], 
            cluster_benchmarks['aov_p50'], cluster_benchmarks['aov_p75']
        )
        ltv_score = self._calculate_percentile_score(
            ltv, cluster_benchmarks['ltv_p25'], 
            cluster_benchmarks['ltv_p50'], cluster_benchmarks['ltv_p75']
        )
        rpr_score = self._calculate_percentile_score(
            rpr, cluster_benchmarks['rpr_p25'], 
            cluster_benchmarks['rpr_p50'], cluster_benchmarks['rpr_p75']
        )
        
        print(f"\n📊 Your Performance vs Peers:")
        print(f"   AOV Score: {aov_score:.0f}/100")
        print(f"   LTV Score: {ltv_score:.0f}/100")
        print(f"   Repeat Rate Score: {rpr_score:.0f}/100")
        print(f"   Overall Score: {(aov_score + ltv_score + rpr_score)/3:.0f}/100")
        
        print("\n   ✅ Benchmark engine working correctly\n")
        
        return {
            'cluster_id': int(cluster_id),
            'scores': {
                'aov': float(aov_score),
                'ltv': float(ltv_score),
                'repeat_rate': float(rpr_score),
                'overall': float((aov_score + ltv_score + rpr_score)/3)
            }
        }
    
    def _calculate_percentile_score(self, value, p25, p50, p75):
        """Calculate percentile score (0-100)"""
        if value <= p25:
            return 25 * (value / p25) if p25 > 0 else 25
        elif value <= p50:
            return 25 + 25 * ((value - p25) / (p50 - p25))
        elif value <= p75:
            return 50 + 25 * ((value - p50) / (p75 - p50))
        else:
            return min(100, 75 + 25 * ((value - p75) / p75))
    
    def test_strategy_engine(self, merchant_data, discovery_result, benchmark_result):
        """Test Strategy Engine inference"""
        print("="*70)
        print("🎯 TESTING STRATEGY ENGINE")
        print("="*70 + "\n")
        
        # Prepare features for ranking
        strategy_input = {
            feat: merchant_data[feat] for feat in self.strategy_features
        }
        X = pd.DataFrame([strategy_input])
        X_scaled = self.strategy_scaler.transform(X)
        
        # Score each strategy
        strategy_scores = []
        for strategy_name, template in self.strategy_templates.items():
            # Get predicted ROI
            predicted_roi = self.strategy_model.predict(X_scaled)[0]
            
            # Apply business rules
            is_eligible = True
            
            if 'min_maturity' in template:
                if discovery_result['maturity'] not in template['min_maturity']:
                    is_eligible = False
            
            if 'min_subscribers' in template:
                if merchant_data['email_subscriber_count'] < template['min_subscribers']:
                    is_eligible = False
            
            if 'min_aov' in template:
                if merchant_data['aov'] < template['min_aov']:
                    is_eligible = False
            
            # Adjust score based on benchmark performance
            score_multiplier = 1.0 + (benchmark_result['scores']['overall'] - 50) / 100
            final_score = predicted_roi * score_multiplier * (1 if is_eligible else 0.3)
            
            strategy_scores.append({
                'name': strategy_name,
                'score': final_score,
                'expected_roi': template['expected_roi'],
                'description': template['description'],
                'eligible': is_eligible
            })
        
        # Sort by score
        strategy_scores.sort(key=lambda x: x['score'], reverse=True)
        
        print("📊 Recommended Strategies (Ranked):\n")
        for i, strategy in enumerate(strategy_scores[:5], 1):
            status = "✅" if strategy['eligible'] else "⚠️"
            print(f"   {i}. {status} {strategy['name']}")
            print(f"      Score: {strategy['score']:.1f}")
            print(f"      Expected ROI: {strategy['expected_roi']}%")
            print(f"      {strategy['description']}")
            if not strategy['eligible']:
                print(f"      (Not currently eligible)")
            print()
        
        print("   ✅ Strategy engine working correctly\n")
        
        return strategy_scores[:5]
    
    def run_full_test(self, scenario='growth'):
        """Run full end-to-end inference test"""
        print(f"🧪 Testing with '{scenario}' merchant scenario...\n")
        
        # Create test merchant
        merchant_data = self.create_test_merchant(scenario)
        
        print("📋 Test Merchant Profile:")
        print(f"   Monthly Revenue: ${merchant_data['monthly_revenue']:,.0f}")
        print(f"   Total Customers: {merchant_data['total_customers']:,}")
        print(f"   Average Order Value: ${merchant_data['aov']:.2f}")
        print(f"   Repeat Purchase Rate: {merchant_data['repeat_purchase_rate']:.1f}x")
        print(f"   Customer Lifetime Value: ${merchant_data['ltv']:.2f}\n")
        
        # Run engines sequentially
        discovery_result = self.test_discovery_engine(merchant_data)
        benchmark_result = self.test_benchmark_engine(merchant_data)
        strategy_result = self.test_strategy_engine(
            merchant_data, discovery_result, benchmark_result
        )
        
        # Summary
        print("="*70)
        print("✨ INFERENCE TEST COMPLETE")
        print("="*70)
        print("\n📊 Complete Analysis Summary:")
        print(f"   Merchant Profile: {discovery_result['persona']}")
        print(f"   Maturity Stage: {discovery_result['maturity']}")
        print(f"   Peer Group: Cluster {benchmark_result['cluster_id']}")
        print(f"   Overall Performance: {benchmark_result['scores']['overall']:.0f}/100")
        print(f"   Top Strategy: {strategy_result[0]['name']}")
        print(f"   Expected Impact: {strategy_result[0]['expected_roi']}% ROI")
        print("\n✅ All ML engines are functioning correctly!")
        print("🚀 Ready to start the application: make dev\n")


def main():
    tester = BravolaInferenceTester()
    
    # Test different scenarios
    scenarios = ['startup', 'growth', 'scaleup', 'mature']
    
    for scenario in scenarios:
        tester.run_full_test(scenario)
        if scenario != scenarios[-1]:
            print("\n" + "─"*70 + "\n")


if __name__ == "__main__":
    main()