"""
Model registry for tracking ML model versions
"""

from typing import Dict, Any, Optional
import joblib
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger


class ModelRegistry:
    """
    Registry for managing ML model versions
    """
    
    def __init__(self):
        self.artifacts_path = settings.ML_ARTIFACTS_PATH
    
    def get_model_metadata(self, engine: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific engine's models
        
        Args:
            engine: Engine name (discovery, benchmark, strategy)
        """
        try:
            metadata_path = self.artifacts_path / 'training_metadata.joblib'
            
            if not metadata_path.exists():
                logger.warning(f"Model metadata not found at {metadata_path}")
                return None
            
            metadata = joblib.load(metadata_path)
            
            return {
                'engine': engine,
                'version': settings.MODEL_VERSION,
                'trained_at': metadata.get('trained_at'),
                'models': metadata.get('models', {}).get(engine, {}),
                'training_data': {
                    'merchants': metadata.get('num_merchants'),
                    'orders': metadata.get('num_orders'),
                    'campaigns': metadata.get('num_campaigns')
                }
            }
        
        except Exception as e:
            logger.error(f"Error retrieving model metadata: {str(e)}")
            return None
    
    def register_model_version(
        self,
        engine: str,
        version: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Register a new model version
        
        Args:
            engine: Engine name
            version: Model version
            metadata: Model metadata
        """
        try:
            registry_path = self.artifacts_path / 'model_registry.joblib'
            
            # Load existing registry or create new
            if registry_path.exists():
                registry = joblib.load(registry_path)
            else:
                registry = {}
            
            # Add new version
            if engine not in registry:
                registry[engine] = {}
            
            registry[engine][version] = {
                'metadata': metadata,
                'registered_at': datetime.utcnow().isoformat()
            }
            
            # Save updated registry
            joblib.dump(registry, registry_path)
            
            logger.info(f"Registered {engine} model version {version}")
            return True
        
        except Exception as e:
            logger.error(f"Error registering model version: {str(e)}")
            return False
    
    def get_active_version(self, engine: str) -> str:
        """
        Get the active version for an engine
        
        Args:
            engine: Engine name
        """
        return settings.MODEL_VERSION
    
    def list_available_versions(self, engine: str) -> list:
        """
        List all available versions for an engine
        
        Args:
            engine: Engine name
        """
        try:
            registry_path = self.artifacts_path / 'model_registry.joblib'
            
            if not registry_path.exists():
                return [settings.MODEL_VERSION]
            
            registry = joblib.load(registry_path)
            
            if engine in registry:
                return list(registry[engine].keys())
            
            return [settings.MODEL_VERSION]
        
        except Exception as e:
            logger.error(f"Error listing versions: {str(e)}")
            return [settings.MODEL_VERSION]
