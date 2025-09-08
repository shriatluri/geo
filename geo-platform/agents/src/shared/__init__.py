"""
Shared components for GEO platform agents.
"""

from .base_agent import BaseAgent
from .models import (
    AnalysisResult,
    AgentResponse,
    WebsiteData,
    SchemaMarkup,
    BusinessInfo,
    APIEndpoint,
    FormData,
    ConflictResolution,
    PriorityMatrix
)
from .llm_client import LLMClient
from .utils import (
    extract_json_ld,
    validate_schema,
    normalize_phone,
    normalize_email,
    extract_domain,
    calculate_impact_score
)

__all__ = [
    "BaseAgent",
    "AnalysisResult",
    "AgentResponse", 
    "WebsiteData",
    "SchemaMarkup",
    "BusinessInfo",
    "APIEndpoint",
    "FormData",
    "ConflictResolution",
    "PriorityMatrix",
    "LLMClient",
    "extract_json_ld",
    "validate_schema",
    "normalize_phone",
    "normalize_email",
    "extract_domain",
    "calculate_impact_score"
]
