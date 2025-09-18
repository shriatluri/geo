"""
Tests for AEO Agent and its modular 3-phase components.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from bs4 import BeautifulSoup

from src.aeo_agent.agent import AEOAgent
from src.aeo_agent.analyzer import AEOAnalyzer
from src.aeo_agent.generator import AEOGenerator
from src.aeo_agent.validator import AEOValidator
from src.shared.models import PriorityLevel, ImpactLevel, EffortLevel


class TestAEOAnalyzer:
    """Test cases for AEOAnalyzer."""

    @pytest.fixture
    def analyzer(self, mock_llm_client):
        """Create AEOAnalyzer instance."""
        return AEOAnalyzer(mock_llm_client)

    @pytest.mark.asyncio
    async def test_analyze_schema_markup(self, analyzer, mock_soup, sample_website_data):
        """Test schema markup analysis."""
        # Add JSON-LD script to soup
        mock_soup.find_all = MagicMock(return_value=[
            MagicMock(string='{"@context": "https://schema.org", "@type": "Organization", "name": "Test"}')
        ])

        analyzer._determine_required_schemas = MagicMock(return_value=["Organization", "LocalBusiness"])
        analyzer._llm_analyze_schema_opportunities = AsyncMock(return_value={"test": "response"})

        result = await analyzer.analyze_schema_markup(mock_soup, sample_website_data)

        assert "existing_schemas" in result
        assert "missing_schemas" in result
        assert len(result["missing_schemas"]) > 0
        assert result["missing_schemas"] == ["LocalBusiness"]  # Organization exists, LocalBusiness missing

    def test_analyze_content_structure(self, analyzer, mock_soup):
        """Test content structure analysis."""
        # Mock headings
        mock_soup.find_all.side_effect = [
            [MagicMock(name='h1'), MagicMock(name='h2')],  # For headings
            [MagicMock(), MagicMock()],  # For sections/articles
            MagicMock(),  # For nav
            [MagicMock(), MagicMock(), MagicMock()]  # For h1,h2,h3
        ]

        result = analyzer.analyze_content_structure(mock_soup)

        assert "heading_structure" in result
        assert "content_organization" in result
        assert "readability_factors" in result

    def test_analyze_meta_information(self, analyzer, mock_soup, sample_website_data):
        """Test meta information analysis."""
        # Mock title tag
        title_mock = MagicMock()
        title_mock.get_text.return_value = "Test Title"
        mock_soup.find.return_value = title_mock

        result = analyzer.analyze_meta_information(mock_soup, sample_website_data)

        assert "title_analysis" in result
        assert "meta_description_analysis" in result
        assert "open_graph_analysis" in result

    @pytest.mark.asyncio
    async def test_analyze_ai_response_optimization(self, analyzer, sample_website_data, mock_soup):
        """Test AI response optimization analysis."""
        analyzer._identify_qa_patterns = MagicMock(return_value={"faq_elements_found": 2})
        analyzer._assess_content_clarity = MagicMock(return_value=0.7)
        analyzer._identify_structured_data_gaps = MagicMock(return_value=["ContactPoint"])
        analyzer._llm_analyze_content_optimization = AsyncMock(return_value={"test": "optimization"})

        result = await analyzer.analyze_ai_response_optimization(sample_website_data, mock_soup)

        assert "question_answer_patterns" in result
        assert "content_clarity_score" in result
        assert "structured_data_gaps" in result
        assert "llm_optimization_suggestions" in result

    def test_assess_schema_quality(self, analyzer):
        """Test schema quality assessment."""
        good_schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Test",
            "url": "https://test.com",
            "description": "Test description"
        }

        score = analyzer._assess_schema_quality(good_schema)
        assert score > 0.5  # Should be decent quality

        # Test poor schema
        poor_schema = {"name": "Test"}
        score = analyzer._assess_schema_quality(poor_schema)
        assert score < 0.5  # Should be poor quality

    def test_analyze_heading_structure(self, analyzer):
        """Test heading structure analysis."""
        # Mock heading elements
        h1_mock = MagicMock()
        h1_mock.name = 'h1'
        h2_mock = MagicMock()
        h2_mock.name = 'h2'

        soup_mock = MagicMock()
        soup_mock.find_all.return_value = [h1_mock, h2_mock]

        result = analyzer._analyze_heading_structure(soup_mock)

        assert "total_headings" in result
        assert "h1_count" in result
        assert "hierarchy_issues" in result


class TestAEOGenerator:
    """Test cases for AEOGenerator."""

    @pytest.fixture
    def generator(self, mock_llm_client):
        """Create AEOGenerator instance."""
        return AEOGenerator(mock_llm_client)

    @pytest.mark.asyncio
    async def test_generate_schema_markup(self, generator, sample_website_data, sample_business_info):
        """Test schema markup generation."""
        generator._llm_enhance_schema = AsyncMock(return_value={"enhanced": "schema"})

        result = await generator.generate_schema_markup("Organization", sample_website_data, sample_business_info)

        assert result["schema_type"] == "Organization"
        assert "json_ld" in result
        assert "implementation_notes" in result
        assert "validation_requirements" in result

    def test_generate_meta_tags(self, generator, sample_website_data, sample_meta_analysis):
        """Test meta tags generation."""
        result = generator.generate_meta_tags(sample_website_data, sample_meta_analysis)

        assert "title_tag" in result
        assert "meta_description" in result
        assert "open_graph_tags" in result
        assert "twitter_cards" in result
        assert "additional_meta" in result

    @pytest.mark.asyncio
    async def test_generate_ai_optimization_content(self, generator, sample_website_data, sample_meta_analysis):
        """Test AI optimization content generation."""
        generator._generate_qa_content = AsyncMock(return_value={"qa_sections": []})

        result = await generator.generate_ai_optimization_content(sample_website_data, sample_meta_analysis)

        assert "structured_qa_content" in result
        assert "content_restructuring" in result
        assert "semantic_improvements" in result
        assert "accessibility_enhancements" in result

    def test_generate_content_structure_improvements(self, generator, sample_meta_analysis):
        """Test content structure improvement generation."""
        # Add heading issues to analysis
        analysis_with_issues = sample_meta_analysis.copy()
        analysis_with_issues["heading_structure"] = {
            "hierarchy_issues": ["Missing H1 tag", "Multiple H1 tags found"]
        }

        result = generator.generate_content_structure_improvements(analysis_with_issues)

        assert "heading_structure_fixes" in result
        assert "content_organization" in result
        assert "readability_improvements" in result

    def test_generate_organization_schema(self, generator, sample_website_data, sample_business_info):
        """Test Organization schema generation."""
        schema = generator._generate_organization_schema(sample_website_data, sample_business_info)

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Organization"
        assert schema["name"] == sample_business_info.name
        assert schema["url"] == str(sample_website_data.url)

    def test_generate_local_business_schema(self, generator, sample_website_data, sample_business_info):
        """Test LocalBusiness schema generation."""
        schema = generator._generate_local_business_schema(sample_website_data, sample_business_info)

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "LocalBusiness"
        assert schema["name"] == sample_business_info.name
        assert schema["telephone"] == sample_business_info.phone

    @pytest.mark.asyncio
    async def test_llm_generate_faq_content(self, generator):
        """Test LLM-powered FAQ content generation."""
        generator.llm_client.generate_text = AsyncMock(return_value=json.dumps({
            "questions": [
                {
                    "@type": "Question",
                    "name": "What services do you offer?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "We offer consulting services."
                    }
                }
            ]
        }))

        result = await generator._llm_generate_faq_content("Test content")

        assert "questions" in result
        assert len(result["questions"]) == 1
        assert result["questions"][0]["@type"] == "Question"

    def test_extract_business_name(self, generator, sample_website_data, sample_business_info):
        """Test business name extraction."""
        # Test with business info
        name = generator._extract_business_name(sample_website_data, sample_business_info)
        assert name == sample_business_info.name

        # Test without business info (from title)
        name = generator._extract_business_name(sample_website_data)
        assert "Example Business" in name


class TestAEOValidator:
    """Test cases for AEOValidator."""

    @pytest.fixture
    def validator(self, mock_llm_client):
        """Create AEOValidator instance."""
        return AEOValidator(mock_llm_client)

    @pytest.mark.asyncio
    async def test_validate_schema_markup(self, validator, sample_generated_schema):
        """Test schema markup validation."""
        validator._llm_validate_schema = AsyncMock(return_value={
            "has_issues": False,
            "quality_rating": "good",
            "suggestions": []
        })

        result = await validator.validate_schema_markup(sample_generated_schema)

        assert result["is_valid"] is True
        assert "quality_score" in result
        assert "completeness_score" in result
        assert "implementation_ready" in result

    def test_validate_meta_tags(self, validator):
        """Test meta tags validation."""
        meta_package = {
            "title_tag": "Good Title Tag Length",
            "meta_description": "This is a good meta description that is within the recommended length range for optimal SEO performance.",
            "open_graph_tags": {
                "og:title": "Title",
                "og:description": "Description",
                "og:url": "https://example.com",
                "og:type": "website"
            }
        }

        result = validator.validate_meta_tags(meta_package)

        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_ai_optimization(self, validator):
        """Test AI optimization validation."""
        optimization_package = {
            "structured_qa_content": {
                "qa_sections": [
                    {
                        "question": "What services do you offer?",
                        "answer": "We provide comprehensive consulting services.",
                        "placement_suggestion": "homepage"
                    }
                ]
            },
            "content_restructuring": ["Add clear subheadings", "Use bullet points"],
            "semantic_improvements": ["Use descriptive heading tags"],
            "accessibility_enhancements": ["Add alt text to images"]
        }

        result = validator.validate_ai_optimization(optimization_package)

        assert "quality_score" in result
        assert "actionability_score" in result
        assert result["quality_score"] > 0

    def test_validate_content_structure_improvements(self, validator):
        """Test content structure improvement validation."""
        improvements = {
            "heading_structure_fixes": ["Add a single H1 tag"],
            "content_organization": ["Group related content"],
            "readability_improvements": ["Reduce sentence length"]
        }

        result = validator.validate_content_structure_improvements(improvements)

        assert "implementation_feasibility" in result
        assert "impact_score" in result
        assert result["implementation_feasibility"] > 0

    @pytest.mark.asyncio
    async def test_validate_implementation_readiness(self, validator):
        """Test overall implementation readiness validation."""
        all_content = {
            "schema_validations": {
                "Organization": {"is_valid": True, "quality_score": 0.8}
            },
            "meta_validation": {"is_valid": True},
            "ai_optimization_validation": {"quality_score": 0.7, "actionability_score": 0.8},
            "structure_validation": {"implementation_feasibility": 0.9, "impact_score": 0.8}
        }

        result = await validator.validate_implementation_readiness(all_content)

        assert "ready_for_implementation" in result
        assert "readiness_score" in result
        assert "implementation_priority" in result
        assert result["readiness_score"] > 0.5

    def test_validate_schema_structure(self, validator):
        """Test schema structure validation."""
        good_schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Test"
        }

        result = validator._validate_schema_structure(good_schema, "Organization")
        assert result["structure_valid"] is True
        assert len(result["errors"]) == 0

        # Test bad schema
        bad_schema = {"name": "Test"}  # Missing @context and @type
        result = validator._validate_schema_structure(bad_schema, "Organization")
        assert result["structure_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_title_tag(self, validator):
        """Test title tag validation."""
        # Good title
        result = validator._validate_title_tag("This is a good title that meets length requirements")
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

        # Too short title
        result = validator._validate_title_tag("Short")
        assert len(result["warnings"]) > 0

        # Empty title
        result = validator._validate_title_tag("")
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0


class TestAEOAgent:
    """Test cases for AEOAgent integration."""

    @pytest.fixture
    def aeo_agent(self, mock_llm_client):
        """Create AEOAgent instance."""
        return AEOAgent(mock_llm_client)

    @pytest.mark.asyncio
    async def test_analyze_3_phase_pattern(self, aeo_agent, sample_website_data):
        """Test the complete 3-phase analysis pattern."""
        # Mock the modular components
        aeo_agent.analyzer.analyze_schema_markup = AsyncMock(return_value={"missing_schemas": ["Organization"]})
        aeo_agent.analyzer.analyze_content_structure = MagicMock(return_value={"heading_structure": {}})
        aeo_agent.analyzer.analyze_meta_information = MagicMock(return_value={"title_analysis": {}})
        aeo_agent.analyzer.analyze_ai_response_optimization = AsyncMock(return_value={"content_clarity_score": 0.8})

        aeo_agent.generator.generate_schema_markup = AsyncMock(return_value={"schema_type": "Organization"})
        aeo_agent.generator.generate_meta_tags = MagicMock(return_value={"title_tag": "Test"})
        aeo_agent.generator.generate_ai_optimization_content = AsyncMock(return_value={"structured_qa_content": {}})
        aeo_agent.generator.generate_content_structure_improvements = MagicMock(return_value={"heading_structure_fixes": []})

        aeo_agent.validator.validate_schema_markup = AsyncMock(return_value={"is_valid": True})
        aeo_agent.validator.validate_meta_tags = MagicMock(return_value={"is_valid": True})
        aeo_agent.validator.validate_ai_optimization = MagicMock(return_value={"quality_score": 0.8})
        aeo_agent.validator.validate_content_structure_improvements = MagicMock(return_value={"implementation_feasibility": 0.9})
        aeo_agent.validator.validate_implementation_readiness = AsyncMock(return_value={"ready_for_implementation": True, "readiness_score": 0.85})

        result = await aeo_agent.analyze(sample_website_data)

        # Verify response structure
        assert result.agent_name == "AEO Agent"
        assert result.confidence > 0
        assert len(result.results) > 0

        # Verify metadata contains all 3 phases
        assert "analysis_phase" in result.metadata
        assert "generation_phase" in result.metadata
        assert "validation_phase" in result.metadata
        assert result.metadata["modular_pattern_version"] == "3-phase"

    @pytest.mark.asyncio
    async def test_analyze_with_client_input(self, aeo_agent, sample_website_data, sample_business_info):
        """Test analysis with client input data."""
        # Mock the modular components
        aeo_agent.analyzer.analyze_schema_markup = AsyncMock(return_value={"missing_schemas": []})
        aeo_agent.analyzer.analyze_content_structure = MagicMock(return_value={})
        aeo_agent.analyzer.analyze_meta_information = MagicMock(return_value={})
        aeo_agent.analyzer.analyze_ai_response_optimization = AsyncMock(return_value={})

        aeo_agent.generator.generate_meta_tags = MagicMock(return_value={})
        aeo_agent.generator.generate_ai_optimization_content = AsyncMock(return_value={})
        aeo_agent.generator.generate_content_structure_improvements = MagicMock(return_value={})

        aeo_agent.validator.validate_meta_tags = MagicMock(return_value={"is_valid": True})
        aeo_agent.validator.validate_ai_optimization = MagicMock(return_value={"quality_score": 0.8})
        aeo_agent.validator.validate_content_structure_improvements = MagicMock(return_value={"implementation_feasibility": 0.9})
        aeo_agent.validator.validate_implementation_readiness = AsyncMock(return_value={"ready_for_implementation": True, "readiness_score": 0.9})

        client_input = {"business_info": sample_business_info}
        result = await aeo_agent.analyze(sample_website_data, client_input)

        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_analyze_error_handling(self, aeo_agent, sample_website_data):
        """Test error handling in analysis."""
        # Mock an error in the analysis phase
        aeo_agent.analyzer.analyze_schema_markup = AsyncMock(side_effect=Exception("Analysis error"))

        result = await aeo_agent.analyze(sample_website_data)

        assert result.confidence == 0.0
        assert len(result.results) == 1  # Should contain error result
        assert "error" in result.results[0].title.lower()

    def test_convert_to_analysis_results(self, aeo_agent):
        """Test conversion of 3-phase results to AnalysisResult format."""
        # Create mock analysis data
        schema_analysis = {"missing_schemas": ["Organization"]}
        content_analysis = {"heading_structure": {"hierarchy_issues": ["Missing H1"]}}
        meta_analysis = {}
        ai_analysis = {}
        schema_packages = {"Organization": {"schema_type": "Organization"}}
        meta_package = {}
        ai_content = {}
        structure_improvements = {"heading_structure_fixes": ["Add H1"]}
        schema_validations = {"Organization": {"is_valid": True}}
        meta_validation = {"is_valid": False}
        ai_validation = {"quality_score": 0.5}
        structure_validation = {"implementation_feasibility": 0.8}
        readiness = {"ready_for_implementation": True, "readiness_score": 0.8}

        results = aeo_agent._convert_to_analysis_results(
            schema_analysis, content_analysis, meta_analysis, ai_analysis,
            schema_packages, meta_package, ai_content, structure_improvements,
            schema_validations, meta_validation, ai_validation, structure_validation,
            readiness
        )

        assert len(results) > 0
        assert all(hasattr(result, 'priority') for result in results)
        assert all(hasattr(result, 'impact') for result in results)
        assert all(hasattr(result, 'effort') for result in results)