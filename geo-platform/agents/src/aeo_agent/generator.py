"""
AEO Agent Generator - Generates schema markup, meta tags, and optimization code.
"""

import json
from typing import Dict, Any, List, Optional
from ..shared.models import WebsiteData, BusinessInfo


class AEOGenerator:
    """
    Generates implementable solutions for visibility optimization.
    
    Creates:
    - JSON-LD schema markup
    - Optimized meta tags  
    - Structured data implementations
    - AI-friendly content structures
    """
    
    def __init__(self):
        self.schema_templates = self._load_schema_templates()
    
    def generate_schema_markup(self, schema_type: str, website_data: WebsiteData, business_info: Optional[BusinessInfo] = None) -> str:
        """Generate JSON-LD schema markup for specified type."""
        
        if schema_type == "Organization":
            return self._generate_organization_schema(website_data, business_info)
        elif schema_type == "LocalBusiness":
            return self._generate_local_business_schema(website_data, business_info)
        elif schema_type == "FAQ":
            return self._generate_faq_schema(website_data)
        else:
            return self._generate_basic_schema(schema_type, website_data)
    
    def generate_meta_tags(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate optimized meta tags."""
        meta_tags = {}
        
        # Generate optimized title
        business_name = self._extract_business_name(website_data)
        if business_name:
            title = f"{business_name} - {self._generate_title_suffix(website_data)}"
            meta_tags["title"] = self._truncate_title(title, 60)
        
        # Generate meta description
        meta_description = self._generate_meta_description(website_data, analysis)
        meta_tags["description"] = meta_description
        
        return meta_tags
    
    def generate_faq_schema(self, questions_and_answers: List[Dict[str, str]]) -> str:
        """Generate FAQ schema from Q&A pairs."""
        faq_entities = []
        
        for qa in questions_and_answers:
            faq_entities.append({
                "@type": "Question",
                "name": qa["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": qa["answer"]
                }
            })
        
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_entities
        }
        
        return json.dumps(faq_schema, indent=2)
    
    def generate_html_improvements(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate HTML structure improvements."""
        improvements = {}
        
        # Generate improved heading structure
        if "heading_structure" in analysis:
            improvements["headings"] = "Use single H1, then H2, H3 hierarchy"
        
        # Generate accessibility improvements
        improvements["accessibility"] = "Add alt text to images, ensure proper form labels"
        
        return improvements
    
    def _generate_organization_schema(self, website_data: WebsiteData, business_info: Optional[BusinessInfo]) -> str:
        """Generate Organization schema markup."""
        business_name = business_info.name if business_info else self._extract_business_name(website_data)
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": business_name or "Organization",
            "url": str(website_data.url),
            "description": website_data.meta_description or f"Website for {business_name}"
        }
        
        # Add contact information if available
        if business_info:
            if business_info.phone:
                schema["telephone"] = business_info.phone
            if business_info.email:
                schema["email"] = business_info.email
            if business_info.address:
                schema["address"] = {
                    "@type": "PostalAddress",
                    "streetAddress": business_info.address
                }
            if business_info.social_media:
                schema["sameAs"] = list(business_info.social_media.values())
        
        return json.dumps(schema, indent=2)
    
    def _generate_local_business_schema(self, website_data: WebsiteData, business_info: Optional[BusinessInfo]) -> str:
        """Generate LocalBusiness schema markup."""
        business_name = business_info.name if business_info else self._extract_business_name(website_data)
        
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_name or "Local Business",
            "url": str(website_data.url)
        }
        
        # Add required address if available
        if business_info and business_info.address:
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": business_info.address
            }
        
        # Add contact information
        if business_info:
            if business_info.phone:
                schema["telephone"] = business_info.phone
            if business_info.email:
                schema["email"] = business_info.email
        
        return json.dumps(schema, indent=2)
    
    def _generate_faq_schema(self, website_data: WebsiteData) -> str:
        """Generate basic FAQ schema template."""
        business_type = website_data.metadata.get("business_type", "")
        
        # Generate common questions based on business type
        common_questions = []
        if "consulting" in business_type:
            common_questions = [
                {
                    "question": "What services do you offer?",
                    "answer": "We provide comprehensive consulting services including strategic planning, market research, and business analysis."
                },
                {
                    "question": "How can I get started?",
                    "answer": "Contact us through our application form or email to discuss your specific needs and project requirements."
                }
            ]
        
        return self.generate_faq_schema(common_questions)
    
    def _generate_basic_schema(self, schema_type: str, website_data: WebsiteData) -> str:
        """Generate basic schema for unknown types."""
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": f"{schema_type} for {self._extract_business_name(website_data)}",
            "url": str(website_data.url)
        }
        
        return json.dumps(schema, indent=2)
    
    def _generate_meta_description(self, website_data: WebsiteData, analysis: Dict[str, Any]) -> str:
        """Generate optimized meta description."""
        business_name = self._extract_business_name(website_data)
        business_type = website_data.metadata.get("business_type", "")
        
        if "consulting" in business_type and business_name:
            description = f"{business_name} provides professional consulting services including strategic planning, market research, and business analysis. Contact us for expert solutions."
        else:
            description = f"{business_name or 'Professional services'} - Expert solutions and strategic guidance for your business needs. Get in touch to learn more about our services."
        
        return self._truncate_description(description, 160)
    
    def _extract_business_name(self, website_data: WebsiteData) -> Optional[str]:
        """Extract business name from website data."""
        if website_data.title:
            return website_data.title.split(' | ')[0].split(' - ')[0]
        return None
    
    def _generate_title_suffix(self, website_data: WebsiteData) -> str:
        """Generate appropriate title suffix based on business type."""
        business_type = website_data.metadata.get("business_type", "")
        
        if "consulting" in business_type:
            return "Professional Consulting Services"
        elif "education" in business_type:
            return "Educational Excellence"
        else:
            return "Professional Services"
    
    def _truncate_title(self, title: str, max_length: int) -> str:
        """Truncate title to specified length."""
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + "..."
    
    def _truncate_description(self, description: str, max_length: int) -> str:
        """Truncate description to specified length."""
        if len(description) <= max_length:
            return description
        return description[:max_length-3] + "..."
    
    def _load_schema_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load schema templates."""
        return {
            "Organization": {
                "required": ["name", "url"],
                "recommended": ["description", "contactPoint", "address", "logo"]
            },
            "LocalBusiness": {
                "required": ["name", "address", "telephone"],
                "recommended": ["openingHours", "priceRange", "image"]
            },
            "FAQ": {
                "required": ["mainEntity"],
                "recommended": ["acceptedAnswer"]
            }
        }
