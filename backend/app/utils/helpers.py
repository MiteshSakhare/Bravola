"""
Helper utility functions
"""

import uuid
from typing import Any


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix
    
    Args:
        prefix: Prefix for the ID
    """
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"{prefix}_{unique_id}" if prefix else unique_id


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Numeric amount
        currency: Currency code
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'C$',
        'AUD': 'A$'
    }
    
    symbol = symbols.get(currency, '$')
    return f"{symbol}{amount:,.2f}"


def calculate_percentage(part: float, total: float) -> float:
    """
    Calculate percentage
    
    Args:
        part: Part value
        total: Total value
    """
    if total == 0:
        return 0.0
    
    return round((part / total) * 100, 2)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length
    
    Args:
        text: Input text
        max_length: Maximum length
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."
