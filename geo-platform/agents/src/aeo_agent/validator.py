"""
AEO Agent Validator - Validates generated schema markup and optimizations.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from ..shared.models import WebsiteData


class AEOValidator:
    """
    Validates generated solutions before delivery to ensure quality and correctness.
    
    Validates:
    - JSON-LD schema syntax and completeness
    - Meta tag compliance and length
    - Accessibility standards
    - Implementation feasibility
    """
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
    
    def validate_schema_markup(self, schema_json: str, schema_type: str) -> Dict[str, Any]:
        """Validate JSON-LD schema markup."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "quality_score": 0.0,
            "completeness_score": 0.0
        }
        
        try:
            # Parse JSON
            schema_data = json.loads(schema_json)
            
            # Basic structure validation
            structure_validation = self._validate_schema_structure(schema_data, schema_type)
            validation_result.update(structure_validation)
            
            # Content validation
            content_validation = self._validate_schema_content(schema_data, schema_type)
            validation_result["quality_score"] = content_validation["quality_score"]
            validation_result["completeness_score"] = content_validation["completeness_score"]
            validation_result["warnings"].extend(content_validation["warnings"])
            
            # Schema-specific validation
            specific_validation = self._validate_schema_specific(schema_data, schema_type)
            validation_result["warnings"].extend(specific_validation["warnings"])
            if specific_validation["errors"]:
                validation_result["errors"].extend(specific_validation["errors"])
                validation_result["is_valid"] = False
            
        except json.JSONDecodeError as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Invalid JSON syntax: {str(e)}")
        
        return validation_result
    
    def validate_meta_tags(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Validate generated meta tags."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "quality_scores": {}
        }
        
        # Validate title
        if "title" in meta_tags:
            title_validation = self._validate_title_tag(meta_tags["title"])
            validation_result["quality_scores"]["title"] = title_validation["score"]
            validation_result["warnings"].extend(title_validation["warnings"])
            if title_validation["errors"]:
                validation_result["errors"].extend(title_validation["errors"])
        else:
            validation_result["errors"].append("Missing title tag")
            validation_result["is_valid"] = False
        
        # Validate meta description
        if "description" in meta_tags:
            desc_validation = self._validate_meta_description(meta_tags["description"])
            validation_result["quality_scores"]["description"] = desc_validation["score"]
            validation_result["warnings"].extend(desc_validation["warnings"])
        else:
            validation_result["warnings"].append("Missing meta description")
        
        # Validate Open Graph tags
        og_validation = self._validate_open_graph_tags(meta_tags)
        validation_result["quality_scores"]["open_graph"] = og_validation["score"]
        validation_result["warnings"].extend(og_validation["warnings"])
        
        return validation_result
    
    def validate_html_improvements(self, improvements: Dict[str, str]) -> Dict[str, Any]:
        """Validate HTML improvement suggestions."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "implementation_feasibility": {}
        }
        
        for improvement_type, suggestion in improvements.items():
            feasibility = self._assess_implementation_feasibility(improvement_type, suggestion)
            validation_result["implementation_feasibility"][improvement_type] = feasibility
            
            if feasibility["complexity"] == "high":
                validation_result["warnings"].append(
                    f"{improvement_type}: High complexity implementation"
                )
        
        return validation_result
    
    def validate_implementation_readiness(self, generated_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall implementation readiness."""
        validation_result = {
            "ready_for_implementation": True,
            "readiness_score": 0.0,
            "blocking_issues": [],
            "recommendations": []
        }
        
        readiness_factors = []
        
        # Check schema validation
        if "schema_markup" in generated_content:
            schema_valid = generated_content["schema_markup"].get("is_valid", False)
            readiness_factors.append(1.0 if schema_valid else 0.0)
            if not schema_valid:
                validation_result["blocking_issues"].append("Schema markup validation failed")
        
        # Check meta tags validation
        if "meta_tags" in generated_content:
            meta_valid = generated_content["meta_tags"].get("is_valid", False)
            readiness_factors.append(1.0 if meta_valid else 0.0)
            if not meta_valid:
                validation_result["blocking_issues"].append("Meta tags validation failed")
        
        # Calculate readiness score
        if readiness_factors:
            validation_result["readiness_score"] = sum(readiness_factors) / len(readiness_factors)
        
        # Determine if ready for implementation
        validation_result["ready_for_implementation"] = (
            validation_result["readiness_score"] >= 0.8 and 
            not validation_result["blocking_issues"]
        )
        
        # Generate recommendations
        validation_result["recommendations"] = self._generate_implementation_recommendations(
            validation_result["readiness_score"], 
            validation_result["blocking_issues"]
        )
        
        return validation_result
    
    def validate_squarespace_compatibility(self, generated_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compatibility with Squarespace platform."""
        compatibility_result = {
            "is_compatible": True,
            "platform_issues": [],
            "implementation_notes": []
        }
        
        # Check schema markup compatibility
        if "schema_markup" in generated_content:
            schema_compatibility = self._check_squarespace_schema_compatibility(
                generated_content["schema_markup"]
            )
            compatibility_result["implementation_notes"].extend(
                schema_compatibility["notes"]
            )
        
        # Check meta tags compatibility
        if "meta_tags" in generated_content:
            meta_compatibility = self._check_squarespace_meta_compatibility(
                generated_content["meta_tags"]
            )
            compatibility_result["implementation_notes"].extend(
                meta_compatibility["notes"]
            )
        
        return compatibility_result
    
    def _validate_schema_structure(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Validate basic schema structure."""
        result = {"errors": [], "warnings": []}
        
        # Check for required @context
        if "@context" not in schema_data:
            result["errors"].append("Missing @context property")
        elif schema_data["@context"] != "https://schema.org":
            result["warnings"].append("@context should be 'https://schema.org'")
        
        # Check for required @type
        if "@type" not in schema_data:
            result["errors"].append("Missing @type property")
        elif schema_data["@type"] != schema_type:
            result["warnings"].append(f"@type mismatch: expected {schema_type}, got {schema_data['@type']}")
        
        return result
    
    def _validate_schema_content(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Validate schema content quality and completeness."""
        result = {
            "quality_score": 0.0,
            "completeness_score": 0.0,
            "warnings": []
        }
        
        # Get required and recommended properties for schema type
        schema_rules = self.validation_rules.get(schema_type, {})
        required_props = schema_rules.get("required", [])
        recommended_props = schema_rules.get("recommended", [])
        
        # Check required properties
        missing_required = [prop for prop in required_props if prop not in schema_data]
        if missing_required:
            result["warnings"].append(f"Missing required properties: {', '.join(missing_required)}")
        
        # Calculate completeness score
        total_required = len(required_props) if required_props else 1
        present_required = len([prop for prop in required_props if prop in schema_data])
        result["completeness_score"] = present_required / total_required
        
        # Calculate quality score
        quality_factors = []
        
        # Check property values quality
        for prop, value in schema_data.items():
            if prop.startswith('@'):
                continue
            
            if isinstance(value, str):
                if len(value.strip()) > 0:
                    quality_factors.append(1.0)
                else:
                    quality_factors.append(0.0)
                    result["warnings"].append(f"Empty value for property: {prop}")
            else:
                quality_factors.append(0.8)  # Non-string values get partial credit
        
        result["quality_score"] = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
        
        return result
    
    def _validate_schema_specific(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Perform schema-type specific validation."""
        result = {"errors": [], "warnings": []}
        
        if schema_type == "Organization":
            result = self._validate_organization_schema(schema_data)
        elif schema_type == "LocalBusiness":
            result = self._validate_local_business_schema(schema_data)
        elif schema_type == "FAQ":
            result = self._validate_faq_schema(schema_data)
        
        return result
    
    def _validate_organization_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Organization schema specifics."""
        result = {"errors": [], "warnings": []}
        
        # Validate URL format
        if "url" in schema_data:
            if not self._is_valid_url(schema_data["url"]):
                result["errors"].append("Invalid URL format")
        
        # Validate contact points
        if "contactPoint" in schema_data:
            contact_validation = self._validate_contact_points(schema_data["contactPoint"])
            result["warnings"].extend(contact_validation["warnings"])
        
        return result
    
    def _validate_local_business_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LocalBusiness schema specifics."""
        result = {"errors": [], "warnings": []}
        
        # Address is required for LocalBusiness
        if "address" not in schema_data:
            result["errors"].append("LocalBusiness schema requires address property")
        elif isinstance(schema_data["address"], dict):
            address_validation = self._validate_address_schema(schema_data["address"])
            result["warnings"].extend(address_validation["warnings"])
        
        return result
    
    def _validate_faq_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate FAQ schema specifics."""
        result = {"errors": [], "warnings": []}
        
        if "mainEntity" not in schema_data:
            result["errors"].append("FAQ schema requires mainEntity property")
        elif isinstance(schema_data["mainEntity"], list):
            for i, entity in enumerate(schema_data["mainEntity"]):
                if not isinstance(entity, dict) or "@type" not in entity:
                    result["warnings"].append(f"FAQ entity {i} missing @type")
                if "name" not in entity:
                    result["warnings"].append(f"FAQ entity {i} missing question name")
                if "acceptedAnswer" not in entity:
                    result["warnings"].append(f"FAQ entity {i} missing accepted answer")
        
        return result
    
    def _validate_title_tag(self, title: str) -> Dict[str, Any]:
        """Validate title tag."""
        result = {"score": 0.0, "errors": [], "warnings": []}
        
        length = len(title)
        
        # Length validation
        if length == 0:
            result["errors"].append("Title cannot be empty")
            return result
        elif length < 30:
            result["warnings"].append("Title is shorter than recommended (30+ chars)")
            result["score"] = 0.6
        elif length > 60:
            result["warnings"].append("Title is longer than recommended (60 chars max)")
            result["score"] = 0.7
        else:
            result["score"] = 1.0
        
        # Content validation
        if not any(char.isalpha() for char in title):
            result["errors"].append("Title should contain alphabetic characters")
        
        return result
    
    def _validate_meta_description(self, description: str) -> Dict[str, Any]:
        """Validate meta description."""
        result = {"score": 0.0, "errors": [], "warnings": []}
        
        length = len(description)
        
        # Length validation
        if length == 0:
            result["warnings"].append("Meta description is empty")
            result["score"] = 0.0
        elif length < 120:
            result["warnings"].append("Meta description is shorter than recommended (120+ chars)")
            result["score"] = 0.7
        elif length > 160:
            result["warnings"].append("Meta description is longer than recommended (160 chars max)")
            result["score"] = 0.8
        else:
            result["score"] = 1.0
        
        return result
    
    def _validate_open_graph_tags(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Validate Open Graph tags."""
        result = {"score": 0.0, "warnings": []}
        
        og_tags = [key for key in meta_tags.keys() if key.startswith('og:')]
        required_og = ['og:title', 'og:description', 'og:url', 'og:type']
        
        present_required = len([tag for tag in required_og if tag in og_tags])
        result["score"] = present_required / len(required_og)
        
        missing_og = [tag for tag in required_og if tag not in og_tags]
        if missing_og:
            result["warnings"].append(f"Missing Open Graph tags: {', '.join(missing_og)}")
        
        return result
    
    def _assess_implementation_feasibility(self, improvement_type: str, suggestion: str) -> Dict[str, Any]:
        """Assess implementation feasibility."""
        feasibility_map = {
            "headings": {"complexity": "low", "time_estimate": "30 minutes"},
            "accessibility": {"complexity": "medium", "time_estimate": "1-2 hours"},
            "schema_markup": {"complexity": "medium", "time_estimate": "1 hour"},
            "meta_tags": {"complexity": "low", "time_estimate": "15 minutes"}
        }
        
        return feasibility_map.get(improvement_type, {"complexity": "medium", "time_estimate": "1 hour"})
    
    def _generate_implementation_recommendations(self, readiness_score: float, blocking_issues: List[str]) -> List[str]:
        """Generate implementation recommendations."""
        recommendations = []
        
        if readiness_score < 0.5:
            recommendations.append("Address validation errors before implementation")
        elif readiness_score < 0.8:
            recommendations.append("Review warnings and optimize before implementation")
        else:
            recommendations.append("Ready for implementation - proceed with deployment")
        
        if blocking_issues:
            recommendations.append("Resolve blocking issues first")
        
        return recommendations
    
    def _check_squarespace_schema_compatibility(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check Squarespace platform compatibility for schema."""
        return {
            "notes": [
                "Add JSON-LD to Code Injection in Website Settings",
                "Place schema in Header section for best results",
                "Test with Google Rich Results Test after implementation"
            ]
        }
    
    def _check_squarespace_meta_compatibility(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Check Squarespace compatibility for meta tags."""
        return {
            "notes": [
                "Update meta tags in Page Settings > SEO tab",
                "Social sharing tags auto-generate from SEO settings",
                "Custom Open Graph tags require Code Injection"
            ]
        }
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _validate_contact_points(self, contact_points) -> Dict[str, Any]:
        """Validate contact point structures."""
        result = {"warnings": []}
        
        if isinstance(contact_points, list):
            for i, contact in enumerate(contact_points):
                if not isinstance(contact, dict) or "@type" not in contact:
                    result["warnings"].append(f"Contact point {i} missing @type")
        
        return result
    
    def _validate_address_schema(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """Validate address schema structure."""
        result = {"warnings": []}
        
        if "@type" not in address:
            result["warnings"].append("Address missing @type property")
        
        required_address_fields = ["streetAddress"]
        missing_fields = [field for field in required_address_fields if field not in address]
        
        if missing_fields:
            result["warnings"].append(f"Address missing fields: {', '.join(missing_fields)}")
        
        return result
    
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules for different schema types."""
        return {
            "Organization": {
                "required": ["name", "url"],
                "recommended": ["description", "contactPoint", "address", "logo", "sameAs"]
            },
            "LocalBusiness": {
                "required": ["name", "address"],
                "recommended": ["telephone", "openingHours", "priceRange", "image", "review"]
            },
            "FAQ": {
                "required": ["mainEntity"],
                "recommended": ["acceptedAnswer"]
            },
            "Event": {
                "required": ["name", "startDate"],
                "recommended": ["description", "location", "organizer", "endDate"]
            }
        }
