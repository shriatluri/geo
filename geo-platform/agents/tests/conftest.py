"""
Pytest configuration and shared fixtures for agent testing.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any

from src.shared.models import WebsiteData, BusinessInfo, AgentType
from src.shared.llm_client import LLMClient


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.generate_text = AsyncMock(return_value='{"test": "response"}')
    return mock_client


@pytest.fixture
def sample_website_data():
    """Sample website data for testing."""
    return WebsiteData(
        url="https://example.com",
        html_content="""
        <html>
        <head>
            <title>Example Business - Professional Services</title>
            <meta name="description" content="We provide professional consulting services for businesses.">
            <meta property="og:title" content="Example Business">
            <meta property="og:description" content="Professional consulting services">
        </head>
        <body>
            <h1>Example Business</h1>
            <h2>Our Services</h2>
            <p>We provide comprehensive consulting services including strategic planning and market research.</p>
            <div>
                <p>Contact us at:</p>
                <p>Phone: (555) 123-4567</p>
                <p>Email: contact@example.com</p>
                <p>Address: 123 Main St, Anytown, ST 12345</p>
            </div>
        </body>
        </html>
        """,
        title="Example Business - Professional Services",
        meta_description="We provide professional consulting services for businesses.",
        extracted_text="Example Business Our Services We provide comprehensive consulting services including strategic planning and market research. Contact us at: Phone: (555) 123-4567 Email: contact@example.com Address: 123 Main St, Anytown, ST 12345",
        metadata={"business_type": "consulting", "cms": "unknown"}
    )


@pytest.fixture
def sample_business_info():
    """Sample business info for testing."""
    return BusinessInfo(
        name="Example Business",
        phone="(555) 123-4567",
        email="contact@example.com",
        address="123 Main St, Anytown, ST 12345",
        website="https://example.com",
        social_media={"linkedin": "https://linkedin.com/company/example"},
        confidence=0.9
    )


@pytest.fixture
def mock_soup(sample_website_data):
    """Mock BeautifulSoup object for testing."""
    from bs4 import BeautifulSoup
    return BeautifulSoup(sample_website_data.html_content, 'html.parser')


@pytest.fixture
def sample_schema_analysis():
    """Sample schema analysis data."""
    return {
        "existing_schemas": [
            {
                "type": "Organization",
                "data": {"@context": "https://schema.org", "@type": "Organization", "name": "Example Business"},
                "quality_score": 0.7
            }
        ],
        "missing_schemas": ["LocalBusiness", "FAQ"],
        "quality_issues": ["Missing description property"],
        "llm_recommendations": {
            "advanced_schema_opportunities": ["LocalBusiness", "FAQ"],
            "content_based_recommendations": ["Add opening hours", "Include price range"],
            "ai_optimization_suggestions": ["Improve content structure"],
            "missing_structured_data": ["ContactPoint", "PostalAddress"]
        }
    }


@pytest.fixture
def sample_meta_analysis():
    """Sample meta analysis data."""
    return {
        "title_analysis": {
            "present": True,
            "length": 42,
            "text": "Example Business - Professional Services",
            "issues": []
        },
        "meta_description_analysis": {
            "present": True,
            "length": 56,
            "content": "We provide professional consulting services for businesses.",
            "issues": []
        },
        "open_graph_analysis": {
            "present_tags": {
                "og:title": "Example Business",
                "og:description": "Professional consulting services"
            },
            "missing_tags": ["og:url", "og:type", "og:image"],
            "completeness_score": 0.4
        }
    }


@pytest.fixture
def sample_generated_schema():
    """Sample generated schema package."""
    return {
        "schema_type": "Organization",
        "json_ld": {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Example Business",
            "url": "https://example.com",
            "description": "We provide professional consulting services for businesses.",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "(555) 123-4567",
                "email": "contact@example.com",
                "contactType": "customer service"
            }
        },
        "implementation_notes": [
            "Place in <head> section of your website",
            "Ensure all contact information is accurate",
            "Update logo URL when available"
        ],
        "validation_requirements": ["name", "url"]
    }


@pytest.fixture
def sample_validation_result():
    """Sample validation result."""
    return {
        "is_valid": True,
        "errors": [],
        "warnings": ["Consider adding description property"],
        "quality_score": 0.8,
        "completeness_score": 0.9,
        "implementation_ready": True
    }


@pytest.fixture
def sample_agent_responses():
    """Sample agent responses for coordinator testing."""
    from src.shared.models import AgentResponse, AnalysisResult, PriorityLevel, ImpactLevel, EffortLevel
    from datetime import datetime

    aeo_response = AgentResponse(
        agent_name="AEO Agent",
        agent_type=AgentType.AEO,
        results=[
            AnalysisResult(
                id="missing_schema",
                type="schema_markup",
                title="Missing Schema Markup",
                description="Website is missing LocalBusiness schema",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Add LocalBusiness schema markup",
                implementation_steps=["Create JSON-LD schema", "Add to head section"],
                confidence=0.9
            )
        ],
        confidence=0.85,
        processing_time=2.5,
        timestamp=datetime.utcnow()
    )

    geo_response = AgentResponse(
        agent_name="GEO Agent",
        agent_type=AgentType.GEO,
        results=[
            AnalysisResult(
                id="contact_optimization",
                type="contact_validation",
                title="Contact Information Optimization",
                description="Contact information could be more accessible",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Make contact info more prominent",
                implementation_steps=["Add click-to-call links", "Improve contact page"],
                confidence=0.8
            )
        ],
        confidence=0.8,
        processing_time=1.8,
        timestamp=datetime.utcnow()
    )

    return [aeo_response, geo_response]