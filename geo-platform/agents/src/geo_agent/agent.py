"""
Main GEO agent class for accuracy optimization.
Focuses on data consistency validation, business information accuracy,
and canonical data creation across multiple sources.
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
import difflib
from bs4 import BeautifulSoup

from ..shared.base_agent import BaseAgent
from ..shared.models import (
    WebsiteData, AgentResponse, AnalysisResult, AgentType,
    PriorityLevel, ImpactLevel, EffortLevel, BusinessInfo
)
from ..shared.llm_client import LLMClient
from .analyzer import GEOAnalyzer
from .generator import GEOGenerator
from .validator import GEOValidator


class GEOAgent(BaseAgent):
    """
    GEO Agent for Accuracy Optimization.
    
    Analyzes websites for data accuracy and consistency through:
    - Business information validation across pages
    - Contact information consistency checks
    - Data quality scoring and canonical data creation
    - Cross-reference validation with external sources
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("GEO Agent", llm_client)
        self.analyzer = GEOAnalyzer(llm_client)
        self.generator = GEOGenerator(llm_client)
        self.validator = GEOValidator(llm_client)
        self.data_validators = self._initialize_validators()
        
    def get_agent_type(self) -> str:
        return AgentType.GEO
    
    async def analyze(self, website_data: WebsiteData, client_input: Dict[str, Any] = None) -> AgentResponse:
        """
        Analyze website for data accuracy and consistency using modular components.
        
        Args:
            website_data: Website data to analyze
            client_input: Optional client input data for enhanced analysis
            
        Returns:
            AgentResponse with accuracy optimization recommendations
        """
        start_time = time.time()
        self._log_analysis_start(str(website_data.url))
        
        try:
            # Use the new analyzer for comprehensive business information analysis
            business_analysis = self.analyzer.analyze_business_information(website_data)
            contact_analysis = self.analyzer.analyze_contact_accuracy(website_data)
            location_analysis = self.analyzer.analyze_location_accuracy(website_data)
            credibility_analysis = self.analyzer.analyze_business_credibility(website_data)
            
            # Generate standardized business data and improvements
            business_data = self.generator.generate_business_data(business_analysis, client_input)
            nap_standardization = self.generator.generate_nap_standardization(business_analysis)
            contact_optimization = self.generator.generate_contact_optimization(contact_analysis)
            local_business_schema = self.generator.generate_local_business_schema(business_analysis, client_input)
            accuracy_corrections = self.generator.generate_accuracy_corrections(business_analysis)
            verification_checklist = self.generator.generate_verification_checklist(business_analysis)
            
            # Validate all generated content
            business_validation = self.validator.validate_business_data(business_data)
            nap_validation = self.validator.validate_nap_consistency(nap_standardization)
            contact_validation = self.validator.validate_contact_optimization(contact_optimization)
            schema_validation = self.validator.validate_local_business_schema(local_business_schema)
            corrections_validation = self.validator.validate_accuracy_corrections(accuracy_corrections)
            checklist_validation = self.validator.validate_verification_checklist(verification_checklist)
            
            # Check overall implementation readiness
            all_generated_content = {
                "business_data": business_validation,
                "nap_standardization": nap_validation,
                "contact_optimization": contact_validation,
                "local_business_schema": schema_validation,
                "accuracy_corrections": corrections_validation,
                "verification_checklist": checklist_validation
            }
            implementation_readiness = self.validator.validate_implementation_readiness(all_generated_content)
            
            # Convert analysis results to AnalysisResult format for compatibility
            results = self._convert_to_analysis_results(
                business_analysis, contact_analysis, location_analysis, credibility_analysis,
                business_data, nap_standardization, contact_optimization, local_business_schema,
                accuracy_corrections, verification_checklist, implementation_readiness
            )
            
            processing_time = time.time() - start_time
            confidence = implementation_readiness.get("readiness_score", 0.0)
            
            self._log_analysis_complete(str(website_data.url), len(results), confidence)
            
            return self._create_response(
                results=results,
                confidence=confidence,
                processing_time=processing_time,
                metadata={
                    "business_analysis": business_analysis,
                    "contact_analysis": contact_analysis,
                    "location_analysis": location_analysis,
                    "credibility_analysis": credibility_analysis,
                    "generated_content": all_generated_content,
                    "implementation_readiness": implementation_readiness,
                    "validation_summary": {
                        "business_valid": business_validation.get("is_valid", False),
                        "nap_consistent": nap_validation.get("is_consistent", False),
                        "schema_valid": schema_validation.get("is_valid", False),
                        "ready_for_implementation": implementation_readiness.get("ready_for_implementation", False)
                    }
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
        start_time = time.time()
        self._log_analysis_start(str(website_data.url))
        
        try:
            results = []
            
            # Parse HTML content
            soup = BeautifulSoup(website_data.html_content, 'html.parser')
            
            # Extract business information from current page
            business_info = self._extract_business_information(soup, website_data)
            
            # 1. Business information consistency analysis
            consistency_results = await self._analyze_business_consistency(business_info, website_data)
            results.extend(consistency_results)
            
            # 2. Contact information validation
            contact_results = await self._validate_contact_information(business_info, soup)
            results.extend(contact_results)
            
            # 3. Data quality assessment
            quality_results = await self._assess_data_quality(business_info, website_data)
            results.extend(quality_results)
            
            # 4. External validation opportunities
            external_results = await self._identify_external_validation_opportunities(business_info)
            results.extend(external_results)
            
            # 5. Canonical data recommendations
            canonical_results = await self._generate_canonical_data_recommendations(business_info)
            results.extend(canonical_results)
            
            processing_time = time.time() - start_time
            confidence = self._calculate_overall_confidence(results)
            
            self._log_analysis_complete(str(website_data.url), len(results), confidence)
            
            return self._create_response(
                results=results,
                confidence=confidence,
                processing_time=processing_time,
                metadata={
                    "business_info_extracted": business_info.dict() if business_info else {},
                    "validation_categories": [
                        "business_consistency", "contact_validation", "data_quality",
                        "external_validation", "canonical_data"
                    ],
                    "data_completeness_score": self._calculate_data_completeness(business_info)
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
    
    def _extract_business_information(self, soup: BeautifulSoup, website_data: WebsiteData) -> BusinessInfo:
        """Extract business information from webpage."""
        business_info = BusinessInfo()
        
        # Extract business name
        business_info.name = self._extract_business_name(soup, website_data)
        
        # Extract contact information
        text_content = soup.get_text()
        
        # Phone number extraction
        phone_matches = re.findall(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', text_content)
        if phone_matches:
            phone = '-'.join(phone_matches[0])
            business_info.phone = f"({phone_matches[0][0]}) {phone_matches[0][1]}-{phone_matches[0][2]}"
        
        # Email extraction
        email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
        if email_matches:
            business_info.email = email_matches[0]
        
        # Address extraction (basic pattern)
        address_patterns = [
            r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Court|Ct)\b[^.]*(?:[A-Z]{2}\s+\d{5}|\d{5})',
            r'\b[A-Z][a-z]+\s+University\b[^.]*(?:[A-Z]{2}\s+\d{5}|\d{5})'
        ]
        
        for pattern in address_patterns:
            address_matches = re.findall(pattern, text_content, re.IGNORECASE)
            if address_matches:
                business_info.address = address_matches[0]
                break
        
        # Website URL
        business_info.website = str(website_data.url)
        
        # Extract social media links
        social_links = soup.find_all('a', href=True)
        social_media = {}
        
        for link in social_links:
            href = link['href']
            if 'linkedin.com' in href:
                social_media['linkedin'] = href
            elif 'instagram.com' in href:
                social_media['instagram'] = href
            elif 'facebook.com' in href:
                social_media['facebook'] = href
            elif 'twitter.com' in href or 'x.com' in href:
                social_media['twitter'] = href
        
        business_info.social_media = social_media
        
        # Calculate confidence based on extracted data
        confidence_factors = [
            1.0 if business_info.name else 0.0,
            1.0 if business_info.phone else 0.0,
            1.0 if business_info.email else 0.0,
            1.0 if business_info.address else 0.0,
            0.5 if business_info.social_media else 0.0
        ]
        
        business_info.confidence = sum(confidence_factors) / len(confidence_factors)
        
        return business_info
    
    async def _analyze_business_consistency(self, business_info: BusinessInfo, website_data: WebsiteData) -> List[AnalysisResult]:
        """Analyze business information consistency."""
        results = []
        
        # Check if critical business information is missing
        missing_info = []
        
        if not business_info.name:
            missing_info.append("Business name")
        if not business_info.phone:
            missing_info.append("Phone number")
        if not business_info.email:
            missing_info.append("Email address")
        if not business_info.address:
            missing_info.append("Physical address")
        
        if missing_info:
            results.append(AnalysisResult(
                id="missing_business_info",
                type="business_consistency",
                title="Missing Critical Business Information",
                description=f"Found {len(missing_info)} missing critical business information fields",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation=f"Add missing business information: {', '.join(missing_info)}",
                implementation_steps=[
                    "Add missing contact information to website",
                    "Ensure information is prominently displayed",
                    "Include contact details in footer or header",
                    "Add structured data markup for business info"
                ],
                confidence=0.9,
                metadata={
                    "missing_fields": missing_info,
                    "completeness_score": business_info.confidence
                }
            ))
        
        return results
    
    async def _validate_contact_information(self, business_info: BusinessInfo, soup: BeautifulSoup) -> List[AnalysisResult]:
        """Validate contact information accuracy and accessibility."""
        results = []
        
        # Check contact information accessibility
        accessibility_issues = []
        
        # Check if contact info is in multiple locations
        contact_locations = []
        
        # Look for contact info in common locations
        header = soup.find('header')
        footer = soup.find('footer')
        contact_page_indicators = soup.find_all(text=re.compile(r'contact', re.IGNORECASE))
        
        if header and (business_info.phone or business_info.email):
            contact_locations.append("header")
        if footer and (business_info.phone or business_info.email):
            contact_locations.append("footer")
        if contact_page_indicators:
            contact_locations.append("contact_page")
        
        if len(contact_locations) < 2:
            accessibility_issues.append("Contact information not prominently displayed")
        
        # Check for click-to-call/email functionality
        phone_links = soup.find_all('a', href=re.compile(r'^tel:'))
        email_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        
        if business_info.phone and not phone_links:
            accessibility_issues.append("Phone number not linked for click-to-call")
        
        if business_info.email and not email_links:
            accessibility_issues.append("Email not linked for click-to-email")
        
        if accessibility_issues:
            results.append(AnalysisResult(
                id="contact_accessibility",
                type="contact_validation",
                title="Contact Information Accessibility Issues",
                description="Contact information could be more accessible to users",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Improve contact information accessibility",
                implementation_steps=[
                    "Add contact info to header and footer",
                    "Make phone numbers clickable with tel: links",
                    "Make email addresses clickable with mailto: links",
                    "Create dedicated contact page",
                    "Add contact information to schema markup"
                ],
                confidence=0.8,
                metadata={
                    "accessibility_issues": accessibility_issues,
                    "contact_locations": contact_locations
                }
            ))
        
        return results
    
    async def _assess_data_quality(self, business_info: BusinessInfo, website_data: WebsiteData) -> List[AnalysisResult]:
        """Assess overall data quality and completeness."""
        results = []
        
        # Calculate data quality score
        quality_factors = {
            "name_quality": 1.0 if business_info.name and len(business_info.name) > 2 else 0.0,
            "phone_quality": 1.0 if business_info.phone and len(business_info.phone) >= 10 else 0.0,
            "email_quality": 1.0 if business_info.email and '@' in business_info.email else 0.0,
            "address_quality": 1.0 if business_info.address and len(business_info.address) > 10 else 0.0,
            "social_presence": 1.0 if business_info.social_media else 0.0,
            "website_quality": 1.0 if business_info.website else 0.0
        }
        
        overall_quality = sum(quality_factors.values()) / len(quality_factors)
        
        if overall_quality < 0.7:
            results.append(AnalysisResult(
                id="low_data_quality",
                type="data_quality",
                title="Low Data Quality Score",
                description=f"Overall data quality score is {overall_quality:.2f}/1.0, below recommended threshold",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Improve data completeness and quality",
                implementation_steps=[
                    "Complete missing business information fields",
                    "Validate existing contact information",
                    "Add social media links",
                    "Ensure information accuracy across all pages",
                    "Implement data validation procedures"
                ],
                confidence=0.9,
                metadata={
                    "quality_score": overall_quality,
                    "quality_factors": quality_factors,
                    "threshold": 0.7
                }
            ))
        
        return results
    
    async def _identify_external_validation_opportunities(self, business_info: BusinessInfo) -> List[AnalysisResult]:
        """Identify opportunities for external validation."""
        results = []
        
        external_opportunities = []
        
        # Check for Google My Business optimization opportunity
        if business_info.name and business_info.address:
            external_opportunities.append({
                "platform": "Google My Business",
                "description": "Verify and optimize Google My Business listing",
                "benefit": "Improved local search visibility"
            })
        
        # Check for social media validation
        if len(business_info.social_media) < 2:
            external_opportunities.append({
                "platform": "Social Media",
                "description": "Establish presence on major social platforms",
                "benefit": "Enhanced brand credibility and reach"
            })
        
        # Industry-specific opportunities
        if business_info.name and "consulting" in business_info.name.lower():
            external_opportunities.append({
                "platform": "LinkedIn Company Page",
                "description": "Create and optimize LinkedIn company presence",
                "benefit": "Professional network visibility"
            })
        
        if external_opportunities:
            results.append(AnalysisResult(
                id="external_validation_opportunities",
                type="external_validation",
                title="External Validation Opportunities",
                description=f"Found {len(external_opportunities)} opportunities for external platform validation",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.HIGH,
                recommendation="Establish and validate presence on external platforms",
                implementation_steps=[
                    "Claim and verify Google My Business listing",
                    "Create consistent social media profiles",
                    "Ensure NAP (Name, Address, Phone) consistency across platforms",
                    "Monitor and respond to reviews",
                    "Set up regular monitoring of external mentions"
                ],
                confidence=0.8,
                metadata={"opportunities": external_opportunities}
            ))
        
        return results
    
    async def _generate_canonical_data_recommendations(self, business_info: BusinessInfo) -> List[AnalysisResult]:
        """Generate recommendations for canonical data creation."""
        results = []
        
        if business_info.confidence > 0.5:  # Only if we have reasonable data
            canonical_recommendations = []
            
            # JSON-LD structured data
            canonical_recommendations.append({
                "type": "structured_data",
                "description": "Create canonical business data in JSON-LD format",
                "implementation": "Add Organization schema with verified business information"
            })
            
            # Contact page standardization
            if business_info.phone or business_info.email:
                canonical_recommendations.append({
                    "type": "contact_standardization",
                    "description": "Standardize contact information presentation",
                    "implementation": "Create consistent contact blocks across all pages"
                })
            
            if canonical_recommendations:
                results.append(AnalysisResult(
                    id="canonical_data_creation",
                    type="canonical_data",
                    title="Canonical Data Creation",
                    description="Establish canonical business data standards",
                    priority=PriorityLevel.MEDIUM,
                    impact=ImpactLevel.HIGH,
                    effort=EffortLevel.MEDIUM,
                    recommendation="Create and implement canonical business data standards",
                    implementation_steps=[
                        "Define canonical business information format",
                        "Implement JSON-LD structured data",
                        "Standardize contact information display",
                        "Create master data source/template",
                        "Implement data validation procedures"
                    ],
                    confidence=0.8,
                    metadata={
                        "recommendations": canonical_recommendations,
                        "business_data": business_info.dict()
                    }
                ))
        
        return results
    
    def _extract_business_name(self, soup: BeautifulSoup, website_data: WebsiteData) -> Optional[str]:
        """Extract business name from various sources."""
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            # Clean up title - remove common suffixes
            title = title_tag.string.split(' | ')[0].split(' - ')[0].strip()
            if title and len(title) > 2:
                return title
        
        # Try h1 tag
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text().strip():
            return h1_tag.get_text().strip()
        
        # Try meta property og:site_name
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            return og_site_name.get('content')
        
        # Fallback to domain name
        if website_data.url:
            domain = str(website_data.url).replace('https://', '').replace('http://', '').split('.')[0]
            return domain.replace('www', '').title()
        
        return None
    
    def _initialize_validators(self) -> Dict[str, Any]:
        """Initialize data validators."""
        return {
            "phone": re.compile(r'^\(\d{3}\)\s\d{3}-\d{4}$'),
            "email": re.compile(r'^[^@]+@[^@]+\.[^@]+$'),
            "url": re.compile(r'^https?://[^\s]+$')
        }
    
    def _calculate_data_completeness(self, business_info: Optional[BusinessInfo]) -> float:
        """Calculate data completeness score."""
        if not business_info:
            return 0.0
        
        fields = [
            business_info.name,
            business_info.phone,
            business_info.email,
            business_info.address,
            business_info.website
        ]
        
        complete_fields = sum(1 for field in fields if field)
        return complete_fields / len(fields)
    
    def _calculate_overall_confidence(self, results: List[AnalysisResult]) -> float:
        """Calculate overall confidence score based on results."""
        if not results:
            return 0.0
        
        total_confidence = sum(result.confidence for result in results)
        return min(total_confidence / len(results), 1.0)
    
    def _convert_to_analysis_results(self, *analysis_data) -> List[AnalysisResult]:
        """Convert new analysis format to AnalysisResult objects for compatibility."""
        results = []
        
        (business_analysis, contact_analysis, location_analysis, credibility_analysis,
         business_data, nap_standardization, contact_optimization, local_business_schema,
         accuracy_corrections, verification_checklist, implementation_readiness) = analysis_data
        
        # Business Analysis Results
        if business_analysis.get("accuracy_score", 0) < 0.7:
            results.append(AnalysisResult(
                id="business_accuracy_low",
                type="business_accuracy",
                title="Low Business Information Accuracy",
                description=f"Business information accuracy score is {business_analysis.get('accuracy_score', 0):.2f}/1.0",
                priority=PriorityLevel.HIGH if business_analysis.get("accuracy_score", 0) < 0.5 else PriorityLevel.MEDIUM,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Improve business information accuracy and completeness",
                implementation_steps=[
                    "Verify and standardize business name across all sources",
                    "Ensure NAP (Name, Address, Phone) consistency",
                    "Validate contact information accuracy",
                    "Complete missing business information fields"
                ],
                confidence=business_analysis.get("completeness_score", 0.0),
                metadata={"business_analysis": business_analysis}
            ))
        
        # NAP Consistency Results
        if not nap_standardization.get("is_consistent", True):
            results.append(AnalysisResult(
                id="nap_inconsistency",
                type="data_consistency",
                title="NAP Information Inconsistency",
                description="Name, Address, Phone information is inconsistent across sources",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Standardize NAP information across all platforms",
                implementation_steps=[
                    "Create standardized business name format",
                    "Standardize address format (USPS compliant)",
                    "Format phone numbers consistently",
                    "Update all online listings with consistent information"
                ],
                confidence=nap_standardization.get("consistency_score", 0.0),
                metadata={"nap_validation": nap_standardization}
            ))
        
        # Schema Markup Results
        if not local_business_schema.get("is_valid", True):
            results.append(AnalysisResult(
                id="invalid_schema_markup",
                type="structured_data",
                title="Invalid or Missing LocalBusiness Schema",
                description="LocalBusiness schema markup is missing or contains errors",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Implement valid LocalBusiness schema markup",
                implementation_steps=[
                    "Create LocalBusiness JSON-LD schema",
                    "Include required properties (name, address, telephone)",
                    "Add optional properties (openingHours, description, url)",
                    "Validate with Google Rich Results Test",
                    "Monitor for schema errors in Search Console"
                ],
                confidence=local_business_schema.get("schema_score", 0.0),
                metadata={"schema_validation": local_business_schema}
            ))
        
        # Contact Optimization Results
        contact_score = contact_optimization.get("optimization_score", 0.0)
        if contact_score < 0.8:
            results.append(AnalysisResult(
                id="contact_optimization_needed",
                type="contact_optimization",
                title="Contact Information Optimization Needed",
                description=f"Contact information optimization score is {contact_score:.2f}/1.0",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Optimize contact information presentation and accessibility",
                implementation_steps=[
                    "Make phone numbers clickable (tel: links)",
                    "Make email addresses clickable (mailto: links)",
                    "Add contact information to header and footer",
                    "Create dedicated contact page",
                    "Improve contact form accessibility"
                ],
                confidence=contact_score,
                metadata={"contact_optimization": contact_optimization}
            ))
        
        # Implementation Readiness Results
        if not implementation_readiness.get("ready_for_implementation", False):
            blocking_issues = implementation_readiness.get("blocking_issues", [])
            results.append(AnalysisResult(
                id="implementation_not_ready",
                type="implementation_readiness",
                title="Not Ready for Implementation",
                description=f"Found {len(blocking_issues)} blocking issues preventing implementation",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Resolve blocking issues before proceeding with implementation",
                implementation_steps=[
                    "Address validation errors",
                    "Resolve data consistency issues",
                    "Complete missing required information",
                    "Verify all generated content"
                ],
                confidence=implementation_readiness.get("readiness_score", 0.0),
                metadata={"blocking_issues": blocking_issues, "readiness": implementation_readiness}
            ))
        
        # If no major issues found, add a positive result
        if not results:
            results.append(AnalysisResult(
                id="geo_optimization_ready",
                type="optimization_ready",
                title="Ready for GEO Optimization",
                description="Business information is accurate and ready for optimization",
                priority=PriorityLevel.LOW,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Proceed with implementing generated optimizations",
                implementation_steps=[
                    "Implement generated schema markup",
                    "Apply NAP standardization",
                    "Deploy contact optimizations",
                    "Monitor implementation results"
                ],
                confidence=implementation_readiness.get("readiness_score", 1.0),
                metadata={"all_validations_passed": True}
            ))
        
        return results
    
    def _create_error_result(self, error_message: str) -> AnalysisResult:
        """Create an error result."""
        return AnalysisResult(
            id="analysis_error",
            type="error",
            title="Analysis Error",
            description=f"Error during GEO analysis: {error_message}",
            priority=PriorityLevel.LOW,
            impact=ImpactLevel.LOW,
            effort=EffortLevel.LOW,
            recommendation="Review error and retry analysis",
            confidence=0.0
        )
