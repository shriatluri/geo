"""
Client Input Processor - Processes client requirements and converts them to internal models.
"""

import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from .models import WebsiteData, BusinessInfo, ClientRequirements
from .llm_client import LLMClient


class ClientInputProcessor:
    """
    Processes various forms of client input and standardizes them into internal models.
    
    Handles:
    - Manual client input forms
    - Business information extraction
    - Website URL processing
    - Requirements validation
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    async def process_client_input(self, raw_input: Dict[str, Any]) -> ClientRequirements:
        """
        Process raw client input into standardized ClientRequirements.
        
        Args:
            raw_input: Raw client input dictionary
            
        Returns:
            ClientRequirements object with validated and processed data
        """
        # Validate basic required fields
        self._validate_required_fields(raw_input)
        
        # Extract and validate website URL
        website_url = self._process_website_url(raw_input.get("website_url", ""))
        
        # Process business information
        business_info = await self._process_business_info(raw_input.get("business_info", {}))
        
        # Process service requirements
        services_needed = self._process_service_requirements(raw_input.get("services", []))
        
        # Extract priority and timeline
        priority = raw_input.get("priority", "medium")
        timeline = raw_input.get("timeline", "standard")
        
        # Process additional requirements
        additional_requirements = raw_input.get("additional_requirements", "")
        
        # Validate platform access
        platform_access = self._process_platform_access(raw_input.get("platform_access", {}))
        
        return ClientRequirements(
            website_url=website_url,
            business_info=business_info,
            services_needed=services_needed,
            priority=priority,
            timeline=timeline,
            additional_requirements=additional_requirements,
            platform_access=platform_access,
            metadata={
                "processed_at": "2024-09-15",
                "input_source": "manual_form",
                "validation_status": "validated"
            }
        )
    
    async def enhance_with_website_analysis(self, client_requirements: ClientRequirements, website_data: WebsiteData) -> ClientRequirements:
        """
        Enhance client requirements with automatic website analysis.
        
        Args:
            client_requirements: Existing client requirements
            website_data: Analyzed website data
            
        Returns:
            Enhanced ClientRequirements with additional insights
        """
        if not self.llm_client:
            return client_requirements
        
        # Extract business info from website if not provided
        if not client_requirements.business_info or not client_requirements.business_info.name:
            enhanced_business_info = await self._extract_business_from_website(website_data)
            if enhanced_business_info:
                client_requirements.business_info = enhanced_business_info
        
        # Suggest additional services based on website analysis
        suggested_services = await self._suggest_additional_services(website_data, client_requirements.services_needed)
        if suggested_services:
            client_requirements.metadata["suggested_additional_services"] = suggested_services
        
        return client_requirements
    
    def _validate_required_fields(self, raw_input: Dict[str, Any]) -> None:
        """Validate that required fields are present."""
        required_fields = ["website_url"]
        
        for field in required_fields:
            if field not in raw_input or not raw_input[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
    
    def _process_website_url(self, url: str) -> str:
        """Process and validate website URL."""
        if not url:
            raise ValueError("Website URL is required")
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception:
            raise ValueError("Invalid URL format")
        
        return url
    
    async def _process_business_info(self, business_data: Dict[str, Any]) -> BusinessInfo:
        """Process business information from client input."""
        return BusinessInfo(
            name=business_data.get("name", ""),
            phone=business_data.get("phone", ""),
            email=business_data.get("email", ""),
            address=business_data.get("address", ""),
            business_hours=business_data.get("hours", ""),
            services=business_data.get("services", []),
            social_media={
                "facebook": business_data.get("facebook", ""),
                "linkedin": business_data.get("linkedin", ""),
                "twitter": business_data.get("twitter", ""),
                "instagram": business_data.get("instagram", "")
            }
        )
    
    def _process_service_requirements(self, services: List[str]) -> List[str]:
        """Process and standardize service requirements."""
        standard_services = {
            "visibility": ["aeo", "schema", "search_optimization"],
            "accuracy": ["geo", "nap_consistency", "business_info"],
            "actionability": ["geo_plus", "implementation", "monitoring"],
            "schema_markup": ["aeo"],
            "business_listings": ["geo"],
            "implementation": ["geo_plus"]
        }
        
        processed_services = []
        
        for service in services:
            service_lower = service.lower().strip()
            
            # Direct match
            if service_lower in ["aeo", "geo", "geo_plus"]:
                processed_services.append(service_lower)
            
            # Map common requests to services
            for category, agent_services in standard_services.items():
                if service_lower in category or any(s in service_lower for s in agent_services):
                    processed_services.extend(agent_services)
        
        # Remove duplicates and ensure at least AEO if nothing specified
        processed_services = list(set(processed_services))
        if not processed_services:
            processed_services = ["aeo"]  # Default service
        
        return processed_services
    
    def _process_platform_access(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process platform access information."""
        return {
            "squarespace": {
                "has_access": platform_data.get("squarespace_access", False),
                "login_provided": bool(platform_data.get("squarespace_login")),
                "admin_level": platform_data.get("squarespace_admin", False)
            },
            "other_platforms": platform_data.get("other_platforms", {}),
            "ftp_access": platform_data.get("ftp_access", False),
            "code_access": platform_data.get("code_access", False)
        }
    
    async def _extract_business_from_website(self, website_data: WebsiteData) -> Optional[BusinessInfo]:
        """Extract business information from website using LLM."""
        if not website_data.html_content:
            return None
        
        try:
            business_data = await self.llm_client.extract_business_info(website_data.html_content)
            
            return BusinessInfo(
                name=business_data.get("business_name", ""),
                phone=business_data.get("contact_info", {}).get("phone", ""),
                email=business_data.get("contact_info", {}).get("email", ""),
                address=business_data.get("contact_info", {}).get("address", ""),
                business_hours=business_data.get("business_hours", ""),
                services=business_data.get("services", []),
                social_media=business_data.get("social_media", {})
            )
        except Exception:
            return None
    
    async def _suggest_additional_services(self, website_data: WebsiteData, current_services: List[str]) -> List[str]:
        """Suggest additional services based on website analysis."""
        suggestions = []
        
        if not website_data.extracted_text:
            return suggestions
        
        content = website_data.extracted_text.lower()
        
        # Suggest AEO if not included and business content detected
        if "aeo" not in current_services:
            if any(word in content for word in ["business", "services", "about", "contact"]):
                suggestions.append("aeo")
        
        # Suggest GEO if location/contact info found
        if "geo" not in current_services:
            if any(word in content for word in ["address", "location", "phone", "email", "contact"]):
                suggestions.append("geo")
        
        # Suggest GEO+ if implementation needs detected
        if "geo_plus" not in current_services:
            if any(word in content for word in ["squarespace", "website", "update", "manage"]):
                suggestions.append("geo_plus")
        
        return suggestions


def create_sample_client_input() -> Dict[str, Any]:
    """Create a sample client input for testing purposes."""
    return {
        "website_url": "https://purdueagr.com/pif",
        "business_info": {
            "name": "Purdue Agricultural Innovation Foundation",
            "phone": "+1-765-494-6258",
            "email": "info@purdueagr.com",
            "address": "1435 Win Hentschel Blvd, West Lafayette, IN 47906",
            "hours": "Monday-Friday 8:00 AM - 5:00 PM",
            "services": ["Agricultural Innovation", "Research Programs", "Technology Transfer"],
            "facebook": "https://facebook.com/purdueagr",
            "linkedin": "https://linkedin.com/company/purdue-agr"
        },
        "services": ["visibility", "accuracy", "schema_markup"],
        "priority": "high",
        "timeline": "2_weeks",
        "additional_requirements": "Focus on improving search visibility for agricultural research programs and technology transfer services. Need to highlight partnership opportunities.",
        "platform_access": {
            "squarespace_access": True,
            "squarespace_login": "admin@purdueagr.com",
            "squarespace_admin": True,
            "code_access": True
        }
    }


async def process_sample_client() -> ClientRequirements:
    """Process sample client input for demonstration."""
    processor = ClientInputProcessor()
    sample_input = create_sample_client_input()
    return await processor.process_client_input(sample_input)