"""
AEO Agent Analyzer - Analyzes website content for visibility optimization opportunities.
"""

import json
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from ..shared.models import WebsiteData
from ..shared.llm_client import LLMClient


class AEOAnalyzer:
    """
    Analyzes websites for visibility optimization opportunities.
    
    Focuses on:
    - Schema markup gaps and quality
    - Content structure analysis  
    - Meta information assessment
    - AI response optimization opportunities
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.schema_requirements = self._load_schema_requirements()
        
    async def analyze_schema_markup(self, soup: BeautifulSoup, website_data: WebsiteData) -> Dict[str, Any]:
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
        
        # Enhance with LLM analysis
        if self.llm_client:
            llm_analysis = await self._llm_analyze_schema_opportunities(str(soup), analysis)
            analysis["llm_recommendations"] = llm_analysis
        
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
    
    async def analyze_ai_response_optimization(self, website_data: WebsiteData, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content for AI-generated response optimization."""
        analysis = {
            "question_answer_patterns": self._identify_qa_patterns(soup),
            "content_clarity_score": self._assess_content_clarity(soup),
            "structured_data_gaps": self._identify_structured_data_gaps(soup, website_data)
        }
        
        # Enhance with LLM-powered content optimization analysis
        if self.llm_client:
            content_text = soup.get_text()[:8000]  # Limit content for token management
            llm_optimization = await self._llm_analyze_content_optimization(content_text)
            analysis["llm_optimization_suggestions"] = llm_optimization
        
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
    
    async def _llm_analyze_schema_opportunities(self, html_content: str, existing_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to identify additional schema opportunities."""
        prompt = f"""
        Analyze this HTML content for schema markup opportunities. Consider the existing analysis and provide advanced recommendations.
        
        Existing Analysis:
        {json.dumps(existing_analysis, indent=2)}
        
        HTML Content (first 6000 chars):
        {html_content[:6000]}
        
        Provide JSON response with:
        {{
            "advanced_schema_opportunities": ["list of specific schema types that would benefit this content"],
            "content_based_recommendations": ["specific recommendations based on content analysis"],
            "ai_optimization_suggestions": ["ways to structure content for better AI visibility"],
            "missing_structured_data": ["specific structured data elements that should be added"]
        }}
        """
        
        try:
            response = await self.llm_client.generate_text(prompt, max_tokens=1500)
            return json.loads(response)
        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}
    
    async def _llm_analyze_content_optimization(self, content_text: str) -> Dict[str, Any]:
        """Use LLM to analyze content for AI response optimization."""
        prompt = f"""
        Analyze this content for optimization opportunities to improve visibility in AI-generated responses.
        
        Content:
        {content_text}
        
        Provide analysis focusing on:
        1. Content structure for AI comprehension
        2. Question-answer format opportunities  
        3. Key information accessibility
        4. Semantic clarity improvements
        
        Return JSON with:
        {{
            "content_structure_score": 0.85,
            "ai_comprehension_issues": ["list of issues"],
            "optimization_recommendations": ["specific actionable recommendations"],
            "question_answer_opportunities": ["content sections that could be reformatted as Q&A"],
            "semantic_improvements": ["ways to improve semantic clarity"]
        }}
        """
        
        try:
            response = await self.llm_client.generate_text(prompt, max_tokens=1200)
            return json.loads(response)
        except Exception as e:
            return {"error": f"Content optimization analysis failed: {str(e)}"}
    
    def _analyze_content_organization(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content organization."""
        return {
            "has_clear_sections": len(soup.find_all(['section', 'article'])) > 0,
            "navigation_present": soup.find('nav') is not None,
            "content_hierarchy_clear": len(soup.find_all(['h1', 'h2', 'h3'])) > 0
        }
    
    def _analyze_readability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze readability factors."""
        text = soup.get_text()
        sentences = text.split('.')
        words = text.split()
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "readability_score": "high" if avg_sentence_length < 20 else "medium" if avg_sentence_length < 30 else "low",
            "total_words": len(words)
        }
    
    def _analyze_title_tag(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze title tag."""
        title = soup.find('title')
        if not title:
            return {"present": False, "issues": ["Missing title tag"]}
        
        title_text = title.get_text().strip()
        return {
            "present": True,
            "length": len(title_text),
            "text": title_text,
            "issues": [] if 30 <= len(title_text) <= 60 else ["Title length not optimal (should be 30-60 chars)"]
        }
    
    def _analyze_meta_description(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            return {"present": False, "issues": ["Missing meta description"]}
        
        content = meta_desc.get('content', '').strip()
        return {
            "present": True,
            "length": len(content),
            "content": content,
            "issues": [] if 120 <= len(content) <= 160 else ["Meta description length not optimal (should be 120-160 chars)"]
        }
    
    def _analyze_open_graph(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze Open Graph tags."""
        og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
        
        found_tags = {}
        for tag in og_tags:
            prop = tag.get('property', '')
            content = tag.get('content', '')
            found_tags[prop] = content
        
        required_tags = ['og:title', 'og:description', 'og:image', 'og:url']
        missing_tags = [tag for tag in required_tags if tag not in found_tags]
        
        return {
            "present_tags": found_tags,
            "missing_tags": missing_tags,
            "completeness_score": (len(required_tags) - len(missing_tags)) / len(required_tags)
        }
    
    def _identify_qa_patterns(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Identify existing question-answer patterns."""
        # Look for FAQ sections, dt/dd pairs, etc.
        faqs = soup.find_all(['dt', 'details'])
        qa_sections = soup.find_all(string=re.compile(r'\?'))
        
        return {
            "faq_elements_found": len(faqs),
            "question_patterns_found": len(qa_sections),
            "has_structured_qa": len(faqs) > 0
        }
    
    def _assess_content_clarity(self, soup: BeautifulSoup) -> float:
        """Assess content clarity score."""
        text = soup.get_text()
        
        # Simple heuristics for clarity
        score = 0.5  # Base score
        
        # Bonus for good structure
        if soup.find_all(['h1', 'h2', 'h3']):
            score += 0.2
        
        # Bonus for lists
        if soup.find_all(['ul', 'ol']):
            score += 0.1
        
        # Bonus for shorter paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            avg_p_length = sum(len(p.get_text()) for p in paragraphs) / len(paragraphs)
            if avg_p_length < 200:
                score += 0.2
        
        return min(score, 1.0)
    
    def _identify_structured_data_gaps(self, soup: BeautifulSoup, website_data: WebsiteData) -> List[str]:
        """Identify gaps in structured data."""
        gaps = []
        
        # Check for contact information structure
        if not soup.find(attrs={'itemtype': lambda x: x and 'ContactPoint' in x}):
            gaps.append("Missing ContactPoint structured data")
        
        # Check for address structure
        if not soup.find(attrs={'itemtype': lambda x: x and 'PostalAddress' in x}):
            gaps.append("Missing PostalAddress structured data")
        
        return gaps
