"""
GEO Agent Generator - Generates accurate business information and NAP data.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ..shared.models import WebsiteData, BusinessInfo
from ..shared.llm_client import LLMClient


class GEOGenerator:
    """
    Generates accurate business information and standardized data formats.
    
    Focuses on:
    - NAP (Name, Address, Phone) standardization
    - Business information normalization
    - Contact data optimization
    - Local business data generation
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.business_types = self._load_business_types()
        self.address_formats = self._load_address_formats()
        self.llm_client = llm_client or LLMClient()
    
    def generate_business_data(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate standardized business data based on analysis."""
        business_data = {
            "business_profile": self._generate_business_profile(analysis_result, client_input),
            "contact_information": self._generate_contact_data(analysis_result, client_input),
            "location_data": self._generate_location_data(analysis_result, client_input),
            "operating_hours": self._generate_operating_hours(analysis_result, client_input),
            "business_verification": self._generate_verification_data(analysis_result),
            "accuracy_improvements": self._generate_accuracy_improvements(analysis_result)
        }
        
        return business_data
    
    def generate_nap_standardization(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate standardized Name, Address, Phone data."""
        nap_standardization = {
            "standardized_name": self._standardize_business_name(analysis_result),
            "standardized_address": self._standardize_address(analysis_result),
            "standardized_phone": self._standardize_phone_numbers(analysis_result),
            "consistency_report": self._generate_consistency_report(analysis_result),
            "implementation_guidelines": self._generate_nap_guidelines()
        }
        
        return nap_standardization
    
    def generate_contact_optimization(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized contact information."""
        contact_optimization = {
            "primary_contact_methods": self._identify_primary_contacts(analysis_result),
            "contact_hierarchy": self._create_contact_hierarchy(analysis_result),
            "missing_contact_recommendations": self._recommend_missing_contacts(analysis_result),
            "contact_form_improvements": self._suggest_form_improvements(analysis_result),
            "social_media_optimization": self._optimize_social_presence(analysis_result)
        }
        
        return contact_optimization
    
    def generate_local_business_schema(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate LocalBusiness schema markup for accuracy."""
        business_name = self._extract_primary_business_name(analysis_result)
        contact_info = analysis_result.get("contact_information", {})
        location_data = analysis_result.get("location_data", {})
        
        # Base LocalBusiness schema
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_name or "Local Business",
        }
        
        # Add address if available
        address_data = self._extract_address_data(location_data)
        if address_data:
            schema["address"] = {
                "@type": "PostalAddress",
                **address_data
            }
        
        # Add contact information
        phones = contact_info.get("phones", [])
        if phones:
            schema["telephone"] = self._format_primary_phone(phones)
        
        emails = contact_info.get("emails", [])
        if emails:
            schema["email"] = self._select_primary_email(emails)
        
        # Add operating hours if available
        hours_data = analysis_result.get("business_hours", {})
        if hours_data and hours_data.get("structured_hours"):
            schema["openingHours"] = self._format_opening_hours(hours_data["structured_hours"])
        
        # Add business type if determinable
        business_type = self._determine_business_type(analysis_result, client_input)
        if business_type:
            schema["@type"] = business_type
        
        # Add additional properties from client input
        if client_input:
            schema.update(self._add_client_business_data(client_input))
        
        return {
            "schema_markup": schema,
            "implementation_notes": self._generate_schema_implementation_notes(),
            "validation_requirements": self._generate_schema_validation_requirements()
        }
    
    def generate_accuracy_corrections(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate corrections for identified accuracy issues."""
        corrections = {
            "name_corrections": self._generate_name_corrections(analysis_result),
            "address_corrections": self._generate_address_corrections(analysis_result),
            "phone_corrections": self._generate_phone_corrections(analysis_result),
            "email_corrections": self._generate_email_corrections(analysis_result),
            "hours_corrections": self._generate_hours_corrections(analysis_result),
            "priority_fixes": self._prioritize_corrections(analysis_result)
        }
        
        return corrections
    
    def generate_verification_checklist(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate verification checklist for business information."""
        checklist = {
            "critical_verifications": self._identify_critical_verifications(analysis_result),
            "recommended_verifications": self._identify_recommended_verifications(analysis_result),
            "verification_sources": self._suggest_verification_sources(),
            "verification_timeline": self._create_verification_timeline(),
            "automated_checks": self._suggest_automated_checks(analysis_result)
        }
        
        return checklist
    
    def _generate_business_profile(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate standardized business profile."""
        business_name_data = analysis_result.get("business_name", {})
        
        profile = {
            "legal_name": business_name_data.get("primary_name", ""),
            "display_name": self._generate_display_name(business_name_data, client_input),
            "business_type": self._determine_business_type(analysis_result, client_input),
            "industry": self._determine_industry(analysis_result, client_input),
            "description": self._generate_business_description(analysis_result, client_input),
            "established_date": self._extract_established_date(analysis_result, client_input),
            "confidence_score": business_name_data.get("confidence", 0.0)
        }
        
        return profile
    
    def _generate_contact_data(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate standardized contact data."""
        contact_info = analysis_result.get("contact_information", {})
        
        contact_data = {
            "primary_phone": self._select_primary_phone(contact_info.get("phones", [])),
            "secondary_phones": self._select_secondary_phones(contact_info.get("phones", [])),
            "primary_email": self._select_primary_email(contact_info.get("emails", [])),
            "contact_emails": self._categorize_emails(contact_info.get("emails", [])),
            "website": client_input.get("domain") if client_input else None,
            "contact_methods": self._rank_contact_methods(contact_info)
        }
        
        return contact_data
    
    def _generate_location_data(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate standardized location data."""
        location_info = analysis_result.get("location_data", {})
        
        location_data = {
            "primary_address": self._standardize_primary_address(location_info),
            "service_areas": self._standardize_service_areas(location_info),
            "geographic_coverage": self._determine_geographic_coverage(location_info),
            "location_type": self._determine_location_type(analysis_result, client_input),
            "coordinates": self._extract_coordinates(location_info)
        }
        
        return location_data
    
    def _generate_operating_hours(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate standardized operating hours."""
        hours_data = analysis_result.get("business_hours", {})
        
        operating_hours = {
            "regular_hours": self._standardize_regular_hours(hours_data),
            "special_hours": self._identify_special_hours(hours_data),
            "timezone": self._determine_timezone(analysis_result, client_input),
            "24_7_operation": self._check_24_7_operation(hours_data),
            "seasonal_variations": self._identify_seasonal_hours(hours_data)
        }
        
        return operating_hours
    
    def _generate_verification_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business verification data."""
        verification_data = {
            "verification_status": self._assess_verification_status(analysis_result),
            "verification_sources": self._identify_verification_sources(analysis_result),
            "confidence_indicators": self._identify_confidence_indicators(analysis_result),
            "red_flags": self._identify_verification_red_flags(analysis_result),
            "verification_score": self._calculate_verification_score(analysis_result)
        }
        
        return verification_data
    
    def _generate_accuracy_improvements(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate accuracy improvement recommendations."""
        improvements = {
            "high_priority": self._identify_high_priority_improvements(analysis_result),
            "medium_priority": self._identify_medium_priority_improvements(analysis_result),
            "low_priority": self._identify_low_priority_improvements(analysis_result),
            "implementation_order": self._determine_implementation_order(analysis_result),
            "expected_impact": self._assess_improvement_impact(analysis_result)
        }
        
        return improvements
    
    def _standardize_business_name(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize business name across all sources."""
        business_name_data = analysis_result.get("business_name", {})
        primary_name = business_name_data.get("primary_name", "")
        
        standardization = {
            "recommended_name": self._clean_business_name(primary_name),
            "legal_variations": self._generate_legal_variations(primary_name),
            "display_variations": self._generate_display_variations(primary_name),
            "seo_optimized_name": self._generate_seo_name(primary_name),
            "abbreviations": self._generate_name_abbreviations(primary_name)
        }
        
        return standardization
    
    def _standardize_address(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize address information."""
        location_data = analysis_result.get("location_data", {})
        addresses = location_data.get("addresses", [])
        
        if not addresses:
            return {"standardized_address": None, "recommendations": ["Add complete business address"]}
        
        primary_address = addresses[0] if isinstance(addresses, list) else addresses
        
        standardization = {
            "standardized_address": self._format_standard_address(primary_address),
            "usps_format": self._format_usps_address(primary_address),
            "google_format": self._format_google_address(primary_address),
            "components": self._parse_address_components(primary_address),
            "validation_status": self._validate_address_format(primary_address)
        }
        
        return standardization
    
    def _standardize_phone_numbers(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize phone number information."""
        contact_info = analysis_result.get("contact_information", {})
        phones = contact_info.get("phones", [])
        
        standardization = {
            "primary_phone": self._format_primary_phone(phones),
            "alternate_phones": self._format_alternate_phones(phones),
            "international_format": self._format_international_phones(phones),
            "click_to_call": self._format_click_to_call(phones),
            "validation_results": self._validate_phone_formats(phones)
        }
        
        return standardization
    
    def _generate_consistency_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NAP consistency report."""
        nap_data = analysis_result.get("nap_consistency", {})
        
        report = {
            "overall_consistency": nap_data.get("consistency_score", 0.0),
            "name_consistency": self._assess_name_consistency(nap_data),
            "address_consistency": self._assess_address_consistency(nap_data),
            "phone_consistency": self._assess_phone_consistency(nap_data),
            "inconsistency_details": nap_data.get("inconsistencies", []),
            "improvement_priority": self._prioritize_consistency_improvements(nap_data)
        }
        
        return report
    
    def _generate_nap_guidelines(self) -> Dict[str, Any]:
        """Generate NAP implementation guidelines."""
        return {
            "name_guidelines": [
                "Use consistent business name across all platforms",
                "Include legal entity type (LLC, Inc.) consistently",
                "Avoid unnecessary abbreviations in primary name",
                "Use proper capitalization and spacing"
            ],
            "address_guidelines": [
                "Use USPS standardized format",
                "Include suite/unit numbers where applicable",
                "Spell out directionals (North, South, East, West)",
                "Use proper abbreviations (St, Ave, Blvd)"
            ],
            "phone_guidelines": [
                "Use consistent format across platforms",
                "Include area code for all numbers",
                "Use local number for local business",
                "Format as (XXX) XXX-XXXX for US numbers"
            ],
            "consistency_checkpoints": [
                "Website footer and header",
                "Contact page",
                "Google Business Profile",
                "Social media profiles",
                "Directory listings"
            ]
        }
    
    # Helper methods for data processing and formatting
    def _extract_primary_business_name(self, analysis_result: Dict[str, Any]) -> str:
        """Extract primary business name from analysis."""
        business_name_data = analysis_result.get("business_name", {})
        return business_name_data.get("primary_name", "")
    
    def _extract_address_data(self, location_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract address data for schema markup."""
        primary_location = location_data.get("primary_location")
        if not primary_location:
            return {}
        
        # This would need more sophisticated address parsing
        return {
            "streetAddress": primary_location,
            "addressLocality": "City",
            "addressRegion": "State",
            "postalCode": "00000",
            "addressCountry": "US"
        }
    
    def _format_primary_phone(self, phones: List[str]) -> str:
        """Format primary phone number."""
        if not phones:
            return ""
        
        # Select the first valid phone number
        for phone in phones:
            formatted = self._format_phone_standard(phone)
            if formatted:
                return formatted
        
        return phones[0] if phones else ""
    
    def _select_primary_email(self, emails: List[str]) -> str:
        """Select primary email address."""
        if not emails:
            return ""
        
        # Prioritize general/info emails
        priority_patterns = ['info@', 'contact@', 'hello@', 'mail@']
        
        for pattern in priority_patterns:
            for email in emails:
                if email.lower().startswith(pattern):
                    return email
        
        # Return first email if no priority match
        return emails[0] if emails else ""
    
    def _format_opening_hours(self, structured_hours: Dict[str, Any]) -> List[str]:
        """Format opening hours for schema markup."""
        # This would need implementation based on structured_hours format
        return ["Mo-Fr 09:00-17:00"]  # Default format
    
    def _determine_business_type(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> str:
        """Determine schema.org business type."""
        if client_input and client_input.get("business_type"):
            return client_input["business_type"]
        
        # Analyze business patterns to determine type
        # This would need more sophisticated analysis
        return "LocalBusiness"
    
    def _add_client_business_data(self, client_input: Dict[str, Any]) -> Dict[str, str]:
        """Add additional business data from client input."""
        additional_data = {}
        
        if client_input.get("website"):
            additional_data["url"] = client_input["website"]
        
        if client_input.get("description"):
            additional_data["description"] = client_input["description"]
        
        return additional_data
    
    def _generate_schema_implementation_notes(self) -> List[str]:
        """Generate implementation notes for schema markup."""
        return [
            "Add JSON-LD to website header",
            "Validate with Google Rich Results Test",
            "Monitor Google Search Console for structured data issues",
            "Update schema when business information changes"
        ]
    
    def _generate_schema_validation_requirements(self) -> List[str]:
        """Generate schema validation requirements."""
        return [
            "Name must match Google Business Profile exactly",
            "Address must be complete and standardized",
            "Phone number must be local business number",
            "Opening hours must be current and accurate"
        ]
    
    def _format_phone_standard(self, phone: str) -> str:
        """Format phone to standard format."""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as (XXX) XXX-XXXX for 10-digit numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return ""
    
    def _load_business_types(self) -> Dict[str, str]:
        """Load business type mappings."""
        return {
            "restaurant": "Restaurant",
            "retail": "Store",
            "service": "LocalBusiness",
            "professional": "ProfessionalService",
            "medical": "MedicalOrganization",
            "legal": "LegalService"
        }
    
    def _load_address_formats(self) -> Dict[str, str]:
        """Load address format templates."""
        return {
            "us_standard": "{number} {street}, {city}, {state} {zip}",
            "us_extended": "{number} {street}, {unit}, {city}, {state} {zip}",
            "international": "{street}, {city}, {country} {postal_code}"
        }
    
    # Placeholder methods - would need full implementation
    def _generate_display_name(self, business_name_data: Dict[str, Any], client_input: Dict[str, Any] = None) -> str:
        return business_name_data.get("primary_name", "")
    
    def _determine_industry(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> str:
        return "Professional Services"
    
    def _generate_business_description(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> str:
        return ""
    
    def _extract_established_date(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> Optional[str]:
        return None
    
    def _select_secondary_phones(self, phones: List[str]) -> List[str]:
        return phones[1:] if len(phones) > 1 else []
    
    def _categorize_emails(self, emails: List[str]) -> Dict[str, List[str]]:
        return {"general": emails}
    
    def _rank_contact_methods(self, contact_info: Dict[str, Any]) -> List[str]:
        return ["phone", "email", "website"]
    
    def _standardize_primary_address(self, location_info: Dict[str, Any]) -> Optional[str]:
        return location_info.get("primary_location")
    
    def _standardize_service_areas(self, location_info: Dict[str, Any]) -> List[str]:
        return location_info.get("service_areas", [])
    
    def _determine_geographic_coverage(self, location_info: Dict[str, Any]) -> str:
        return "local"
    
    def _determine_location_type(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> str:
        return "physical"
    
    def _extract_coordinates(self, location_info: Dict[str, Any]) -> Optional[Dict[str, float]]:
        return None
    
    def _standardize_regular_hours(self, hours_data: Dict[str, Any]) -> Dict[str, str]:
        return {}
    
    def _identify_special_hours(self, hours_data: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _determine_timezone(self, analysis_result: Dict[str, Any], client_input: Dict[str, Any] = None) -> str:
        return "America/New_York"
    
    def _check_24_7_operation(self, hours_data: Dict[str, Any]) -> bool:
        return False
    
    def _identify_seasonal_hours(self, hours_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    def _assess_verification_status(self, analysis_result: Dict[str, Any]) -> str:
        return "pending"
    
    def _identify_verification_sources(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_confidence_indicators(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_verification_red_flags(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _calculate_verification_score(self, analysis_result: Dict[str, Any]) -> float:
        return 0.0
    
    def _identify_high_priority_improvements(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_medium_priority_improvements(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_low_priority_improvements(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _determine_implementation_order(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _assess_improvement_impact(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        return {}
    
    def _clean_business_name(self, name: str) -> str:
        return name.strip()
    
    def _generate_legal_variations(self, name: str) -> List[str]:
        return [name]
    
    def _generate_display_variations(self, name: str) -> List[str]:
        return [name]
    
    def _generate_seo_name(self, name: str) -> str:
        return name
    
    def _generate_name_abbreviations(self, name: str) -> List[str]:
        return []
    
    def _format_standard_address(self, address: str) -> str:
        return address
    
    def _format_usps_address(self, address: str) -> str:
        return address
    
    def _format_google_address(self, address: str) -> str:
        return address
    
    def _parse_address_components(self, address: str) -> Dict[str, str]:
        return {}
    
    def _validate_address_format(self, address: str) -> str:
        return "valid"
    
    def _format_alternate_phones(self, phones: List[str]) -> List[str]:
        return phones[1:] if len(phones) > 1 else []
    
    def _format_international_phones(self, phones: List[str]) -> List[str]:
        return phones
    
    def _format_click_to_call(self, phones: List[str]) -> List[str]:
        return [f"tel:{phone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')}" for phone in phones]
    
    def _validate_phone_formats(self, phones: List[str]) -> List[Dict[str, Any]]:
        return []
    
    def _assess_name_consistency(self, nap_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    def _assess_address_consistency(self, nap_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    def _assess_phone_consistency(self, nap_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    def _prioritize_consistency_improvements(self, nap_data: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_primary_contacts(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        return {}
    
    def _create_contact_hierarchy(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _recommend_missing_contacts(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _suggest_form_improvements(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _optimize_social_presence(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    def _generate_name_corrections(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _generate_address_corrections(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _generate_phone_corrections(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _generate_email_corrections(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _generate_hours_corrections(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
    
    def _prioritize_corrections(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_critical_verifications(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _identify_recommended_verifications(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []
    
    def _suggest_verification_sources(self) -> List[str]:
        return []
    
    def _create_verification_timeline(self) -> Dict[str, str]:
        return {}
    
    def _suggest_automated_checks(self, analysis_result: Dict[str, Any]) -> List[str]:
        return []