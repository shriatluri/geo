"""
Pydantic data models for GEO platform agents.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Agent type enumeration."""
    AEO = "aeo"
    GEO = "geo"
    GEO_PLUS = "geo_plus"
    COORDINATOR = "coordinator"


class PriorityLevel(str, Enum):
    """Priority level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactLevel(str, Enum):
    """Impact level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EffortLevel(str, Enum):
    """Effort level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SchemaType(str, Enum):
    """Schema.org type enumeration."""
    ORGANIZATION = "Organization"
    PRODUCT = "Product"
    FAQ = "FAQ"
    REVIEW = "Review"
    EVENT = "Event"
    ARTICLE = "Article"
    BREADCRUMB = "BreadcrumbList"
    LOCAL_BUSINESS = "LocalBusiness"
    RESTAURANT = "Restaurant"
    HOTEL = "Hotel"


class WebsiteData(BaseModel):
    """Website data structure."""
    url: HttpUrl
    html_content: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    status_code: int = 200
    load_time: Optional[float] = None
    screenshot_path: Optional[str] = None
    extracted_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SchemaMarkup(BaseModel):
    """Schema markup data."""
    type: SchemaType
    content: Dict[str, Any]
    format: str = "json-ld"  # json-ld, microdata, rdfa
    location: str = "head"  # head, body, inline
    confidence: float = Field(ge=0, le=1)


class BusinessInfo(BaseModel):
    """Business information data."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[Dict[str, str]] = None
    social_media: Dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0, le=1)


class APIEndpoint(BaseModel):
    """API endpoint data."""
    url: str
    method: str = "GET"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    response_format: str = "json"
    authentication_required: bool = False
    rate_limit: Optional[int] = None
    documentation_url: Optional[str] = None


class FormData(BaseModel):
    """Form data structure."""
    action_url: str
    method: str = "POST"
    fields: List[Dict[str, Any]] = Field(default_factory=list)
    csrf_token: Optional[str] = None
    captcha_required: bool = False
    file_upload: bool = False


class AnalysisResult(BaseModel):
    """Individual analysis result."""
    id: str
    type: str
    title: str
    description: str
    priority: PriorityLevel
    impact: ImpactLevel
    effort: EffortLevel
    recommendation: str
    implementation_steps: List[str] = Field(default_factory=list)
    code_examples: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Agent response structure."""
    agent_name: str
    agent_type: AgentType
    results: List[AnalysisResult]
    confidence: float = Field(ge=0, le=1)
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConflictResolution(BaseModel):
    """Conflict resolution data."""
    conflict_id: str
    conflicting_agents: List[str]
    conflict_description: str
    resolution_strategy: str
    final_recommendation: str
    confidence: float = Field(ge=0, le=1)


class PriorityMatrix(BaseModel):
    """Priority matrix for recommendations."""
    high_impact_low_effort: List[AnalysisResult] = Field(default_factory=list)
    high_impact_high_effort: List[AnalysisResult] = Field(default_factory=list)
    low_impact_low_effort: List[AnalysisResult] = Field(default_factory=list)
    low_impact_high_effort: List[AnalysisResult] = Field(default_factory=list)


class ImplementationPlan(BaseModel):
    """Implementation plan structure."""
    phases: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_timeline: str
    resource_requirements: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)


class CoordinatorResponse(BaseModel):
    """Coordinator agent response."""
    unified_results: List[AnalysisResult]
    conflict_resolutions: List[ConflictResolution]
    priority_matrix: PriorityMatrix
    implementation_plan: ImplementationPlan
    overall_confidence: float = Field(ge=0, le=1)
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
