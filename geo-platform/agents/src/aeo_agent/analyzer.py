"""
AEO Agent Analyzer - Analyzes website content for visibility optimization opportunities.
"""

import json
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from ..shared.models import WebsiteData


class AEOAnalyzer:
    """
    Analyzes websites for visibility optimization opportunities.
    
    Focuses on:
    - Schema markup gaps and quality
    - Content structure analysis  
    - Meta information assessment
    - AI response optimization opportunities
    """
    
    def __init__(self):
        self.schema_requirements = self._load_schema_requirements()
        
    def analyze_schema_markup(self, soup: BeautifulSoup, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze existing schema markup and identify gaps."""
        analysis = {
            "existing_schemas": [],
            "missing_schemas": [],
            "quality_issues": [],
            "recommendations": []
        }
        
        # Find existing JSON-LD scripts
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                schema_data = json.loads(script.string or '{}')
                schema_type = schema_data.get('@type', 'Unknown')
                analysis["existing_schemas"].append({
                    "type": schema_type,
                    "data": schema_data,
                    "quality_score": self._assess_schema_quality(schema_data)
                })
            except json.JSONDecodeError:
                analysis["quality_issues"].append("Invalid JSON-LD syntax found")
        
        # Determine required schemas based on content and business type
        required_schemas = self._determine_required_schemas(website_data)
        existing_types = [s["type"] for s in analysis["existing_schemas"]]
        analysis["missing_schemas"] = [s for s in required_schemas if s not in existing_types]
        
        return analysis
    
    def analyze_content_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content structure for optimization opportunities."""
        analysis = {
            "heading_structure": self._analyze_heading_structure(soup),
            "content_organization": self._analyze_content_organization(soup),
            "readability_factors": self._analyze_readability(soup)
        }
        
        return analysis
    
    def analyze_meta_information(self, soup: BeautifulSoup, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze meta information for optimization."""
        analysis = {
            "title_analysis": self._analyze_title_tag(soup),
            "meta_description_analysis": self._analyze_meta_description(soup),
            "open_graph_analysis": self._analyze_open_graph(soup),
            "recommendations": []
        }
        
        return analysis
    
    def analyze_ai_response_optimization(self, website_data: WebsiteData, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content for AI-generated response optimization."""
        analysis = {
            "question_answer_patterns": self._identify_qa_patterns(soup),
            "content_clarity_score": self._assess_content_clarity(soup),
            "structured_data_gaps": self._identify_structured_data_gaps(soup, website_data)
        }
        
        return analysis
    
    def _load_schema_requirements(self) -> Dict[str, List[str]]:
        """Load schema requirements for different business types."""
        return {
            "consulting": ["Organization", "LocalBusiness", "FAQ"],
            "education": ["Organization", "EducationalOrganization", "FAQ"],
            "student_organization": ["Organization", "FAQ", "Event"],
            "default": ["Organization"]
        }
    
    def _determine_required_schemas(self, website_data: WebsiteData) -> List[str]:
        """Determine required schema types based on website content and business type."""
        business_type = website_data.metadata.get("business_type", "default")
        content = (website_data.extracted_text or "").lower()
        
        # Get base requirements
        required = self.schema_requirements.get(business_type, self.schema_requirements["default"]).copy()
        
        # Add content-based requirements
        if any(word in content for word in ["consulting", "services", "business"]):
            if "LocalBusiness" not in required:
                required.append("LocalBusiness")
        
        return required
    
    def _assess_schema_quality(self, schema_data: Dict[str, Any]) -> float:
        """Assess quality of schema markup."""
        score = 0.0
        
        # Check for @context
        if "@context" in schema_data:
            score += 0.25
        
        # Check for @type
        if "@type" in schema_data:
            score += 0.25
        
        # Check for substantial content (more than 3 properties)
        if len(schema_data.keys()) > 3:
            score += 0.25
        
        # Check for required properties based on type
        schema_type = schema_data.get("@type", "")
        if self._has_required_properties(schema_data, schema_type):
            score += 0.25
        
        return score
    
    def _has_required_properties(self, schema_data: Dict[str, Any], schema_type: str) -> bool:
        """Check if schema has required properties for its type."""
        required_props = {
            "Organization": ["name", "url"],
            "LocalBusiness": ["name", "address"],
            "FAQ": ["mainEntity"],
            "Event": ["name", "startDate"]
        }
        
        props = required_props.get(schema_type, [])
        return all(prop in schema_data for prop in props)
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure and hierarchy."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        analysis = {
            "total_headings": len(headings),
            "h1_count": len(soup.find_all('h1')),
            "hierarchy_issues": []
        }
        
        # Check for issues
        if analysis["h1_count"] == 0:
            analysis["hierarchy_issues"].append("Missing H1 tag")
        elif analysis["h1_count"] > 1:
            analysis["hierarchy_issues"].append("Multiple H1 tags found")
        
        # Check hierarchy
        if not self._has_proper_heading_hierarchy(headings):
            analysis["hierarchy_issues"].append("Improper heading hierarchy")
        
        return analysis
    
    def _has_proper_heading_hierarchy(self, headings) -> bool:
        """Check if headings follow proper hierarchy."""
        if not headings:
            return False
        
        current_level = 0
        for heading in headings:
            level = int(heading.name[1])  # Extract number from h1, h2, etc.
            
            if current_level == 0:
                current_level = level
            elif level > current_level + 1:
                return False  # Skipped a level
            
            current_level = level
        
        return True
