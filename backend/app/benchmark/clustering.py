"""
Clustering logic for peer group assignment
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.preprocessing import StandardScaler


class PeerGroupClustering:
    """
    Utilities for peer group clustering and analysis
    """
    
    @staticmethod
    def calculate_cluster_profiles(
        cluster_data: Dict[int, List[Dict[str, float]]]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Calculate statistical profiles for each cluster
        """
        profiles = {}
        
        for cluster_id, merchants in cluster_data.items():
            if not merchants:
                continue
            
            # Convert to numpy array
            data = np.array([
                [m['monthly_revenue'], m['aov'], m['ltv'], m['repeat_purchase_rate']]
                for m in merchants
            ])
            
            profiles[cluster_id] = {
                'size': len(merchants),
                'revenue_profile': {
                    'mean': float(np.mean(data[:, 0])),
                    'median': float(np.median(data[:, 0])),
                    'std': float(np.std(data[:, 0])),
                    'min': float(np.min(data[:, 0])),
                    'max': float(np.max(data[:, 0]))
                },
                'aov_profile': {
                    'mean': float(np.mean(data[:, 1])),
                    'median': float(np.median(data[:, 1])),
                    'std': float(np.std(data[:, 1]))
                },
                'ltv_profile': {
                    'mean': float(np.mean(data[:, 2])),
                    'median': float(np.median(data[:, 2])),
                    'std': float(np.std(data[:, 2]))
                },
                'characteristics': PeerGroupClustering._generate_characteristics(
                    cluster_id, data
                )
            }
        
        return profiles
    
    @staticmethod
    def _generate_characteristics(
        cluster_id: int,
        data: np.ndarray
    ) -> List[str]:
        """Generate human-readable characteristics for cluster"""
        
        characteristics = []
        
        # Revenue level
        avg_revenue = np.mean(data[:, 0])
        if avg_revenue < 10000:
            characteristics.append("Early-stage businesses")
        elif avg_revenue < 50000:
            characteristics.append("Growing businesses")
        elif avg_revenue < 200000:
            characteristics.append("Scaling businesses")
        else:
            characteristics.append("Established businesses")
        
        # AOV level
        avg_aov = np.mean(data[:, 1])
        if avg_aov < 50:
            characteristics.append("Low ticket items")
        elif avg_aov < 100:
            characteristics.append("Medium ticket items")
        else:
            characteristics.append("High ticket items")
        
        # Repeat rate
        avg_repeat = np.mean(data[:, 3])
        if avg_repeat > 3.0:
            characteristics.append("Strong repeat business")
        elif avg_repeat > 2.0:
            characteristics.append("Moderate repeat business")
        else:
            characteristics.append("Primarily new customers")
        
        return characteristics
    
    @staticmethod
    def calculate_distance_to_cluster_center(
        merchant_features: np.ndarray,
        cluster_center: np.ndarray,
        scaler: StandardScaler = None
    ) -> float:
        """
        Calculate distance from merchant to cluster center
        """
        if scaler:
            merchant_scaled = scaler.transform(merchant_features.reshape(1, -1))
            center_scaled = scaler.transform(cluster_center.reshape(1, -1))
        else:
            merchant_scaled = merchant_features
            center_scaled = cluster_center
        
        distance = np.linalg.norm(merchant_scaled - center_scaled)
        return float(distance)
    
    @staticmethod
    def find_similar_merchants(
        target_features: np.ndarray,
        all_features: List[np.ndarray],
        merchant_ids: List[str],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar merchants based on features
        """
        distances = []
        
        for mid, features in zip(merchant_ids, all_features):
            distance = np.linalg.norm(target_features - features)
            distances.append((mid, float(distance)))
        
        # Sort by distance and return top k
        distances.sort(key=lambda x: x[1])
        return distances[:top_k]
