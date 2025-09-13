"""
Main GEO+ agent class for actionability optimization.
Focuses on enabling AI agent interactions through API analysis,
form automation testing, and interaction pattern generation.
"""

import time
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

from ..shared.base_agent import BaseAgent
from ..shared.models import (
    WebsiteData, AgentResponse, AnalysisResult, AgentType,
    PriorityLevel, ImpactLevel, EffortLevel, APIEndpoint, FormData
)
from ..shared.llm_client import LLMClient


class GEOPlusAgent(BaseAgent):
    """
    GEO+ Agent for Actionability Optimization.
    
    Analyzes websites for AI agent interaction capabilities through:
    - API endpoint discovery and analysis
    - Form automation compatibility testing
    - Interaction pattern generation
    - Automation readiness assessment
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("GEO+ Agent", llm_client)
        self.api_analyzers = self._initialize_api_analyzers()
        self.form_testers = self._initialize_form_testers()
        
    def get_agent_type(self) -> str:
        return AgentType.GEO_PLUS
    
    async def analyze(self, website_data: WebsiteData) -> AgentResponse:
        """
        Analyze website for actionability and AI agent interaction capabilities.
        
        Args:
            website_data: Website data to analyze
            
        Returns:
            AgentResponse with actionability optimization recommendations
        """
        start_time = time.time()
        self._log_analysis_start(str(website_data.url))
        
        try:
            results = []
            
            # Parse HTML content
            soup = BeautifulSoup(website_data.html_content, 'html.parser')
            
            # 1. API endpoint analysis
            api_results = await self._analyze_api_endpoints(website_data, soup)
            results.extend(api_results)
            
            # 2. Form automation analysis
            form_results = await self._analyze_form_automation(soup, str(website_data.url))
            results.extend(form_results)
            
            # 3. Interaction pattern analysis
            interaction_results = await self._analyze_interaction_patterns(soup, website_data)
            results.extend(interaction_results)
            
            # 4. Contact form and conversion opportunities
            conversion_results = await self._analyze_conversion_opportunities(soup)
            results.extend(conversion_results)
            
            # 5. Automation readiness assessment
            automation_results = await self._assess_automation_readiness(website_data, soup)
            results.extend(automation_results)
            
            processing_time = time.time() - start_time
            confidence = self._calculate_overall_confidence(results)
            
            self._log_analysis_complete(str(website_data.url), len(results), confidence)
            
            return self._create_response(
                results=results,
                confidence=confidence,
                processing_time=processing_time,
                metadata={
                    "api_endpoints_found": len(website_data.metadata.get("api_endpoints", [])),
                    "forms_analyzed": len(soup.find_all('form')),
                    "automation_readiness": self._calculate_automation_readiness_score(results),
                    "analysis_categories": [
                        "api_endpoints", "form_automation", "interaction_patterns",
                        "conversion_opportunities", "automation_readiness"
                    ]
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
    
    async def _analyze_api_endpoints(self, website_data: WebsiteData, soup: BeautifulSoup) -> List[AnalysisResult]:
        """Analyze discovered API endpoints for AI agent compatibility."""
        results = []
        
        # Get API endpoints from crawler metadata
        api_endpoints = website_data.metadata.get("api_endpoints", [])
        
        if not api_endpoints:
            # Look for potential API indicators in the HTML
            api_indicators = self._find_api_indicators(soup)
            
            if api_indicators:
                results.append(AnalysisResult(
                    id="potential_api_discovery",
                    type="api_endpoints",
                    title="Potential API Endpoints Discovered",
                    description=f"Found {len(api_indicators)} potential API indicators that could be explored",
                    priority=PriorityLevel.MEDIUM,
                    impact=ImpactLevel.MEDIUM,
                    effort=EffortLevel.HIGH,
                    recommendation="Investigate potential API endpoints for automation opportunities",
                    implementation_steps=[
                        "Review JavaScript files for API endpoint references",
                        "Check for API documentation or developer sections",
                        "Test discovered endpoints for accessibility",
                        "Implement API interaction patterns"
                    ],
                    confidence=0.6,
                    metadata={"api_indicators": api_indicators}
                ))
            else:
                results.append(AnalysisResult(
                    id="no_api_endpoints",
                    type="api_endpoints",
                    title="No API Endpoints Available",
                    description="No API endpoints found for automated interactions",
                    priority=PriorityLevel.LOW,
                    impact=ImpactLevel.MEDIUM,
                    effort=EffortLevel.HIGH,
                    recommendation="Consider creating API endpoints for better automation support",
                    implementation_steps=[
                        "Evaluate business processes suitable for API exposure",
                        "Design REST API for key functionality",
                        "Implement API with proper authentication",
                        "Document API for external integrations"
                    ],
                    confidence=0.8,
                    metadata={"suggestion": "api_creation"}
                ))
        else:
            # Analyze existing API endpoints
            endpoint_analysis = self._analyze_existing_endpoints(api_endpoints)
            
            results.append(AnalysisResult(
                id="api_endpoint_analysis",
                type="api_endpoints",
                title="API Endpoints Analysis",
                description=f"Analyzed {len(api_endpoints)} API endpoints for automation compatibility",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Optimize API endpoints for AI agent interactions",
                implementation_steps=[
                    "Document API endpoints and parameters",
                    "Implement proper authentication mechanisms",
                    "Add rate limiting and error handling",
                    "Create OpenAPI/Swagger documentation"
                ],
                confidence=0.8,
                metadata=endpoint_analysis
            ))
        
        return results
    
    async def _analyze_form_automation(self, soup: BeautifulSoup, base_url: str) -> List[AnalysisResult]:
        """Analyze forms for automation compatibility."""
        results = []
        
        forms = soup.find_all('form')
        
        if not forms:
            results.append(AnalysisResult(
                id="no_forms_found",
                type="form_automation",
                title="No Forms Available for Automation",
                description="No forms found on the page for potential automation",
                priority=PriorityLevel.LOW,
                impact=ImpactLevel.LOW,
                effort=EffortLevel.MEDIUM,
                recommendation="Consider adding contact or interaction forms",
                implementation_steps=[
                    "Add contact form for user inquiries",
                    "Implement newsletter signup form",
                    "Create consultation request form",
                    "Ensure forms are automation-friendly"
                ],
                confidence=0.9
            ))
            return results
        
        automation_compatible_forms = 0
        form_analysis = []
        
        for i, form in enumerate(forms):
            form_data = self._analyze_single_form(form, i, base_url)
            form_analysis.append(form_data)
            
            if form_data["automation_score"] > 0.7:
                automation_compatible_forms += 1
        
        if automation_compatible_forms > 0:
            results.append(AnalysisResult(
                id="automation_ready_forms",
                type="form_automation",
                title="Automation-Ready Forms Detected",
                description=f"Found {automation_compatible_forms} forms compatible with automation",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation="Implement automated form interaction patterns",
                implementation_steps=[
                    "Create form interaction specifications",
                    "Implement automated form filling procedures",
                    "Add form validation and error handling",
                    "Test automation workflows"
                ],
                confidence=0.9,
                metadata={"compatible_forms": form_analysis}
            ))
        
        # Analyze form accessibility and usability
        accessibility_issues = self._assess_form_accessibility(forms)
        
        if accessibility_issues:
            results.append(AnalysisResult(
                id="form_accessibility_issues",
                type="form_automation",
                title="Form Accessibility Issues",
                description=f"Found {len(accessibility_issues)} accessibility issues that may impact automation",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                recommendation="Improve form accessibility for better automation compatibility",
                implementation_steps=[
                    "Add proper labels to all form fields",
                    "Implement clear field validation messages",
                    "Ensure forms work without JavaScript",
                    "Add ARIA labels for better accessibility"
                ],
                confidence=0.8,
                metadata={"accessibility_issues": accessibility_issues}
            ))
        
        return results
    
    async def _analyze_interaction_patterns(self, soup: BeautifulSoup, website_data: WebsiteData) -> List[AnalysisResult]:
        """Analyze available interaction patterns for AI agents."""
        results = []
        
        interaction_opportunities = []
        
        # Check for contact information interaction
        contact_info = self._extract_contact_interactions(soup)
        if contact_info:
            interaction_opportunities.extend(contact_info)
        
        # Check for booking/scheduling opportunities
        booking_patterns = self._identify_booking_patterns(soup)
        if booking_patterns:
            interaction_opportunities.extend(booking_patterns)
        
        # Check for information request patterns
        info_patterns = self._identify_information_patterns(soup)
        if info_patterns:
            interaction_opportunities.extend(info_patterns)
        
        # Check for social media interactions
        social_patterns = self._identify_social_interaction_patterns(soup)
        if social_patterns:
            interaction_opportunities.extend(social_patterns)
        
        if interaction_opportunities:
            results.append(AnalysisResult(
                id="interaction_patterns_available",
                type="interaction_patterns",
                title="AI Agent Interaction Opportunities",
                description=f"Identified {len(interaction_opportunities)} potential interaction patterns",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Implement structured interaction patterns for AI agents",
                implementation_steps=[
                    "Create standardized interaction protocols",
                    "Implement structured response formats",
                    "Add machine-readable interaction metadata",
                    "Test interaction patterns with AI agents"
                ],
                confidence=0.8,
                metadata={"interaction_patterns": interaction_opportunities}
            ))
        else:
            results.append(AnalysisResult(
                id="limited_interaction_patterns",
                type="interaction_patterns",
                title="Limited AI Agent Interaction Opportunities",
                description="Few structured interaction patterns available for AI agents",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.HIGH,
                recommendation="Develop structured interaction capabilities",
                implementation_steps=[
                    "Add contact forms with structured fields",
                    "Implement booking/scheduling systems",
                    "Create information request mechanisms",
                    "Add chatbot or AI assistant integration"
                ],
                confidence=0.7
            ))
        
        return results
    
    async def _analyze_conversion_opportunities(self, soup: BeautifulSoup) -> List[AnalysisResult]:
        """Analyze conversion opportunities for AI agent interactions."""
        results = []
        
        conversion_elements = []
        
        # Look for call-to-action buttons
        cta_buttons = soup.find_all(['button', 'a'], text=re.compile(r'(contact|call|email|schedule|book|apply|signup|subscribe)', re.IGNORECASE))
        if cta_buttons:
            conversion_elements.append({
                "type": "cta_buttons",
                "count": len(cta_buttons),
                "description": "Call-to-action buttons for user engagement"
            })
        
        # Look for contact forms
        contact_forms = soup.find_all('form')
        if contact_forms:
            conversion_elements.append({
                "type": "contact_forms", 
                "count": len(contact_forms),
                "description": "Contact forms for user inquiries"
            })
        
        # Look for phone numbers and email links
        tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        
        if tel_links or mailto_links:
            conversion_elements.append({
                "type": "direct_contact",
                "count": len(tel_links) + len(mailto_links),
                "description": "Direct contact links (phone/email)"
            })
        
        if conversion_elements:
            results.append(AnalysisResult(
                id="conversion_opportunities_available",
                type="conversion_opportunities",
                title="Conversion Opportunities for AI Agents",
                description=f"Found {len(conversion_elements)} types of conversion opportunities",
                priority=PriorityLevel.MEDIUM,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                recommendation="Optimize conversion elements for AI agent interactions",
                implementation_steps=[
                    "Add structured data to conversion elements",
                    "Implement clear conversion tracking",
                    "Create AI-friendly conversion pathways",
                    "Add conversion confirmation mechanisms"
                ],
                confidence=0.8,
                metadata={"conversion_elements": conversion_elements}
            ))
        else:
            results.append(AnalysisResult(
                id="limited_conversion_opportunities",
                type="conversion_opportunities",
                title="Limited Conversion Opportunities",
                description="Few clear conversion opportunities for AI agent interactions",
                priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                recommendation="Create clear conversion pathways for AI agents",
                implementation_steps=[
                    "Add prominent call-to-action elements",
                    "Implement contact forms with clear purposes",
                    "Create booking or scheduling systems",
                    "Add multiple contact methods (phone, email, form)"
                ],
                confidence=0.9
            ))
        
        return results
    
    async def _assess_automation_readiness(self, website_data: WebsiteData, soup: BeautifulSoup) -> List[AnalysisResult]:
        """Assess overall automation readiness of the website."""
        results = []
        
        readiness_factors = {
            "api_availability": 1.0 if website_data.metadata.get("api_endpoints") else 0.0,
            "form_presence": 1.0 if soup.find_all('form') else 0.0,
            "structured_data": 1.0 if soup.find_all('script', type='application/ld+json') else 0.0,
            "contact_mechanisms": 1.0 if (soup.find_all('a', href=re.compile(r'^(tel:|mailto:)')) or soup.find_all('form')) else 0.0,
            "mobile_friendly": 1.0 if website_data.metadata.get("mobile_friendly", False) else 0.0,
            "ssl_security": 1.0 if website_data.metadata.get("ssl_valid", False) else 0.0
        }
        
        overall_readiness = sum(readiness_factors.values()) / len(readiness_factors)
        
        if overall_readiness < 0.6:
            priority = PriorityLevel.HIGH
            impact = ImpactLevel.HIGH
            recommendation = "Significant improvements needed for automation readiness"
        elif overall_readiness < 0.8:
            priority = PriorityLevel.MEDIUM
            impact = ImpactLevel.MEDIUM
            recommendation = "Moderate improvements needed for better automation support"
        else:
            priority = PriorityLevel.LOW
            impact = ImpactLevel.LOW
            recommendation = "Good automation readiness - focus on optimization"
        
        results.append(AnalysisResult(
            id="automation_readiness_assessment",
            type="automation_readiness",
            title="Automation Readiness Assessment",
            description=f"Overall automation readiness score: {overall_readiness:.2f}/1.0",
            priority=priority,
            impact=impact,
            effort=EffortLevel.MEDIUM,
            recommendation=recommendation,
            implementation_steps=[
                "Improve low-scoring readiness factors",
                "Implement missing automation-friendly features",
                "Add structured data and clear interaction patterns",
                "Test automation workflows regularly"
            ],
            confidence=0.9,
            metadata={
                "readiness_score": overall_readiness,
                "readiness_factors": readiness_factors,
                "improvement_areas": [k for k, v in readiness_factors.items() if v < 1.0]
            }
        ))
        
        return results
    
    def _find_api_indicators(self, soup: BeautifulSoup) -> List[str]:
        """Find potential API indicators in HTML."""
        indicators = []
        
        # Look for JavaScript files that might contain API calls
        script_tags = soup.find_all('script', src=True)
        for script in script_tags:
            src = script.get('src', '')
            if any(keyword in src.lower() for keyword in ['api', 'rest', 'graphql', 'service']):
                indicators.append(f"Script reference: {src}")
        
        # Look for data attributes that might indicate API usage
        elements_with_data_api = soup.find_all(attrs={"data-api": True}) or soup.find_all(attrs={"data-endpoint": True})
        if elements_with_data_api:
            indicators.append(f"Elements with API data attributes: {len(elements_with_data_api)}")
        
        # Look for API-related text content
        api_text = soup.find_all(text=re.compile(r'api|endpoint|rest|graphql', re.IGNORECASE))
        if api_text:
            indicators.append(f"API-related text mentions: {len(api_text)}")
        
        return indicators
    
    def _analyze_existing_endpoints(self, api_endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze existing API endpoints."""
        analysis = {
            "total_endpoints": len(api_endpoints),
            "endpoint_types": {},
            "authentication_required": 0,
            "documented_endpoints": 0
        }
        
        for endpoint in api_endpoints:
            # Categorize by method
            method = endpoint.get("method", "GET")
            if method not in analysis["endpoint_types"]:
                analysis["endpoint_types"][method] = 0
            analysis["endpoint_types"][method] += 1
            
            # Check authentication
            if endpoint.get("authentication_required", False):
                analysis["authentication_required"] += 1
            
            # Check documentation
            if endpoint.get("documentation_url"):
                analysis["documented_endpoints"] += 1
        
        return analysis
    
    def _analyze_single_form(self, form: BeautifulSoup, index: int, base_url: str) -> Dict[str, Any]:
        """Analyze a single form for automation compatibility."""
        form_data = {
            "form_index": index,
            "action": form.get('action', ''),
            "method": form.get('method', 'GET').upper(),
            "fields": [],
            "automation_score": 0.0,
            "issues": []
        }
        
        # Analyze form fields
        fields = form.find_all(['input', 'select', 'textarea'])
        automation_score = 0.0
        total_fields = len(fields)
        
        for field in fields:
            field_data = {
                "tag": field.name,
                "type": field.get('type', 'text'),
                "name": field.get('name', ''),
                "id": field.get('id', ''),
                "required": field.get('required') is not None,
                "label": self._find_field_label(field, form)
            }
            form_data["fields"].append(field_data)
            
            # Score automation compatibility
            field_score = 0.0
            
            # Name attribute present
            if field_data["name"]:
                field_score += 0.3
            
            # ID attribute present
            if field_data["id"]:
                field_score += 0.2
            
            # Label present
            if field_data["label"]:
                field_score += 0.3
            
            # Field type is automation-friendly
            if field_data["type"] in ['text', 'email', 'tel', 'url', 'textarea', 'select']:
                field_score += 0.2
            
            automation_score += field_score
        
        # Calculate overall form automation score
        if total_fields > 0:
            form_data["automation_score"] = automation_score / total_fields
        
        # Check for common issues
        if not form_data["action"]:
            form_data["issues"].append("Missing form action")
        
        if total_fields == 0:
            form_data["issues"].append("No form fields found")
        
        missing_names = sum(1 for field in form_data["fields"] if not field["name"])
        if missing_names > 0:
            form_data["issues"].append(f"{missing_names} fields missing name attributes")
        
        return form_data
    
    def _find_field_label(self, field: BeautifulSoup, form: BeautifulSoup) -> Optional[str]:
        """Find label for a form field."""
        field_id = field.get('id')
        field_name = field.get('name')
        
        # Look for label with 'for' attribute
        if field_id:
            label = form.find('label', attrs={'for': field_id})
            if label:
                return label.get_text(strip=True)
        
        # Look for parent label
        label = field.find_parent('label')
        if label:
            return label.get_text(strip=True)
        
        # Look for nearby text
        previous = field.find_previous_sibling(text=True)
        if previous:
            return previous.strip()
        
        return None
    
    def _assess_form_accessibility(self, forms: List[BeautifulSoup]) -> List[str]:
        """Assess form accessibility issues."""
        issues = []
        
        for i, form in enumerate(forms):
            fields = form.find_all(['input', 'select', 'textarea'])
            
            for field in fields:
                field_type = field.get('type', 'text')
                field_name = field.get('name', '')
                field_id = field.get('id', '')
                
                # Check for missing name
                if not field_name:
                    issues.append(f"Form {i}: Field missing name attribute")
                
                # Check for missing ID
                if not field_id:
                    issues.append(f"Form {i}: Field missing ID attribute")
                
                # Check for missing label
                if not self._find_field_label(field, form):
                    issues.append(f"Form {i}: Field '{field_name or field_type}' missing label")
        
        return issues
    
    def _extract_contact_interactions(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract contact interaction opportunities."""
        interactions = []
        
        # Phone interactions
        tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
        if tel_links:
            interactions.append({
                "type": "phone_contact",
                "count": len(tel_links),
                "automation_potential": "high",
                "description": "Direct phone contact links"
            })
        
        # Email interactions
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        if mailto_links:
            interactions.append({
                "type": "email_contact",
                "count": len(mailto_links),
                "automation_potential": "high",
                "description": "Direct email contact links"
            })
        
        return interactions
    
    def _identify_booking_patterns(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify booking and scheduling patterns."""
        patterns = []
        
        # Look for booking-related text and elements
        booking_keywords = ['book', 'schedule', 'appointment', 'meeting', 'consultation']
        
        for keyword in booking_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            if elements:
                patterns.append({
                    "type": "booking_opportunity",
                    "keyword": keyword,
                    "mentions": len(elements),
                    "automation_potential": "medium",
                    "description": f"Potential {keyword} interactions"
                })
        
        return patterns
    
    def _identify_information_patterns(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify information request patterns."""
        patterns = []
        
        # Look for information request forms
        forms = soup.find_all('form')
        for form in forms:
            form_text = form.get_text().lower()
            if any(keyword in form_text for keyword in ['question', 'inquiry', 'information', 'contact']):
                patterns.append({
                    "type": "information_request",
                    "automation_potential": "high",
                    "description": "Information request form"
                })
        
        return patterns
    
    def _identify_social_interaction_patterns(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify social media interaction patterns."""
        patterns = []
        
        # Look for social media links
        social_platforms = ['linkedin', 'facebook', 'twitter', 'instagram', 'youtube']
        
        for platform in social_platforms:
            links = soup.find_all('a', href=re.compile(platform, re.IGNORECASE))
            if links:
                patterns.append({
                    "type": "social_media",
                    "platform": platform,
                    "count": len(links),
                    "automation_potential": "low",
                    "description": f"{platform.title()} social media links"
                })
        
        return patterns
    
    def _calculate_automation_readiness_score(self, results: List[AnalysisResult]) -> float:
        """Calculate overall automation readiness score."""
        if not results:
            return 0.0
        
        # Find automation readiness assessment result
        for result in results:
            if result.id == "automation_readiness_assessment":
                return result.metadata.get("readiness_score", 0.0)
        
        return 0.0
    
    def _initialize_api_analyzers(self) -> Dict[str, Any]:
        """Initialize API analyzers."""
        return {
            "endpoint_patterns": [
                r'/api/',
                r'/rest/',
                r'/graphql',
                r'/v\d+/',
                r'\.json$'
            ],
            "auth_patterns": [
                'authorization',
                'bearer',
                'api-key',
                'token'
            ]
        }
    
    def _initialize_form_testers(self) -> Dict[str, Any]:
        """Initialize form testing configurations."""
        return {
            "automation_friendly_types": [
                'text', 'email', 'tel', 'url', 'number',
                'password', 'textarea', 'select', 'radio', 'checkbox'
            ],
            "required_attributes": ['name', 'id'],
            "accessibility_requirements": ['label', 'aria-label', 'aria-labelledby']
        }
    
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
            description=f"Error during GEO+ analysis: {error_message}",
            priority=PriorityLevel.LOW,
            impact=ImpactLevel.LOW,
            effort=EffortLevel.LOW,
            recommendation="Review error and retry analysis",
            confidence=0.0
        )
