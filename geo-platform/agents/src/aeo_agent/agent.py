"""
Main AEO agent class for visibility optimization.
Focuses on improving content discoverability through schema markup,
structured data, and AI response optimization.
"""

import json
import time
from typing import Dict, Any, List, Optional
import re
from bs4 import BeautifulSoup

from ..shared.base_agent import BaseAgent
from .analyzer import AEOAnalyzer
from .generator import AEOGenerator
from .validator import AEOValidator
from ..shared.models import (
    WebsiteData, AgentResponse, AnalysisResult, AgentType,
    PriorityLevel, ImpactLevel, EffortLevel, SchemaMarkup, SchemaType
)
from ..shared.llm_client import LLMClient


class AEOAgent(BaseAgent):
    """
    AEO Agent for Visibility Optimization.
    
    Analyzes websites for discoverability improvements through:
    - Schema markup analysis and generation
    - Structured data optimization
    - AI response optimization
    - Content structure enhancement
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("AEO Agent", llm_client)
        self.analyzer = AEOAnalyzer(llm_client)
        self.generator = AEOGenerator(llm_client)
        self.validator = AEOValidator(llm_client)
        
    def get_agent_type(self) -> str:
        return AgentType.AEO
    
    async def analyze(self, website_data: WebsiteData, client_input: Dict[str, Any] = None) -> AgentResponse:
        """
        Analyze website for visibility optimization using modular 3-phase approach.

        Args:
            website_data: Website data to analyze
            client_input: Optional client input data for enhanced analysis

        Returns:
            AgentResponse with visibility optimization recommendations
        """
        start_time = time.time()
        self._log_analysis_start(str(website_data.url))

        try:
            # Parse HTML content
            soup = BeautifulSoup(website_data.html_content, 'html.parser')

            # PHASE 1: ANALYZE - Comprehensive analysis using modular analyzer
            schema_analysis = await self.analyzer.analyze_schema_markup(soup, website_data)
            content_structure_analysis = self.analyzer.analyze_content_structure(soup)
            meta_analysis = self.analyzer.analyze_meta_information(soup, website_data)
            ai_optimization_analysis = await self.analyzer.analyze_ai_response_optimization(website_data, soup)

            # PHASE 2: GENERATE - Create implementable solutions using modular generator
            schema_packages = {}
            missing_schemas = schema_analysis.get("missing_schemas", [])
            for schema_type in missing_schemas:
                schema_package = await self.generator.generate_schema_markup(
                    schema_type, website_data, client_input.get("business_info") if client_input else None
                )
                schema_packages[schema_type] = schema_package

            # Generate meta tags improvements
            meta_package = self.generator.generate_meta_tags(website_data, meta_analysis)

            # Generate AI optimization content
            ai_optimization_content = await self.generator.generate_ai_optimization_content(website_data, ai_optimization_analysis)

            # Generate content structure improvements
            content_structure_improvements = self.generator.generate_content_structure_improvements(content_structure_analysis)

            # PHASE 3: VALIDATE - Ensure quality and implementation readiness
            schema_validations = {}
            for schema_type, package in schema_packages.items():
                validation = await self.validator.validate_schema_markup(package)
                schema_validations[schema_type] = validation

            # Validate meta tags
            meta_validation = self.validator.validate_meta_tags(meta_package)

            # Validate AI optimization recommendations
            ai_optimization_validation = self.validator.validate_ai_optimization(ai_optimization_content)

            # Validate content structure improvements
            structure_validation = self.validator.validate_content_structure_improvements(content_structure_improvements)

            # Check overall implementation readiness
            all_generated_content = {
                "schema_packages": schema_packages,
                "schema_validations": schema_validations,
                "meta_package": meta_package,
                "meta_validation": meta_validation,
                "ai_optimization_content": ai_optimization_content,
                "ai_optimization_validation": ai_optimization_validation,
                "content_structure_improvements": content_structure_improvements,
                "structure_validation": structure_validation
            }

            implementation_readiness = await self.validator.validate_implementation_readiness(all_generated_content)

            # Convert analysis results to AnalysisResult format for compatibility
            results = self._convert_to_analysis_results(
                schema_analysis, content_structure_analysis, meta_analysis, ai_optimization_analysis,
                schema_packages, meta_package, ai_optimization_content, content_structure_improvements,
                schema_validations, meta_validation, ai_optimization_validation, structure_validation,
                implementation_readiness
            )

            processing_time = time.time() - start_time
            confidence = implementation_readiness.get("readiness_score", 0.0)

            self._log_analysis_complete(str(website_data.url), len(results), confidence)

            return self._create_response(
                results=results,
                confidence=confidence,
                processing_time=processing_time,
                metadata={
                    "analysis_phase": {
                        "schema_analysis": schema_analysis,
                        "content_structure_analysis": content_structure_analysis,
                        "meta_analysis": meta_analysis,
                        "ai_optimization_analysis": ai_optimization_analysis
                    },
                    "generation_phase": {
                        "schema_packages": {k: v["schema_type"] for k, v in schema_packages.items()},
                        "meta_package_keys": list(meta_package.keys()),
                        "ai_optimization_keys": list(ai_optimization_content.keys()),
                        "structure_improvement_keys": list(content_structure_improvements.keys())
                    },
                    "validation_phase": {
                        "schema_validation_summary": {k: v["is_valid"] for k, v in schema_validations.items()},
                        "meta_validation_status": meta_validation["is_valid"],
                        "ai_optimization_scores": {
                            "quality": ai_optimization_validation["quality_score"],
                            "actionability": ai_optimization_validation["actionability_score"]
                        },
                        "structure_validation_scores": {
                            "feasibility": structure_validation["implementation_feasibility"],
                            "impact": structure_validation["impact_score"]
                        }
                    },
                    "implementation_readiness": implementation_readiness,
                    "modular_pattern_version": "3-phase"
                }
            )

        except Exception as e:
            self._log_error(e, f"analyzing {website_data.url}")
            processing_time = time.time() - start_time

            return self._create_response(
                results=[self._create_error_result(str(e))],
                confidence=0.0,
                processing_time=processing_time
            )
    
    async def analyze_legacy(self, website_data: WebsiteData) -> AgentResponse:
        """
        Legacy analyze method for backward compatibility.
        """
        # Redirect to new modular analyze method
        return await self.analyze(website_data)

    async def _analyze_schema_markup(self, soup: BeautifulSoup, website_data: WebsiteData) -> List[AnalysisResult]:
        """Analyze existing schema markup and identify gaps."""
        results = []
        
        # Use enhanced analyzer with LLM capabilities
        schema_analysis = await self.analyzer.analyze_schema_markup(soup, website_data)
        
        # Extract existing and missing schemas from analysis
        existing_schemas = [s["type"] for s in schema_analysis.get("existing_schemas", [])]
        missing_schemas = schema_analysis.get("missing_schemas", [])
        
        if missing_schemas:
            results.append(AnalysisResult(
                id="schema_gaps",
                type="schema_markup",
                title="Missing Schema Markup",
                description=f"Found {len(missing_schemas)} missing schema types that could improve visibility",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation=f"Add missing schema markup: {', '.join(missing_schemas)}",
                implementation_steps=[
                    "Generate JSON-LD structured data for missing schemas",
                    "Add scripts to page head section",
                    "Test with Google's Rich Results Test tool",
                    "Monitor search appearance changes"
                ],
                code_examples=[self._generate_schema_example(schema) for schema in missing_schemas[:2]],
                confidence=0.9,
                metadata={
                    "missing_schemas": missing_schemas,
                    "existing_schemas": existing_schemas,
                    "llm_analysis": schema_analysis.get("llm_recommendations", {})
                }
            ))
        
        # Analyze quality of existing schemas
        quality_issues = schema_analysis.get("quality_issues", [])
        if quality_issues:
            results.append(AnalysisResult(
                id="schema_quality",
                type="schema_markup",
                title="Schema Markup Quality Issues",
                description="Existing schema markup has quality issues that may reduce effectiveness",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Fix schema markup quality issues",
                implementation_steps=[
                    "Review and validate existing schema markup",
                    "Fix identified issues",
                    "Ensure all required properties are present",
                    "Test with validation tools"
                ],
                confidence=0.8,
                metadata={"quality_issues": quality_issues}
            ))
        
        return results
    
    async def _generate_structured_data(self, website_data: WebsiteData) -> List[AnalysisResult]:
        """Generate structured data recommendations."""
        results = []
        
        # Extract business information from metadata
        business_name = self._extract_business_name(website_data)
        business_type = website_data.metadata.get("business_type", "organization")
        
        if business_name:
            # Generate Organization schema
            org_schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": business_name,
                "url": str(website_data.url),
                "description": website_data.meta_description or f"Website for {business_name}"
            }
            
            results.append(AnalysisResult(
                id="organization_schema",
                type="structured_data",
                title="Organization Schema Generation",
                description="Generate comprehensive organization schema markup",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation="Add Organization schema to establish business entity",
                implementation_steps=[
                    "Create Organization schema with business details",
                    "Include contact information and social profiles",
                    "Add to website head section",
                    "Validate with structured data testing tools"
                ],
                code_examples=[json.dumps(org_schema, indent=2)],
                confidence=0.95,
                metadata={"schema_type": "Organization", "business_name": business_name}
            ))
        
        # Generate FAQ schema if applicable
        faq_opportunities = self._identify_faq_opportunities(website_data)
        if faq_opportunities:
            results.append(AnalysisResult(
                id="faq_schema",
                type="structured_data",
                title="FAQ Schema Opportunities",
                description="Add FAQ schema to improve visibility in search results",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.MEDIUM,
                recommendation="Create FAQ schema for common questions",
                implementation_steps=[
                    "Identify frequently asked questions",
                    "Create structured FAQ schema markup",
                    "Add to relevant pages",
                    "Test FAQ rich snippets appearance"
                ],
                confidence=0.8,
                metadata={"faq_opportunities": faq_opportunities}
            ))
        
        return results
    
    async def _optimize_for_ai_responses(self, website_data: WebsiteData) -> List[AnalysisResult]:
        """Optimize content for AI-generated responses."""
        results = []
        
        # Use enhanced analyzer with LLM capabilities
        soup = BeautifulSoup(website_data.html_content, 'html.parser')
        ai_analysis = await self.analyzer.analyze_ai_response_optimization(website_data, soup)
        
        # Extract optimization opportunities
        optimization_opportunities = []
        
        # Add traditional analysis
        content = website_data.extracted_text or self._extract_text_content(website_data.html_content)
        
        # Look for missing direct answers to common questions
        if "consulting" in content.lower():
            optimization_opportunities.append({
                "type": "direct_answers",
                "description": "Add clear, direct answers to common consulting questions",
                "example": "What services do we offer? We provide [specific services list]"
            })
        
        # Check for contact information clarity
        if not self._has_clear_contact_info(content):
            optimization_opportunities.append({
                "type": "contact_clarity",
                "description": "Make contact information more prominent and structured",
                "example": "Phone: [number], Email: [email], Address: [address]"
            })
        
        # Include LLM optimization suggestions
        llm_suggestions = ai_analysis.get("llm_optimization_suggestions", {})
        
        if optimization_opportunities or llm_suggestions:
            results.append(AnalysisResult(
                id="ai_response_optimization",
                type="ai_optimization",
                title="AI Response Optimization",
                description="Optimize content structure for better AI search engine visibility",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.MEDIUM,
                recommendation="Restructure content to provide clear, direct answers",
                implementation_steps=[
                    "Add clear headings for key information",
                    "Provide direct answers to common questions",
                    "Structure contact information clearly",
                    "Use bullet points for easy scanning"
                ],
                confidence=0.7,
                metadata={
                    "opportunities": optimization_opportunities,
                    "llm_analysis": llm_suggestions,
                    "content_clarity_score": ai_analysis.get("content_clarity_score", 0.0)
                }
            ))
        
        return results
    
    async def _analyze_content_structure(self, soup: BeautifulSoup) -> List[AnalysisResult]:
        """Analyze content structure for optimization opportunities."""
        results = []
        
        # Check heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        heading_issues = []
        
        # Check for missing H1
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            heading_issues.append("Missing H1 tag")
        elif len(h1_tags) > 1:
            heading_issues.append("Multiple H1 tags found")
        
        # Check heading hierarchy
        if not self._has_proper_heading_hierarchy(headings):
            heading_issues.append("Improper heading hierarchy")
        
        if heading_issues:
            results.append(AnalysisResult(
                id="heading_structure",
                type="content_structure",
                title="Heading Structure Issues",
                description="Heading structure needs optimization for better content hierarchy",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Fix heading structure for better content organization",
                implementation_steps=[
                    "Ensure single H1 tag per page",
                    "Follow proper heading hierarchy (H1 > H2 > H3...)",
                    "Use descriptive, keyword-rich headings",
                    "Test with accessibility tools"
                ],
                confidence=0.9,
                metadata={"heading_issues": heading_issues, "heading_count": len(headings)}
            ))
        
        return results
    
    async def _analyze_meta_information(self, soup: BeautifulSoup, website_data: WebsiteData) -> List[AnalysisResult]:
        """Analyze meta information for optimization."""
        results = []
        
        # Check title tag
        title_tag = soup.find('title')
        title_issues = []
        
        if not title_tag or not title_tag.string:
            title_issues.append("Missing title tag")
        elif len(title_tag.string) > 60:
            title_issues.append("Title too long (>60 characters)")
        elif len(title_tag.string) < 30:
            title_issues.append("Title too short (<30 characters)")
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            title_issues.append("Missing meta description")
        elif len(meta_desc.get('content', '')) > 160:
            title_issues.append("Meta description too long (>160 characters)")
        
        if title_issues:
            results.append(AnalysisResult(
                id="meta_optimization",
                type="meta_information",
                title="Meta Information Optimization",
                description="Meta tags need optimization for better search visibility",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation="Optimize title tags and meta descriptions",
                implementation_steps=[
                    "Write compelling, keyword-rich title tags (30-60 chars)",
                    "Create descriptive meta descriptions (120-160 chars)",
                    "Ensure each page has unique meta information",
                    "Test appearance in search results"
                ],
                confidence=0.95,
                metadata={"issues": title_issues}
            ))
        
        return results
    
    def _load_schema_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load schema templates for different business types."""
        return {
            "Organization": {
                "required": ["name", "url"],
                "recommended": ["description", "contactPoint", "address", "logo"]
            },
            "LocalBusiness": {
                "required": ["name", "address", "telephone"],
                "recommended": ["openingHours", "priceRange", "image"]
            },
            "Product": {
                "required": ["name", "description"],
                "recommended": ["price", "availability", "review"]
            },
            "FAQ": {
                "required": ["mainEntity"],
                "recommended": ["acceptedAnswer"]
            },
            "Review": {
                "required": ["reviewBody", "author"],
                "recommended": ["reviewRating", "datePublished"]
            }
        }
    
    def _determine_required_schemas(self, website_data: WebsiteData) -> List[str]:
        """Determine required schema types based on website content."""
        required = ["Organization"]  # Always needed
        
        content = (website_data.extracted_text or "").lower()
        
        # Business-specific schemas
        if any(word in content for word in ["consulting", "services", "business"]):
            required.append("LocalBusiness")
        
        # Product-related schemas
        if any(word in content for word in ["product", "sell", "buy", "price"]):
            required.append("Product")
        
        # FAQ opportunities
        if any(word in content for word in ["question", "answer", "faq", "help"]):
            required.append("FAQ")
        
        return required
    
    def _generate_schema_example(self, schema_type: str) -> str:
        """Generate example schema markup for given type."""
        examples = {
            "Organization": '''
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Organization Name",
  "url": "https://yourwebsite.com",
  "description": "Brief description of your organization"
}''',
            "LocalBusiness": '''
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Your Business Name",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "City",
    "addressRegion": "State",
    "postalCode": "12345"
  },
  "telephone": "+1-555-123-4567"
}''',
            "FAQ": '''
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What services do you offer?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "We offer consulting services including..."
    }
  }]
}'''
        }
        return examples.get(schema_type, f"// {schema_type} schema example")
    
    async def _assess_schema_quality(self, json_ld_scripts) -> List[str]:
        """Assess quality of existing schema markup."""
        issues = []
        
        for script in json_ld_scripts:
            try:
                schema_data = json.loads(script.string or '{}')
                
                # Check for required @context
                if '@context' not in schema_data:
                    issues.append("Missing @context property")
                
                # Check for @type
                if '@type' not in schema_data:
                    issues.append("Missing @type property")
                
                # Check for empty or minimal content
                if len(schema_data.keys()) < 3:
                    issues.append("Schema has minimal properties")
                
            except json.JSONDecodeError:
                issues.append("Invalid JSON-LD syntax")
        
        return issues
    
    def _convert_to_analysis_results(self, *analysis_data) -> List[AnalysisResult]:
        """
        Convert new 3-phase analysis format to AnalysisResult objects for compatibility.
        """
        results = []

        (schema_analysis, content_structure_analysis, meta_analysis, ai_optimization_analysis,
         schema_packages, meta_package, ai_optimization_content, content_structure_improvements,
         schema_validations, meta_validation, ai_optimization_validation, structure_validation,
         implementation_readiness) = analysis_data

        # Schema Analysis Results
        missing_schemas = schema_analysis.get("missing_schemas", [])
        if missing_schemas:
            results.append(AnalysisResult(
                id="missing_schema_markup",
                type="schema_markup",
                title="Missing Schema Markup Opportunities",
                description=f"Found {len(missing_schemas)} missing schema types that could improve visibility",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation=f"Implement missing schema markup: {', '.join(missing_schemas)}",
                implementation_steps=[
                    "Generate JSON-LD structured data for missing schemas",
                    "Add scripts to page head section",
                    "Test with Google's Rich Results Test tool",
                    "Monitor search appearance changes"
                ],
                confidence=0.9,
                metadata={
                    "missing_schemas": missing_schemas,
                    "generated_packages": list(schema_packages.keys()),
                    "validation_summary": {k: v["is_valid"] for k, v in schema_validations.items()}
                }
            ))

        # Meta Tag Results
        if not meta_validation.get("is_valid", True):
            results.append(AnalysisResult(
                id="meta_tag_optimization",
                type="meta_optimization",
                title="Meta Tag Optimization Needed",
                description="Meta tags require optimization for better search visibility",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation="Implement optimized meta tags package",
                implementation_steps=[
                    "Update title tag with optimal length and keywords",
                    "Improve meta description for better click-through rates",
                    "Add Open Graph tags for social media sharing",
                    "Include Twitter Card markup"
                ],
                confidence=0.9,
                metadata={
                    "meta_validation": meta_validation,
                    "generated_package": list(meta_package.keys())
                }
            ))

        # Content Structure Results
        heading_issues = content_structure_analysis.get("heading_structure", {}).get("hierarchy_issues", [])
        if heading_issues:
            results.append(AnalysisResult(
                id="content_structure_optimization",
                type="content_structure",
                title="Content Structure Improvements Needed",
                description=f"Found {len(heading_issues)} content structure issues affecting SEO and accessibility",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Implement content structure improvements",
                implementation_steps=content_structure_improvements.get("heading_structure_fixes", [])[:4],
                confidence=structure_validation.get("implementation_feasibility", 0.8),
                metadata={
                    "heading_issues": heading_issues,
                    "structure_validation": structure_validation,
                    "improvements_generated": list(content_structure_improvements.keys())
                }
            ))

        # AI Optimization Results
        ai_quality_score = ai_optimization_validation.get("quality_score", 0.0)
        if ai_quality_score < 0.7:
            results.append(AnalysisResult(
                id="ai_response_optimization",
                type="ai_optimization",
                title="AI Response Optimization Opportunities",
                description=f"Content optimization score is {ai_quality_score:.2f}/1.0, below recommended threshold",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.MEDIUM,
                recommendation="Implement AI-friendly content improvements",
                implementation_steps=[
                    "Add structured Q&A content sections",
                    "Improve content clarity and scannability",
                    "Enhance semantic markup",
                    "Implement accessibility improvements"
                ],
                confidence=ai_optimization_validation.get("actionability_score", 0.7),
                metadata={
                    "ai_optimization_analysis": ai_optimization_analysis,
                    "ai_optimization_validation": ai_optimization_validation,
                    "generated_content": list(ai_optimization_content.keys())
                }
            ))

        # Implementation Readiness Results
        if not implementation_readiness.get("ready_for_implementation", False):
            blocking_issues = implementation_readiness.get("blocking_issues", [])
            results.append(AnalysisResult(
                id="implementation_readiness",
                type="implementation_readiness",
                title="Implementation Readiness Issues",
                description=f"Found {len(blocking_issues)} blocking issues preventing implementation",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Resolve blocking issues before proceeding with implementation",
                implementation_steps=[
                    "Address validation errors in generated content",
                    "Resolve quality score issues",
                    "Complete missing required components",
                    "Verify all generated content meets standards"
                ],
                confidence=implementation_readiness.get("readiness_score", 0.0),
                metadata={
                    "blocking_issues": blocking_issues,
                    "readiness_score": implementation_readiness.get("readiness_score", 0.0),
                    "implementation_priority": implementation_readiness.get("implementation_priority", "medium"),
                    "estimated_effort": implementation_readiness.get("estimated_effort", "medium")
                }
            ))

        # If no major issues found, add a positive result
        if not results:
            results.append(AnalysisResult(
                id="aeo_optimization_ready",
                type="optimization_ready",
                title="Ready for AEO Implementation",
                description="All generated optimizations are validated and ready for implementation",
                priority=PriorityLevel.LOW,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation="Proceed with implementing generated optimizations",
                implementation_steps=[
                    "Deploy generated schema markup",
                    "Apply meta tag optimizations",
                    "Implement content structure improvements",
                    "Apply AI optimization recommendations",
                    "Monitor implementation results"
                ],
                confidence=implementation_readiness.get("readiness_score", 1.0),
                metadata={"all_validations_passed": True, "total_optimizations": len(schema_packages) + 1}
            ))

        return results

    def _extract_business_name(self, website_data: WebsiteData) -> Optional[str]:
        """Extract business name from various sources."""
        # Try title first
        if website_data.title:
            return website_data.title.split(' | ')[0].split(' - ')[0]

        # Try from metadata
        if "business_name" in website_data.metadata:
            return website_data.metadata["business_name"]

        # Try from URL
        url_parts = str(website_data.url).split('.')
        if len(url_parts) > 1:
            return url_parts[0].replace('https://', '').replace('http://', '').title()

        return None
    
    def _identify_faq_opportunities(self, website_data: WebsiteData) -> List[str]:
        """Identify opportunities for FAQ schema."""
        content = (website_data.extracted_text or "").lower()
        opportunities = []
        
        # Common question patterns
        question_patterns = [
            "what is", "what are", "how do", "how to", "why do", "when do",
            "where is", "who is", "how much", "how many"
        ]
        
        for pattern in question_patterns:
            if pattern in content:
                opportunities.append(f"Questions starting with '{pattern}'")
        
        return opportunities[:3]  # Limit to top 3
    
    def _extract_text_content(self, html_content: str) -> str:
        """Extract clean text content from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def _has_clear_contact_info(self, content: str) -> bool:
        """Check if content has clear contact information."""
        contact_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr)\b'  # Address
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in contact_patterns)
    
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
    
    def _calculate_overall_confidence(self, results: List[AnalysisResult]) -> float:
        """Calculate overall confidence score based on results."""
        if not results:
            return 0.0
        
        total_confidence = sum(result.confidence for result in results)
        return min(total_confidence / len(results), 1.0)
    
    def _create_error_result(self, error_message: str) -> AnalysisResult:
        """Create an error result."""
        return AnalysisResult(
            id="analysis_error",
            type="error",
            title="Analysis Error",
            description=f"Error during AEO analysis: {error_message}",
            priority=PriorityLevel.LOW,
            impact=ImpactLevel.LOW,
            effort=EffortLevel.LOW,
            recommendation="Review error and retry analysis",
            confidence=0.0
        )
