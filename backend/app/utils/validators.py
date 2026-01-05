"""
Validation utility functions
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_domain(domain: str) -> bool:
    """
    Validate domain name format
    
    Args:
        domain: Domain name to validate
    """
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone)
    
    # Check if remaining characters are digits and length is reasonable
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))
