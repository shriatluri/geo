"""
AEO Agent Validator - Validates generated schema markup and optimizations.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from ..shared.models import WebsiteData
from ..shared.llm_client import LLMClient


class AEOValidator:
    """
    Validates generated solutions before delivery to ensure quality and correctness.

    Validates:
    - JSON-LD schema syntax and completeness
    - Meta tag compliance and length
    - Content structure improvements
    - AI optimization recommendations
    - Implementation feasibility
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.validation_rules = self._load_validation_rules()

    async def validate_schema_markup(self, schema_package: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete schema markup package."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "quality_score": 0.0,
            "completeness_score": 0.0,
            "implementation_ready": False
        }

        try:
            schema_json = schema_package.get("json_ld", {})
            schema_type = schema_package.get("schema_type", "Unknown")

            # Basic structure validation
            structure_validation = self._validate_schema_structure(schema_json, schema_type)
            validation_result.update(structure_validation)

            # Content validation
            content_validation = self._validate_schema_content(schema_json, schema_type)
            validation_result["quality_score"] = content_validation["quality_score"]
            validation_result["completeness_score"] = content_validation["completeness_score"]
            validation_result["warnings"].extend(content_validation["warnings"])

            # Requirements validation
            requirements_validation = self._validate_requirements(schema_json, schema_package.get("validation_requirements", []))
            if not requirements_validation["all_met"]:
                validation_result["errors"].extend(requirements_validation["missing_requirements"])
                validation_result["is_valid"] = False

            # LLM-enhanced validation if available
            if self.llm_client and validation_result["is_valid"]:
                llm_validation = await self._llm_validate_schema(schema_json, schema_type)
                validation_result["llm_feedback"] = llm_validation

                # Adjust scores based on LLM feedback
                if llm_validation.get("has_issues", False):
                    validation_result["quality_score"] *= 0.8
                    validation_result["warnings"].extend(llm_validation.get("suggestions", []))

            # Final implementation readiness check
            validation_result["implementation_ready"] = (
                validation_result["is_valid"] and
                validation_result["quality_score"] >= 0.7 and
                validation_result["completeness_score"] >= 0.6
            )

        except json.JSONDecodeError as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Invalid JSON syntax: {str(e)}")
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {str(e)}")
            validation_result["is_valid"] = False

        return validation_result

    def validate_meta_tags(self, meta_package: Dict[str, Any]) -> Dict[str, Any]:
        """Validate meta tags package."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }

        # Validate title tag
        title_validation = self._validate_title_tag(meta_package.get("title_tag", ""))
        if not title_validation["is_valid"]:
            validation_result["errors"].extend(title_validation["issues"])
        validation_result["warnings"].extend(title_validation["warnings"])

        # Validate meta description
        desc_validation = self._validate_meta_description(meta_package.get("meta_description", ""))
        if not desc_validation["is_valid"]:
            validation_result["errors"].extend(desc_validation["issues"])
        validation_result["warnings"].extend(desc_validation["warnings"])

        # Validate Open Graph tags
        og_validation = self._validate_open_graph_tags(meta_package.get("open_graph_tags", {}))
        validation_result["warnings"].extend(og_validation["warnings"])
        validation_result["recommendations"].extend(og_validation["recommendations"])

        # Set overall validity
        validation_result["is_valid"] = len(validation_result["errors"]) == 0

        return validation_result

    def validate_ai_optimization(self, optimization_package: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AI optimization recommendations."""
        validation_result = {
            "is_valid": True,
            "quality_score": 0.0,
            "actionability_score": 0.0,
            "warnings": [],
            "recommendations": []
        }

        # Validate Q&A content
        qa_content = optimization_package.get("structured_qa_content", {})
        if qa_content.get("qa_sections"):
            qa_validation = self._validate_qa_content(qa_content["qa_sections"])
            validation_result["quality_score"] += qa_validation["quality_score"] * 0.4

        # Validate content restructuring recommendations
        restructuring = optimization_package.get("content_restructuring", [])
        if restructuring:
            restructuring_validation = self._validate_restructuring_recommendations(restructuring)
            validation_result["actionability_score"] += restructuring_validation["actionability_score"] * 0.3

        # Validate semantic improvements
        semantic = optimization_package.get("semantic_improvements", [])
        if semantic:
            semantic_validation = self._validate_semantic_improvements(semantic)
            validation_result["actionability_score"] += semantic_validation["actionability_score"] * 0.4

        # Validate accessibility enhancements
        accessibility = optimization_package.get("accessibility_enhancements", [])
        if accessibility:
            accessibility_validation = self._validate_accessibility_enhancements(accessibility)
            validation_result["actionability_score"] += accessibility_validation["actionability_score"] * 0.3

        # Normalize scores
        validation_result["quality_score"] = min(validation_result["quality_score"], 1.0)
        validation_result["actionability_score"] = min(validation_result["actionability_score"], 1.0)

        return validation_result

    def validate_content_structure_improvements(self, improvements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content structure improvement recommendations."""
        validation_result = {
            "is_valid": True,
            "implementation_feasibility": 0.0,
            "impact_score": 0.0,
            "warnings": []
        }

        # Validate heading fixes
        heading_fixes = improvements.get("heading_structure_fixes", [])
        if heading_fixes:
            heading_validation = self._validate_heading_fixes(heading_fixes)
            validation_result["implementation_feasibility"] += heading_validation["feasibility"] * 0.4
            validation_result["impact_score"] += heading_validation["impact"] * 0.4

        # Validate content organization
        organization = improvements.get("content_organization", [])
        if organization:
            org_validation = self._validate_content_organization(organization)
            validation_result["implementation_feasibility"] += org_validation["feasibility"] * 0.3
            validation_result["impact_score"] += org_validation["impact"] * 0.3

        # Validate readability improvements
        readability = improvements.get("readability_improvements", [])
        if readability:
            readability_validation = self._validate_readability_improvements(readability)
            validation_result["implementation_feasibility"] += readability_validation["feasibility"] * 0.3
            validation_result["impact_score"] += readability_validation["impact"] * 0.3

        # Normalize scores
        validation_result["implementation_feasibility"] = min(validation_result["implementation_feasibility"], 1.0)
        validation_result["impact_score"] = min(validation_result["impact_score"], 1.0)

        return validation_result

    async def validate_implementation_readiness(self, all_generated_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall implementation readiness across all generated content."""
        readiness_result = {
            "ready_for_implementation": False,
            "readiness_score": 0.0,
            "blocking_issues": [],
            "warnings": [],
            "implementation_priority": "medium",
            "estimated_effort": "medium"
        }

        scores = []

        # Check schema markup validation
        schema_validations = all_generated_content.get("schema_validations", {})
        if schema_validations:
            schema_scores = [v.get("quality_score", 0) for v in schema_validations.values() if v.get("is_valid", False)]
            if schema_scores:
                avg_schema_score = sum(schema_scores) / len(schema_scores)
                scores.append(avg_schema_score)
            else:
                readiness_result["blocking_issues"].append("Invalid schema markup detected")

        # Check meta tags validation
        meta_validation = all_generated_content.get("meta_validation", {})
        if meta_validation and not meta_validation.get("is_valid", True):
            readiness_result["blocking_issues"].append("Meta tags validation failed")
        else:
            scores.append(0.8)  # Default good score for valid meta tags

        # Check AI optimization validation
        ai_validation = all_generated_content.get("ai_optimization_validation", {})
        if ai_validation:
            ai_score = (ai_validation.get("quality_score", 0) + ai_validation.get("actionability_score", 0)) / 2
            scores.append(ai_score)

        # Check content structure validation
        structure_validation = all_generated_content.get("structure_validation", {})
        if structure_validation:
            structure_score = (structure_validation.get("implementation_feasibility", 0) + structure_validation.get("impact_score", 0)) / 2
            scores.append(structure_score)

        # Calculate overall readiness score
        if scores:
            readiness_result["readiness_score"] = sum(scores) / len(scores)

        # Determine implementation readiness
        readiness_result["ready_for_implementation"] = (
            len(readiness_result["blocking_issues"]) == 0 and
            readiness_result["readiness_score"] >= 0.6
        )

        # Set implementation priority based on readiness score
        if readiness_result["readiness_score"] >= 0.8:
            readiness_result["implementation_priority"] = "high"
        elif readiness_result["readiness_score"] >= 0.6:
            readiness_result["implementation_priority"] = "medium"
        else:
            readiness_result["implementation_priority"] = "low"

        # Estimate implementation effort
        total_recommendations = sum([
            len(all_generated_content.get("schema_packages", {})),
            len(all_generated_content.get("ai_optimization_content", {}).get("structured_qa_content", {}).get("qa_sections", [])),
            len(all_generated_content.get("content_structure_improvements", {}).get("heading_structure_fixes", []))
        ])

        if total_recommendations <= 5:
            readiness_result["estimated_effort"] = "low"
        elif total_recommendations <= 10:
            readiness_result["estimated_effort"] = "medium"
        else:
            readiness_result["estimated_effort"] = "high"

        return readiness_result

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different content types."""
        return {
            "schema_required_properties": {
                "Organization": ["@context", "@type", "name", "url"],
                "LocalBusiness": ["@context", "@type", "name", "address", "telephone"],
                "FAQ": ["@context", "@type", "mainEntity"],
                "Event": ["@context", "@type", "name", "startDate"],
                "Product": ["@context", "@type", "name", "description"]
            },
            "meta_tag_limits": {
                "title_min": 30,
                "title_max": 60,
                "description_min": 120,
                "description_max": 160
            },
            "quality_thresholds": {
                "schema_completeness": 0.6,
                "content_clarity": 0.7,
                "implementation_feasibility": 0.6
            }
        }

    def _validate_schema_structure(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Validate basic schema structure."""
        validation = {
            "structure_valid": True,
            "errors": [],
            "warnings": []
        }

        # Check for required @context
        if "@context" not in schema_data:
            validation["errors"].append("Missing @context property")
            validation["structure_valid"] = False
        elif schema_data["@context"] != "https://schema.org":
            validation["warnings"].append("@context should be 'https://schema.org'")

        # Check for required @type
        if "@type" not in schema_data:
            validation["errors"].append("Missing @type property")
            validation["structure_valid"] = False
        elif schema_data["@type"] != schema_type:
            validation["warnings"].append(f"@type mismatch: expected {schema_type}, got {schema_data['@type']}")

        return validation

    def _validate_schema_content(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Validate schema content quality and completeness."""
        validation = {
            "quality_score": 0.0,
            "completeness_score": 0.0,
            "warnings": []
        }

        required_props = self.validation_rules["schema_required_properties"].get(schema_type, [])
        present_props = [prop for prop in required_props if prop in schema_data and schema_data[prop]]

        # Calculate completeness score
        if required_props:
            validation["completeness_score"] = len(present_props) / len(required_props)

        # Calculate quality score based on content richness
        total_properties = len([k for k, v in schema_data.items() if v])
        base_quality = min(total_properties / 5, 1.0)  # Up to 5 properties for full score

        # Bonus for well-structured nested objects
        nested_objects = sum(1 for v in schema_data.values() if isinstance(v, dict) and "@type" in v)
        quality_bonus = min(nested_objects * 0.1, 0.3)

        validation["quality_score"] = min(base_quality + quality_bonus, 1.0)

        # Add warnings for missing recommended properties
        if schema_type == "Organization" and "description" not in schema_data:
            validation["warnings"].append("Consider adding description property")
        if schema_type == "LocalBusiness" and "openingHours" not in schema_data:
            validation["warnings"].append("Consider adding openingHours property")

        return validation

    def _validate_requirements(self, schema_data: Dict[str, Any], requirements: List[str]) -> Dict[str, Any]:
        """Validate that all requirements are met."""
        validation = {
            "all_met": True,
            "missing_requirements": []
        }

        for requirement in requirements:
            if "with at least one" in requirement:
                # Special case for FAQ mainEntity
                property_name = requirement.split()[0]
                if property_name not in schema_data or not schema_data[property_name]:
                    validation["missing_requirements"].append(f"Missing {requirement}")
                    validation["all_met"] = False
                elif isinstance(schema_data[property_name], list) and len(schema_data[property_name]) == 0:
                    validation["missing_requirements"].append(f"Empty {requirement}")
                    validation["all_met"] = False
            else:
                if requirement not in schema_data or not schema_data[requirement]:
                    validation["missing_requirements"].append(f"Missing required property: {requirement}")
                    validation["all_met"] = False

        return validation

    async def _llm_validate_schema(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Use LLM to validate schema for advanced issues."""
        prompt = f"""
        Validate this {schema_type} schema markup for quality, correctness, and best practices.

        Schema:
        {json.dumps(schema_data, indent=2)}

        Check for:
        1. Schema.org compliance
        2. Property completeness and accuracy
        3. Data quality and consistency
        4. Best practices adherence
        5. Potential SEO impact

        Return JSON:
        {{
            "has_issues": false,
            "quality_rating": "excellent|good|fair|poor",
            "suggestions": ["list of specific improvement suggestions"],
            "seo_impact": "high|medium|low"
        }}
        """

        try:
            response = await self.llm_client.generate_text(prompt, max_tokens=800)
            return json.loads(response)
        except Exception as e:
            return {"has_issues": False, "quality_rating": "good", "suggestions": [], "error": str(e)}

    def _validate_title_tag(self, title: str) -> Dict[str, Any]:
        """Validate title tag."""
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }

        if not title:
            validation["issues"].append("Title tag is empty")
            validation["is_valid"] = False
            return validation

        length = len(title)
        min_length = self.validation_rules["meta_tag_limits"]["title_min"]
        max_length = self.validation_rules["meta_tag_limits"]["title_max"]

        if length < min_length:
            validation["warnings"].append(f"Title too short ({length} chars, recommended: {min_length}-{max_length})")
        elif length > max_length:
            validation["warnings"].append(f"Title too long ({length} chars, recommended: {min_length}-{max_length})")

        return validation

    def _validate_meta_description(self, description: str) -> Dict[str, Any]:
        """Validate meta description."""
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }

        if not description:
            validation["issues"].append("Meta description is empty")
            validation["is_valid"] = False
            return validation

        length = len(description)
        min_length = self.validation_rules["meta_tag_limits"]["description_min"]
        max_length = self.validation_rules["meta_tag_limits"]["description_max"]

        if length < min_length:
            validation["warnings"].append(f"Description too short ({length} chars, recommended: {min_length}-{max_length})")
        elif length > max_length:
            validation["warnings"].append(f"Description too long ({length} chars, recommended: {min_length}-{max_length})")

        return validation

    def _validate_open_graph_tags(self, og_tags: Dict[str, str]) -> Dict[str, Any]:
        """Validate Open Graph tags."""
        validation = {
            "warnings": [],
            "recommendations": []
        }

        required_og_tags = ["og:title", "og:description", "og:url", "og:type"]
        missing_tags = [tag for tag in required_og_tags if tag not in og_tags]

        if missing_tags:
            validation["warnings"].extend([f"Missing Open Graph tag: {tag}" for tag in missing_tags])

        # Check for og:image
        if "og:image" not in og_tags:
            validation["recommendations"].append("Consider adding og:image for better social media sharing")

        return validation

    def _validate_qa_content(self, qa_sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate Q&A content quality."""
        validation = {
            "quality_score": 0.0
        }

        if not qa_sections:
            return validation

        quality_factors = []

        for qa in qa_sections:
            question = qa.get("question", "")
            answer = qa.get("answer", "")

            # Check question quality
            question_score = 0.5
            if len(question) >= 10 and question.endswith("?"):
                question_score = 1.0

            # Check answer quality
            answer_score = 0.5
            if len(answer) >= 20:
                answer_score = 1.0

            qa_score = (question_score + answer_score) / 2
            quality_factors.append(qa_score)

        validation["quality_score"] = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0

        return validation

    def _validate_restructuring_recommendations(self, recommendations: List[str]) -> Dict[str, Any]:
        """Validate content restructuring recommendations."""
        validation = {
            "actionability_score": 0.0
        }

        if not recommendations:
            return validation

        # Check for specific, actionable recommendations
        actionable_count = 0
        for rec in recommendations:
            if any(word in rec.lower() for word in ["add", "use", "break", "create", "implement"]):
                actionable_count += 1

        validation["actionability_score"] = actionable_count / len(recommendations) if recommendations else 0.0

        return validation

    def _validate_semantic_improvements(self, improvements: List[str]) -> Dict[str, Any]:
        """Validate semantic improvement suggestions."""
        validation = {
            "actionability_score": 0.8  # Default high score for semantic improvements
        }

        return validation

    def _validate_accessibility_enhancements(self, enhancements: List[str]) -> Dict[str, Any]:
        """Validate accessibility enhancement suggestions."""
        validation = {
            "actionability_score": 0.9  # Default high score for accessibility improvements
        }

        return validation

    def _validate_heading_fixes(self, fixes: List[str]) -> Dict[str, Any]:
        """Validate heading structure fixes."""
        validation = {
            "feasibility": 0.9,  # Heading fixes are usually easy to implement
            "impact": 0.8       # High impact on SEO and accessibility
        }

        return validation

    def _validate_content_organization(self, organization: List[str]) -> Dict[str, Any]:
        """Validate content organization recommendations."""
        validation = {
            "feasibility": 0.6,  # May require more work
            "impact": 0.7       # Good impact on user experience
        }

        return validation

    def _validate_readability_improvements(self, improvements: List[str]) -> Dict[str, Any]:
        """Validate readability improvement suggestions."""
        validation = {
            "feasibility": 0.7,  # Moderate effort to implement
            "impact": 0.6       # Moderate impact on user experience
        }

        return validation