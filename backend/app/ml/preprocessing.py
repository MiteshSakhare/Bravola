"""
Data preprocessing utilities
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class DataPreprocessor:
    """
    Utilities for data preprocessing
    """
    
    @staticmethod
    def handle_missing_values(
        data: pd.DataFrame,
        strategy: str = 'mean'
    ) -> pd.DataFrame:
        """
        Handle missing values in dataframe
        
        Args:
            data: Input dataframe
            strategy: Strategy for handling missing values (mean, median, zero, drop)
        """
        if strategy == 'mean':
            return data.fillna(data.mean())
        elif strategy == 'median':
            return data.fillna(data.median())
        elif strategy == 'zero':
            return data.fillna(0)
        elif strategy == 'drop':
            return data.dropna()
        else:
            return data.fillna(data.mean())
    
    @staticmethod
    def normalize_features(
        data: np.ndarray,
        method: str = 'standard'
    ) -> tuple:
        """
        Normalize feature values
        
        Args:
            data: Input array
            method: Normalization method (standard, minmax)
        
        Returns:
            Tuple of (normalized_data, scaler)
        """
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            scaler = StandardScaler()
        
        normalized = scaler.fit_transform(data)
        return normalized, scaler
    
    @staticmethod
    def encode_categorical(
        data: pd.Series,
        method: str = 'onehot'
    ) -> pd.DataFrame:
        """
        Encode categorical variables
        
        Args:
            data: Input series with categorical data
            method: Encoding method (onehot, label)
        """
        if method == 'onehot':
            return pd.get_dummies(data, prefix=data.name)
        elif method == 'label':
            return data.astype('category').cat.codes
        else:
            return pd.get_dummies(data, prefix=data.name)
    
    @staticmethod
    def remove_outliers(
        data: pd.DataFrame,
        columns: List[str],
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers from data
        
        Args:
            data: Input dataframe
            columns: Columns to check for outliers
            method: Method for outlier detection (iqr, zscore)
            threshold: Threshold value
        """
        df = data.copy()
        
        for col in columns:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df = df[z_scores < threshold]
        
        return df
