"""
Common utilities for GEO platform agents.
"""

import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


def extract_json_ld(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract JSON-LD structured data from HTML content.
    
    Args:
        html_content: HTML content to parse
        
    Returns:
        List of JSON-LD objects found
    """
    json_ld_objects = []
    
    # Simple regex to find JSON-LD scripts
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        try:
            json_obj = json.loads(match.strip())
            json_ld_objects.append(json_obj)
        except json.JSONDecodeError:
            continue
    
    return json_ld_objects


def validate_schema(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate schema markup structure.
    
    Args:
        schema_data: Schema data to validate
        
    Returns:
        Validation results
    """
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check for required @context
    if "@context" not in schema_data:
        validation_result["errors"].append("Missing @context property")
        validation_result["is_valid"] = False
    
    # Check for required @type
    if "@type" not in schema_data:
        validation_result["errors"].append("Missing @type property")
        validation_result["is_valid"] = False
    
    # Check for minimal content
    if len(schema_data.keys()) < 3:
        validation_result["warnings"].append("Schema has minimal properties")
    
    return validation_result


def normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize phone number to standard format.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Normalized phone number or None if invalid
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle US phone numbers
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone  # Return original if can't normalize


def normalize_email(email: str) -> Optional[str]:
    """
    Normalize and validate email address.
    
    Args:
        email: Raw email string
        
    Returns:
        Normalized email or None if invalid
    """
    if not email:
        return None
    
    # Basic email validation
    email = email.strip().lower()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(email_pattern, email):
        return email
    
    return None


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain name or None if invalid
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain if domain else None
    except Exception:
        return None


def calculate_impact_score(priority: str, impact: str, effort: str) -> float:
    """
    Calculate impact score based on priority, impact, and effort.
    
    Args:
        priority: Priority level (high/medium/low)
        impact: Impact level (high/medium/low)
        effort: Effort level (high/medium/low)
        
    Returns:
        Impact score (0.0 to 1.0)
    """
    priority_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
    impact_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
    effort_weights = {"low": 1.0, "medium": 0.6, "high": 0.3}  # Lower effort = higher score
    
    priority_score = priority_weights.get(priority.lower(), 0.5)
    impact_score = impact_weights.get(impact.lower(), 0.5)
    effort_score = effort_weights.get(effort.lower(), 0.5)
    
    # Weighted average
    return (priority_score * 0.4 + impact_score * 0.4 + effort_score * 0.2)
