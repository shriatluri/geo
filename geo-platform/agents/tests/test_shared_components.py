"""
Tests for shared components (base agent, models, utilities).
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from src.shared.base_agent import BaseAgent
from src.shared.models import (
    WebsiteData, AgentResponse, AnalysisResult, BusinessInfo,
    PriorityLevel, ImpactLevel, EffortLevel, AgentType
)
from src.shared.llm_client import LLMClient
from src.shared.utils import calculate_confidence_score, normalize_url
from src.shared.client_input_processor import ClientInputProcessor


class TestBaseAgent:
    """Test cases for BaseAgent abstract class."""

    class MockAgent(BaseAgent):
        """Mock concrete implementation of BaseAgent for testing."""

        async def analyze(self, website_data: WebsiteData) -> AgentResponse:
            return self._create_response(
                results=[],
                confidence=0.8,
                processing_time=1.0
            )

    @pytest.fixture
    def mock_agent(self, mock_llm_client):
        """Create mock agent instance."""
        return self.MockAgent("Test Agent", mock_llm_client)

    def test_agent_initialization(self, mock_agent):
        """Test agent initialization."""
        assert mock_agent.name == "Test Agent"
        assert mock_agent.llm_client is not None
        assert mock_agent.logger is not None

    @pytest.mark.asyncio
    async def test_analyze_method(self, mock_agent, sample_website_data):
        """Test abstract analyze method implementation."""
        result = await mock_agent.analyze(sample_website_data)

        assert isinstance(result, AgentResponse)
        assert result.agent_name == "Test Agent"
        assert result.confidence == 0.8
        assert result.processing_time == 1.0

    def test_create_response(self, mock_agent):
        """Test response creation utility."""
        results = [
            AnalysisResult(
                id="test1", type="test", title="Test Result", description="Test",
                priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                recommendation="Test recommendation", confidence=0.9
            )
        ]

        response = mock_agent._create_response(results, 0.85, 2.5)

        assert response.agent_name == "Test Agent"
        assert response.confidence == 0.85
        assert response.processing_time == 2.5
        assert len(response.results) == 1
        assert response.timestamp is not None

    def test_create_error_result(self, mock_agent):
        """Test error result creation."""
        error_result = mock_agent._create_error_result("Test error message")

        assert error_result.type == "error"
        assert "error" in error_result.title.lower()
        assert "Test error message" in error_result.description
        assert error_result.priority == PriorityLevel.HIGH

    def test_calculate_overall_confidence(self, mock_agent):
        """Test confidence calculation."""
        results = [
            AnalysisResult(
                id="test1", type="test", title="Test 1", description="Test",
                priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                recommendation="Test", confidence=0.9
            ),
            AnalysisResult(
                id="test2", type="test", title="Test 2", description="Test",
                priority=PriorityLevel.MEDIUM, impact=ImpactLevel.MEDIUM, effort=EffortLevel.MEDIUM,
                recommendation="Test", confidence=0.7
            )
        ]

        confidence = mock_agent._calculate_overall_confidence(results)
        expected = (0.9 + 0.7) / 2
        assert abs(confidence - expected) < 0.01

    def test_logging_methods(self, mock_agent):
        """Test logging utility methods."""
        # These should not raise exceptions
        mock_agent._log_analysis_start("https://example.com")
        mock_agent._log_analysis_complete("https://example.com", 5, 0.8)
        mock_agent._log_error(Exception("Test error"), "test operation")


class TestModels:
    """Test cases for Pydantic models."""

    def test_website_data_model(self):
        """Test WebsiteData model validation."""
        data = WebsiteData(
            url="https://example.com",
            html_content="<html><body>Test</body></html>",
            title="Test Site",
            meta_description="Test description",
            extracted_text="Test content",
            metadata={"test": "value"}
        )

        assert str(data.url) == "https://example.com"
        assert data.title == "Test Site"
        assert data.metadata["test"] == "value"

    def test_business_info_model(self):
        """Test BusinessInfo model validation."""
        business = BusinessInfo(
            name="Test Business",
            phone="+1-555-123-4567",
            email="test@example.com",
            address="123 Main St",
            website="https://example.com",
            confidence=0.95
        )

        assert business.name == "Test Business"
        assert business.confidence == 0.95

    def test_analysis_result_model(self):
        """Test AnalysisResult model validation."""
        result = AnalysisResult(
            id="test_result",
            type="schema_markup",
            title="Test Schema Issue",
            description="Missing schema markup",
            priority=PriorityLevel.HIGH,
            impact=ImpactLevel.HIGH,
            effort=EffortLevel.MEDIUM,
            recommendation="Add schema markup",
            implementation_steps=["Step 1", "Step 2"],
            confidence=0.9,
            metadata={"source": "analyzer"}
        )

        assert result.id == "test_result"
        assert result.priority == PriorityLevel.HIGH
        assert len(result.implementation_steps) == 2

    def test_agent_response_model(self):
        """Test AgentResponse model validation."""
        result = AnalysisResult(
            id="test", type="test", title="Test", description="Test",
            priority=PriorityLevel.MEDIUM, impact=ImpactLevel.MEDIUM, effort=EffortLevel.LOW,
            recommendation="Test", confidence=0.8
        )

        response = AgentResponse(
            agent_name="Test Agent",
            agent_type=AgentType.AEO,
            results=[result],
            confidence=0.85,
            processing_time=2.0,
            timestamp=datetime.utcnow(),
            metadata={"test": "value"}
        )

        assert response.agent_name == "Test Agent"
        assert response.agent_type == AgentType.AEO
        assert len(response.results) == 1
        assert response.metadata["test"] == "value"

    def test_enum_values(self):
        """Test enumeration values."""
        assert PriorityLevel.HIGH == "high"
        assert ImpactLevel.CRITICAL == "critical"
        assert EffortLevel.VERY_HIGH == "very_high"
        assert AgentType.COORDINATOR == "coordinator"


class TestLLMClient:
    """Test cases for LLM client."""

    @pytest.fixture
    def llm_client(self):
        """Create LLM client instance."""
        return LLMClient()

    def test_llm_client_initialization(self, llm_client):
        """Test LLM client initialization."""
        assert llm_client is not None
        assert hasattr(llm_client, 'generate_text')

    @pytest.mark.asyncio
    async def test_generate_text_mock(self, mock_llm_client):
        """Test mocked text generation."""
        result = await mock_llm_client.generate_text("Test prompt")
        assert result == '{"test": "response"}'
        mock_llm_client.generate_text.assert_called_once_with("Test prompt")


class TestUtils:
    """Test cases for utility functions."""

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        scores = [0.8, 0.9, 0.7]
        result = calculate_confidence_score(scores)
        expected = sum(scores) / len(scores)
        assert abs(result - expected) < 0.01

    def test_calculate_confidence_score_empty(self):
        """Test confidence calculation with empty list."""
        result = calculate_confidence_score([])
        assert result == 0.0

    def test_normalize_url(self):
        """Test URL normalization."""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("http://example.com") == "https://example.com"
        assert normalize_url("https://example.com") == "https://example.com"
        assert normalize_url("https://example.com/") == "https://example.com"

    def test_normalize_url_invalid(self):
        """Test URL normalization with invalid URLs."""
        assert normalize_url("") == ""
        assert normalize_url("not-a-url") == "https://not-a-url"


class TestClientInputProcessor:
    """Test cases for client input processing."""

    @pytest.fixture
    def processor(self):
        """Create client input processor instance."""
        return ClientInputProcessor()

    def test_process_business_info(self, processor):
        """Test business info processing."""
        raw_input = {
            "business_name": "Test Business",
            "phone": "555-123-4567",
            "email": "test@example.com",
            "address": "123 Main St",
            "website": "example.com"
        }

        business_info = processor.process_business_info(raw_input)

        assert business_info.name == "Test Business"
        assert business_info.phone == "555-123-4567"
        assert business_info.website == "https://example.com"  # Should be normalized

    def test_process_business_info_partial(self, processor):
        """Test processing with partial business info."""
        raw_input = {
            "business_name": "Test Business",
            "phone": "555-123-4567"
            # Missing other fields
        }

        business_info = processor.process_business_info(raw_input)

        assert business_info.name == "Test Business"
        assert business_info.phone == "555-123-4567"
        assert business_info.email is None
        assert business_info.address is None

    def test_validate_input(self, processor):
        """Test input validation."""
        valid_input = {
            "url": "https://example.com",
            "business_info": {
                "business_name": "Test",
                "phone": "555-1234"
            }
        }

        is_valid, errors = processor.validate_input(valid_input)
        assert is_valid
        assert len(errors) == 0

    def test_validate_input_invalid(self, processor):
        """Test validation with invalid input."""
        invalid_input = {
            "business_info": {
                "business_name": "",  # Empty name
                "phone": "invalid"    # Invalid phone
            }
        }

        is_valid, errors = processor.validate_input(invalid_input)
        assert not is_valid
        assert len(errors) > 0

    def test_extract_keywords(self, processor):
        """Test keyword extraction."""
        text = "professional consulting services business strategy marketing"
        keywords = processor.extract_keywords(text)

        assert "consulting" in keywords
        assert "business" in keywords
        assert len(keywords) > 0

    def test_clean_text(self, processor):
        """Test text cleaning."""
        dirty_text = "  This   has\n\nextra   whitespace  \t"
        clean_text = processor.clean_text(dirty_text)

        assert clean_text == "This has extra whitespace"
        assert "\n" not in clean_text
        assert "  " not in clean_text