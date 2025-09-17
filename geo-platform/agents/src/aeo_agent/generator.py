"""
AEO Agent Generator - Generates schema markup, meta tags, and optimization code.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..shared.models import WebsiteData, BusinessInfo
from ..shared.llm_client import LLMClient


class AEOGenerator:
    """
    Generates implementable solutions for visibility optimization.

    Creates:
    - JSON-LD schema markup
    - Optimized meta tags
    - Structured data implementations
    - AI-friendly content structures
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.schema_templates = self._load_schema_templates()

    async def generate_schema_markup(self, schema_type: str, website_data: WebsiteData, business_info: Optional[BusinessInfo] = None) -> Dict[str, Any]:
        """Generate comprehensive schema markup package for specified type."""

        # Generate base schema
        if schema_type == "Organization":
            base_schema = self._generate_organization_schema(website_data, business_info)
        elif schema_type == "LocalBusiness":
            base_schema = self._generate_local_business_schema(website_data, business_info)
        elif schema_type == "FAQ":
            base_schema = await self._generate_faq_schema(website_data)
        elif schema_type == "Event":
            base_schema = self._generate_event_schema(website_data)
        elif schema_type == "Product":
            base_schema = self._generate_product_schema(website_data)
        else:
            base_schema = self._generate_basic_schema(schema_type, website_data)

        # Enhance with LLM if available
        enhanced_schema = base_schema
        if self.llm_client:
            enhanced_schema = await self._llm_enhance_schema(base_schema, website_data, schema_type)

        return {
            "schema_type": schema_type,
            "json_ld": enhanced_schema,
            "implementation_notes": self._generate_implementation_notes(schema_type),
            "validation_requirements": self._get_validation_requirements(schema_type)
        }

    def generate_meta_tags(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized meta tags package."""
        meta_package = {
            "title_tag": self._generate_optimized_title(website_data, analysis),
            "meta_description": self._generate_optimized_description(website_data, analysis),
            "open_graph_tags": self._generate_open_graph_tags(website_data),
            "twitter_cards": self._generate_twitter_cards(website_data),
            "additional_meta": self._generate_additional_meta_tags(website_data)
        }

        return meta_package

    async def generate_ai_optimization_content(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-friendly content structures."""
        optimization_package = {
            "structured_qa_content": await self._generate_qa_content(website_data, analysis),
            "content_restructuring": self._generate_content_restructuring(analysis),
            "semantic_improvements": self._generate_semantic_improvements(analysis),
            "accessibility_enhancements": self._generate_accessibility_enhancements(analysis)
        }

        return optimization_package

    def generate_content_structure_improvements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content structure improvement recommendations."""
        improvements = {
            "heading_structure_fixes": self._generate_heading_fixes(analysis),
            "content_organization": self._generate_content_organization(analysis),
            "readability_improvements": self._generate_readability_improvements(analysis)
        }

        return improvements

    def _load_schema_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load schema templates for different types."""
        return {
            "Organization": {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "",
                "url": "",
                "description": "",
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": "",
                    "contactType": "customer service"
                }
            },
            "LocalBusiness": {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": "",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                    "addressLocality": "",
                    "addressRegion": "",
                    "postalCode": ""
                },
                "telephone": "",
                "url": ""
            },
            "FAQ": {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": []
            }
        }

    def _generate_organization_schema(self, website_data: WebsiteData, business_info: Optional[BusinessInfo] = None) -> Dict[str, Any]:
        """Generate Organization schema."""
        schema = self.schema_templates["Organization"].copy()

        # Extract business name
        business_name = self._extract_business_name(website_data, business_info)
        schema["name"] = business_name or "Organization Name"
        schema["url"] = str(website_data.url)

        if website_data.meta_description:
            schema["description"] = website_data.meta_description

        # Add contact information if available
        if business_info:
            if business_info.phone:
                schema["contactPoint"]["telephone"] = business_info.phone
            if business_info.email:
                schema["contactPoint"]["email"] = business_info.email

        return schema

    def _generate_local_business_schema(self, website_data: WebsiteData, business_info: Optional[BusinessInfo] = None) -> Dict[str, Any]:
        """Generate LocalBusiness schema."""
        schema = self.schema_templates["LocalBusiness"].copy()

        business_name = self._extract_business_name(website_data, business_info)
        schema["name"] = business_name or "Local Business"
        schema["url"] = str(website_data.url)

        if business_info:
            if business_info.phone:
                schema["telephone"] = business_info.phone
            if business_info.address:
                # Parse address if it's a string
                if isinstance(business_info.address, str):
                    schema["address"]["streetAddress"] = business_info.address
                else:
                    schema["address"] = business_info.address

        return schema

    async def _generate_faq_schema(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Generate FAQ schema with LLM-powered question generation."""
        schema = self.schema_templates["FAQ"].copy()

        # Use LLM to generate relevant FAQ content
        if self.llm_client:
            content = website_data.extracted_text or ""
            faq_content = await self._llm_generate_faq_content(content[:6000])
            schema["mainEntity"] = faq_content.get("questions", [])

        return schema

    def _generate_event_schema(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Generate Event schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": self._extract_business_name(website_data) or "Event",
            "url": str(website_data.url),
            "startDate": datetime.now().isoformat(),
            "location": {
                "@type": "Place",
                "name": "Event Location"
            }
        }

        return schema

    def _generate_product_schema(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Generate Product schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": self._extract_business_name(website_data) or "Product",
            "url": str(website_data.url),
            "description": website_data.meta_description or "Product description"
        }

        return schema

    def _generate_basic_schema(self, schema_type: str, website_data: WebsiteData) -> Dict[str, Any]:
        """Generate basic schema for any type."""
        return {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": self._extract_business_name(website_data) or f"{schema_type} Name",
            "url": str(website_data.url)
        }

    async def _llm_enhance_schema(self, base_schema: Dict[str, Any], website_data: WebsiteData, schema_type: str) -> Dict[str, Any]:
        """Enhance schema with LLM-generated content."""
        prompt = f"""
        Enhance this {schema_type} schema with relevant information from the website content.

        Base Schema:
        {json.dumps(base_schema, indent=2)}

        Website Content:
        {website_data.extracted_text[:4000] if website_data.extracted_text else "No content available"}

        Website Title: {website_data.title or "No title"}
        Website Description: {website_data.meta_description or "No description"}

        Please enhance the schema by:
        1. Adding relevant properties based on the content
        2. Filling in missing information where possible
        3. Ensuring all required properties are present
        4. Adding optional properties that would be valuable

        Return only the enhanced JSON schema, no explanations.
        """

        try:
            response = await self.llm_client.generate_text(prompt, max_tokens=1500)
            enhanced_schema = json.loads(response)
            return enhanced_schema
        except Exception as e:
            # Return base schema if enhancement fails
            return base_schema

    async def _llm_generate_faq_content(self, content: str) -> Dict[str, Any]:
        """Generate FAQ content using LLM."""
        prompt = f"""
        Based on this website content, generate 3-5 relevant FAQ questions and answers that would be valuable for visitors.

        Content:
        {content}

        Return JSON in this format:
        {{
            "questions": [
                {{
                    "@type": "Question",
                    "name": "What services do you offer?",
                    "acceptedAnswer": {{
                        "@type": "Answer",
                        "text": "We offer comprehensive consulting services..."
                    }}
                }}
            ]
        }}
        """

        try:
            response = await self.llm_client.generate_text(prompt, max_tokens=1200)
            return json.loads(response)
        except Exception as e:
            return {"questions": []}

    def _generate_optimized_title(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> str:
        """Generate optimized title tag."""
        if website_data.title and 30 <= len(website_data.title) <= 60:
            return website_data.title

        business_name = self._extract_business_name(website_data)
        if business_name:
            return f"{business_name} - Professional Services"

        return "Professional Services - Quality Solutions"

    def _generate_optimized_description(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> str:
        """Generate optimized meta description."""
        if website_data.meta_description and 120 <= len(website_data.meta_description) <= 160:
            return website_data.meta_description

        business_name = self._extract_business_name(website_data)
        if business_name:
            return f"Professional services from {business_name}. Quality solutions tailored to your needs. Contact us today for expert consultation."

        return "Professional services and quality solutions. Expert consultation and tailored approaches to meet your specific requirements."

    def _generate_open_graph_tags(self, website_data: WebsiteData) -> Dict[str, str]:
        """Generate Open Graph meta tags."""
        business_name = self._extract_business_name(website_data)

        return {
            "og:title": website_data.title or f"{business_name} - Professional Services" if business_name else "Professional Services",
            "og:description": website_data.meta_description or "Quality professional services",
            "og:url": str(website_data.url),
            "og:type": "website",
            "og:site_name": business_name or "Professional Services"
        }

    def _generate_twitter_cards(self, website_data: WebsiteData) -> Dict[str, str]:
        """Generate Twitter Card meta tags."""
        return {
            "twitter:card": "summary",
            "twitter:title": website_data.title or "Professional Services",
            "twitter:description": website_data.meta_description or "Quality professional services"
        }

    def _generate_additional_meta_tags(self, website_data: WebsiteData) -> Dict[str, str]:
        """Generate additional meta tags."""
        return {
            "viewport": "width=device-width, initial-scale=1.0",
            "robots": "index, follow",
            "language": "en",
            "author": self._extract_business_name(website_data) or "Professional Services"
        }

    async def _generate_qa_content(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured Q&A content."""
        if not self.llm_client:
            return {"qa_sections": []}

        content = website_data.extracted_text or ""
        prompt = f"""
        Create structured Q&A content based on this website content to improve AI response visibility.

        Content:
        {content[:5000]}

        Generate 3-5 question-answer pairs that would help AI systems understand and present this content better.

        Return JSON:
        {{
            "qa_sections": [
                {{
                    "question": "What services are offered?",
                    "answer": "Specific answer based on content",
                    "placement_suggestion": "homepage hero section"
                }}
            ]
        }}
        """

        try:
            response = await self.llm_client.generate_text(prompt, max_tokens=1000)
            return json.loads(response)
        except Exception as e:
            return {"qa_sections": []}

    def _generate_content_restructuring(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate content restructuring recommendations."""
        recommendations = []

        if analysis.get("content_clarity_score", 0) < 0.7:
            recommendations.append("Break long paragraphs into shorter, scannable sections")
            recommendations.append("Add clear subheadings for each main topic")
            recommendations.append("Use bullet points for key information")

        return recommendations

    def _generate_semantic_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate semantic improvement suggestions."""
        improvements = [
            "Use descriptive heading tags (H1, H2, H3) with relevant keywords",
            "Structure contact information with proper markup",
            "Add semantic HTML5 elements (article, section, aside)"
        ]

        return improvements

    def _generate_accessibility_enhancements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate accessibility enhancement suggestions."""
        enhancements = [
            "Add alt text to all images",
            "Ensure proper color contrast ratios",
            "Use ARIA labels for interactive elements",
            "Implement skip navigation links"
        ]

        return enhancements

    def _generate_heading_fixes(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate heading structure fixes."""
        fixes = []

        heading_analysis = analysis.get("heading_structure", {})
        issues = heading_analysis.get("hierarchy_issues", [])

        for issue in issues:
            if "Missing H1" in issue:
                fixes.append("Add a single, descriptive H1 tag to the page")
            elif "Multiple H1" in issue:
                fixes.append("Use only one H1 tag per page, convert others to H2")
            elif "hierarchy" in issue:
                fixes.append("Follow proper heading hierarchy (H1 > H2 > H3)")

        return fixes

    def _generate_content_organization(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate content organization recommendations."""
        recommendations = [
            "Group related content into clear sections",
            "Use consistent navigation structure",
            "Implement breadcrumb navigation for deeper pages",
            "Create a logical content hierarchy"
        ]

        return recommendations

    def _generate_readability_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate readability improvement suggestions."""
        improvements = []

        readability = analysis.get("readability_factors", {})
        if readability.get("readability_score") == "low":
            improvements.extend([
                "Reduce average sentence length to under 20 words",
                "Use simpler vocabulary where possible",
                "Break up long paragraphs"
            ])

        return improvements

    def _generate_implementation_notes(self, schema_type: str) -> List[str]:
        """Generate implementation notes for schema type."""
        notes = {
            "Organization": [
                "Place in <head> section of your website",
                "Ensure all contact information is accurate",
                "Update logo URL when available"
            ],
            "LocalBusiness": [
                "Verify address format with Google My Business",
                "Include opening hours if applicable",
                "Add price range information if relevant"
            ],
            "FAQ": [
                "Place on pages with frequently asked questions",
                "Keep answers concise but informative",
                "Update questions based on customer inquiries"
            ]
        }

        return notes.get(schema_type, ["Place in <head> section", "Validate with Google's Rich Results Test"])

    def _get_validation_requirements(self, schema_type: str) -> List[str]:
        """Get validation requirements for schema type."""
        requirements = {
            "Organization": ["name", "url"],
            "LocalBusiness": ["name", "address", "telephone"],
            "FAQ": ["mainEntity with at least one question"]
        }

        return requirements.get(schema_type, ["@context", "@type"])

    def _extract_business_name(self, website_data: WebsiteData, business_info: Optional[BusinessInfo] = None) -> Optional[str]:
        """Extract business name from various sources."""
        if business_info and business_info.name:
            return business_info.name

        if website_data.title:
            # Clean up title - remove common suffixes
            title = website_data.title.split(' | ')[0].split(' - ')[0].strip()
            if title and len(title) > 2:
                return title

        # Try from metadata
        if "business_name" in website_data.metadata:
            return website_data.metadata["business_name"]

        # Fallback to domain name
        if website_data.url:
            domain = str(website_data.url).replace('https://', '').replace('http://', '').split('.')[0]
            return domain.replace('www', '').title()

        return None