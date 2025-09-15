"""
GEO+ Agent Analyzer - Analyzes website actionability and user interaction capabilities.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from ..shared.models import WebsiteData


class GeoPlusAnalyzer:
    """
    Analyzes website actionability and user interaction capabilities.
    
    Focuses on:
    - Form analysis and interaction capabilities
    - API endpoint discovery and evaluation
    - User engagement opportunities
    - Conversion path optimization
    - Interactive element assessment
    """
    
    def __init__(self):
        self.interaction_patterns = self._load_interaction_patterns()
        self.form_validators = self._load_form_validators()
    
    def analyze_actionability(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze website actionability and user interaction capabilities."""
        analysis_result = {
            "forms_analysis": self._analyze_forms(website_data),
            "api_capabilities": self._analyze_api_capabilities(website_data),
            "user_engagement": self._analyze_user_engagement(website_data),
            "conversion_paths": self._analyze_conversion_paths(website_data),
            "interactive_elements": self._analyze_interactive_elements(website_data),
            "actionability_score": 0.0,
            "interaction_quality": 0.0,
            "recommendations": [],
            "blocking_issues": []
        }
        
        # Calculate overall scores
        scores = self._calculate_actionability_scores(analysis_result)
        analysis_result.update(scores)
        
        return analysis_result
    
    def analyze_form_capabilities(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze form capabilities and interaction potential."""
        form_analysis = {
            "contact_forms": self._analyze_contact_forms(website_data),
            "lead_generation_forms": self._analyze_lead_generation_forms(website_data),
            "booking_forms": self._analyze_booking_forms(website_data),
            "subscription_forms": self._analyze_subscription_forms(website_data),
            "form_accessibility": self._analyze_form_accessibility(website_data),
            "form_validation": self._analyze_form_validation(website_data),
            "form_quality_score": 0.0,
            "improvement_opportunities": []
        }
        
        # Calculate form quality score
        form_analysis["form_quality_score"] = self._calculate_form_quality_score(form_analysis)
        
        return form_analysis
    
    def analyze_api_potential(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze API integration potential and capabilities."""
        api_analysis = {
            "discovered_endpoints": self._discover_api_endpoints(website_data),
            "ajax_interactions": self._analyze_ajax_interactions(website_data),
            "third_party_integrations": self._analyze_third_party_integrations(website_data),
            "data_submission_paths": self._analyze_data_submission_paths(website_data),
            "authentication_mechanisms": self._analyze_authentication_mechanisms(website_data),
            "api_readiness_score": 0.0,
            "integration_opportunities": []
        }
        
        # Calculate API readiness score
        api_analysis["api_readiness_score"] = self._calculate_api_readiness_score(api_analysis)
        
        return api_analysis
    
    def analyze_user_journey(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze user journey and conversion optimization opportunities."""
        journey_analysis = {
            "entry_points": self._identify_entry_points(website_data),
            "call_to_actions": self._analyze_call_to_actions(website_data),
            "conversion_funnels": self._identify_conversion_funnels(website_data),
            "user_flow_barriers": self._identify_user_flow_barriers(website_data),
            "engagement_triggers": self._identify_engagement_triggers(website_data),
            "journey_effectiveness": 0.0,
            "optimization_recommendations": []
        }
        
        # Calculate journey effectiveness
        journey_analysis["journey_effectiveness"] = self._calculate_journey_effectiveness(journey_analysis)
        
        return journey_analysis
    
    def analyze_interaction_quality(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze quality of interactive elements and user experience."""
        interaction_analysis = {
            "interactive_elements": self._catalog_interactive_elements(website_data),
            "usability_assessment": self._assess_usability(website_data),
            "accessibility_compliance": self._assess_accessibility_compliance(website_data),
            "mobile_interaction": self._analyze_mobile_interaction(website_data),
            "loading_performance": self._analyze_loading_performance(website_data),
            "interaction_score": 0.0,
            "quality_issues": []
        }
        
        # Calculate interaction score
        interaction_analysis["interaction_score"] = self._calculate_interaction_score(interaction_analysis)
        
        return interaction_analysis
    
    def _analyze_forms(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze forms on the website."""
        if not website_data.html_content:
            return {"forms_found": 0, "form_details": [], "form_types": []}
        
        soup = BeautifulSoup(website_data.html_content, 'html.parser')
        forms = soup.find_all('form')
        
        form_analysis = {
            "forms_found": len(forms),
            "form_details": [],
            "form_types": [],
            "form_quality": {}
        }
        
        for i, form in enumerate(forms):
            form_detail = {
                "form_id": form.get('id', f'form_{i}'),
                "action": form.get('action', ''),
                "method": form.get('method', 'GET').upper(),
                "fields": self._analyze_form_fields(form),
                "validation": self._check_form_validation(form),
                "accessibility": self._check_form_accessibility(form),
                "type": self._classify_form_type(form)
            }
            
            form_analysis["form_details"].append(form_detail)
            if form_detail["type"] not in form_analysis["form_types"]:
                form_analysis["form_types"].append(form_detail["type"])
        
        # Assess overall form quality
        form_analysis["form_quality"] = self._assess_overall_form_quality(form_analysis["form_details"])
        
        return form_analysis
    
    def _analyze_api_capabilities(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze API capabilities and integration potential."""
        if not website_data.html_content:
            return {"api_indicators": [], "ajax_calls": 0, "third_party_apis": []}
        
        soup = BeautifulSoup(website_data.html_content, 'html.parser')
        
        api_capabilities = {
            "api_indicators": self._find_api_indicators(soup),
            "ajax_calls": self._count_ajax_calls(soup),
            "third_party_apis": self._identify_third_party_apis(soup),
            "data_attributes": self._find_data_attributes(soup),
            "rest_endpoints": self._discover_rest_endpoints(website_data),
            "graphql_endpoints": self._discover_graphql_endpoints(soup)
        }
        
        return api_capabilities
    
    def _analyze_user_engagement(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze user engagement elements and opportunities."""
        if not website_data.html_content:
            return {"engagement_elements": [], "engagement_score": 0.0}
        
        soup = BeautifulSoup(website_data.html_content, 'html.parser')
        
        engagement_analysis = {
            "call_to_actions": self._find_call_to_actions(soup),
            "contact_methods": self._find_contact_methods(soup),
            "social_engagement": self._find_social_engagement(soup),
            "newsletter_signup": self._find_newsletter_signup(soup),
            "booking_systems": self._find_booking_systems(soup),
            "chat_widgets": self._find_chat_widgets(soup),
            "engagement_score": 0.0
        }
        
        # Calculate engagement score
        engagement_analysis["engagement_score"] = self._calculate_engagement_score(engagement_analysis)
        
        return engagement_analysis
    
    def _analyze_conversion_paths(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze conversion paths and optimization opportunities."""
        if not website_data.html_content:
            return {"conversion_paths": [], "optimization_score": 0.0}
        
        soup = BeautifulSoup(website_data.html_content, 'html.parser')
        
        conversion_analysis = {
            "primary_conversions": self._identify_primary_conversions(soup),
            "secondary_conversions": self._identify_secondary_conversions(soup),
            "conversion_barriers": self._identify_conversion_barriers(soup),
            "trust_signals": self._identify_trust_signals(soup),
            "urgency_indicators": self._identify_urgency_indicators(soup),
            "conversion_optimization_score": 0.0
        }
        
        # Calculate conversion optimization score
        conversion_analysis["conversion_optimization_score"] = self._calculate_conversion_score(conversion_analysis)
        
        return conversion_analysis
    
    def _analyze_interactive_elements(self, website_data: WebsiteData) -> Dict[str, Any]:
        """Analyze interactive elements and user interface quality."""
        if not website_data.html_content:
            return {"interactive_elements": [], "interaction_quality": 0.0}
        
        soup = BeautifulSoup(website_data.html_content, 'html.parser')
        
        interactive_analysis = {
            "buttons": self._analyze_buttons(soup),
            "links": self._analyze_links(soup),
            "modals": self._analyze_modals(soup),
            "dropdowns": self._analyze_dropdowns(soup),
            "sliders": self._analyze_sliders(soup),
            "tabs": self._analyze_tabs(soup),
            "accordions": self._analyze_accordions(soup),
            "media_elements": self._analyze_media_elements(soup),
            "interaction_quality": 0.0
        }
        
        # Calculate interaction quality
        interactive_analysis["interaction_quality"] = self._calculate_interaction_quality(interactive_analysis)
        
        return interactive_analysis
    
    def _analyze_form_fields(self, form) -> Dict[str, Any]:
        """Analyze fields within a form."""
        fields = form.find_all(['input', 'textarea', 'select'])
        
        field_analysis = {
            "total_fields": len(fields),
            "field_types": {},
            "required_fields": 0,
            "labeled_fields": 0,
            "field_details": []
        }
        
        for field in fields:
            field_type = field.get('type', field.name)
            field_analysis["field_types"][field_type] = field_analysis["field_types"].get(field_type, 0) + 1
            
            if field.get('required') or 'required' in field.attrs:
                field_analysis["required_fields"] += 1
            
            # Check for labels
            field_id = field.get('id')
            if field_id and form.find('label', attrs={'for': field_id}):
                field_analysis["labeled_fields"] += 1
            
            field_detail = {
                "type": field_type,
                "name": field.get('name', ''),
                "id": field.get('id', ''),
                "required": bool(field.get('required') or 'required' in field.attrs),
                "placeholder": field.get('placeholder', ''),
                "has_label": bool(field_id and form.find('label', attrs={'for': field_id}))
            }
            field_analysis["field_details"].append(field_detail)
        
        return field_analysis
    
    def _classify_form_type(self, form) -> str:
        """Classify the type of form based on its fields and context."""
        form_text = form.get_text().lower()
        fields = form.find_all(['input', 'textarea', 'select'])
        field_names = [field.get('name', '').lower() for field in fields]
        field_types = [field.get('type', field.name).lower() for field in fields]
        
        # Contact form indicators
        if any(keyword in form_text for keyword in ['contact', 'message', 'inquiry']):
            return 'contact_form'
        
        # Email subscription indicators
        if any(keyword in form_text for keyword in ['subscribe', 'newsletter', 'email']):
            return 'subscription_form'
        
        # Booking/appointment indicators
        if any(keyword in form_text for keyword in ['book', 'appointment', 'schedule', 'reserve']):
            return 'booking_form'
        
        # Login/registration indicators
        if any(keyword in field_names for keyword in ['username', 'password', 'login']):
            return 'authentication_form'
        
        # Search form indicators
        if any(field_type == 'search' for field_type in field_types) or 'search' in form_text:
            return 'search_form'
        
        # Quote/lead generation indicators
        if any(keyword in form_text for keyword in ['quote', 'estimate', 'consultation']):
            return 'lead_generation_form'
        
        return 'general_form'
    
    def _find_api_indicators(self, soup) -> List[str]:
        """Find indicators of API usage in the HTML."""
        api_indicators = []
        
        # Look for AJAX/API related script tags
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.string or ''
            if any(keyword in script_content.lower() for keyword in ['fetch', 'ajax', 'xhr', 'api', 'endpoint']):
                api_indicators.append('JavaScript API calls detected')
                break
        
        # Look for data attributes that might indicate API endpoints
        elements_with_data = soup.find_all(attrs=lambda x: x and any(attr.startswith('data-') for attr in x.keys()))
        if elements_with_data:
            api_indicators.append('Data attributes found (potential API integration)')
        
        # Look for REST-like URLs in href attributes
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if re.search(r'/api/|/rest/|\.json|\.xml', href):
                api_indicators.append('REST-like endpoints in links')
                break
        
        return api_indicators
    
    def _count_ajax_calls(self, soup) -> int:
        """Count potential AJAX calls in scripts."""
        ajax_count = 0
        scripts = soup.find_all('script')
        
        for script in scripts:
            script_content = script.string or ''
            ajax_count += len(re.findall(r'\$\.ajax|\$\.get|\$\.post|fetch\(|XMLHttpRequest', script_content))
        
        return ajax_count
    
    def _identify_third_party_apis(self, soup) -> List[str]:
        """Identify third-party API integrations."""
        third_party_apis = []
        
        # Common third-party API patterns
        api_patterns = {
            'Google Maps': r'maps\.googleapis\.com|maps\.google\.com',
            'Google Analytics': r'google-analytics\.com|googletagmanager\.com',
            'Facebook': r'connect\.facebook\.net|graph\.facebook\.com',
            'Twitter': r'api\.twitter\.com|platform\.twitter\.com',
            'YouTube': r'youtube\.com|youtu\.be',
            'Stripe': r'js\.stripe\.com|api\.stripe\.com',
            'PayPal': r'paypal\.com/sdk|paypalobjects\.com',
            'Mailchimp': r'mailchimp\.com|chimpstatic\.com',
            'Calendly': r'calendly\.com',
            'Intercom': r'intercom\.io',
            'Zendesk': r'zendesk\.com'
        }
        
        # Check scripts and links for third-party APIs
        all_sources = []
        all_sources.extend([script.get('src', '') for script in soup.find_all('script', src=True)])
        all_sources.extend([link.get('href', '') for link in soup.find_all('link', href=True)])
        
        for source in all_sources:
            for api_name, pattern in api_patterns.items():
                if re.search(pattern, source):
                    if api_name not in third_party_apis:
                        third_party_apis.append(api_name)
        
        return third_party_apis
    
    def _find_call_to_actions(self, soup) -> List[Dict[str, Any]]:
        """Find call-to-action elements on the page."""
        cta_elements = []
        
        # Common CTA patterns
        cta_patterns = [
            r'contact\s+us',
            r'get\s+started',
            r'learn\s+more',
            r'sign\s+up',
            r'book\s+now',
            r'schedule',
            r'call\s+now',
            r'get\s+quote',
            r'free\s+consultation',
            r'download',
            r'subscribe'
        ]
        
        # Look for buttons and links with CTA text
        cta_selectors = ['button', 'a', '[role="button"]', '.btn', '.cta', '.call-to-action']
        
        for selector in cta_selectors:
            elements = soup.select(selector)
            for element in elements:
                element_text = element.get_text().strip().lower()
                for pattern in cta_patterns:
                    if re.search(pattern, element_text):
                        cta_elements.append({
                            "text": element.get_text().strip(),
                            "type": element.name,
                            "href": element.get('href', ''),
                            "pattern_matched": pattern
                        })
                        break
        
        return cta_elements
    
    def _find_contact_methods(self, soup) -> Dict[str, bool]:
        """Find available contact methods."""
        contact_methods = {
            "phone": False,
            "email": False,
            "contact_form": False,
            "chat": False,
            "social_media": False,
            "address": False
        }
        
        page_text = soup.get_text()
        
        # Phone detection
        if re.search(r'\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\d{10}', page_text):
            contact_methods["phone"] = True
        
        # Email detection
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text):
            contact_methods["email"] = True
        
        # Contact form detection
        forms = soup.find_all('form')
        for form in forms:
            form_text = form.get_text().lower()
            if any(keyword in form_text for keyword in ['contact', 'message', 'inquiry']):
                contact_methods["contact_form"] = True
                break
        
        # Chat detection
        if soup.find_all(text=re.compile(r'chat|live support', re.I)):
            contact_methods["chat"] = True
        
        # Social media detection
        social_patterns = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']
        links = soup.find_all('a', href=True)
        for link in links:
            if any(pattern in link['href'] for pattern in social_patterns):
                contact_methods["social_media"] = True
                break
        
        # Address detection
        if re.search(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd)', page_text):
            contact_methods["address"] = True
        
        return contact_methods
    
    # Helper methods for scoring
    def _calculate_actionability_scores(self, analysis_result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall actionability scores."""
        scores = []
        
        # Form analysis score
        forms_analysis = analysis_result.get("forms_analysis", {})
        if forms_analysis.get("forms_found", 0) > 0:
            scores.append(min(forms_analysis.get("forms_found", 0) / 3.0, 1.0))
        else:
            scores.append(0.0)
        
        # API capabilities score
        api_capabilities = analysis_result.get("api_capabilities", {})
        api_score = min(len(api_capabilities.get("api_indicators", [])) / 3.0, 1.0)
        scores.append(api_score)
        
        # User engagement score
        user_engagement = analysis_result.get("user_engagement", {})
        engagement_score = user_engagement.get("engagement_score", 0.0)
        scores.append(engagement_score)
        
        # Interactive elements score
        interactive_elements = analysis_result.get("interactive_elements", {})
        interaction_score = interactive_elements.get("interaction_quality", 0.0)
        scores.append(interaction_score)
        
        return {
            "actionability_score": sum(scores) / len(scores) if scores else 0.0,
            "interaction_quality": interaction_score
        }
    
    def _calculate_engagement_score(self, engagement_analysis: Dict[str, Any]) -> float:
        """Calculate user engagement score."""
        engagement_factors = []
        
        # Call to actions
        cta_count = len(engagement_analysis.get("call_to_actions", []))
        engagement_factors.append(min(cta_count / 5.0, 1.0))
        
        # Contact methods
        contact_methods = engagement_analysis.get("contact_methods", {})
        contact_score = sum(1 for method in contact_methods.values() if method) / len(contact_methods)
        engagement_factors.append(contact_score)
        
        # Social engagement
        social_engagement = engagement_analysis.get("social_engagement", [])
        engagement_factors.append(min(len(social_engagement) / 3.0, 1.0))
        
        return sum(engagement_factors) / len(engagement_factors) if engagement_factors else 0.0
    
    def _calculate_interaction_quality(self, interactive_analysis: Dict[str, Any]) -> float:
        """Calculate interaction quality score."""
        quality_factors = []
        
        # Button quality
        buttons = interactive_analysis.get("buttons", [])
        quality_factors.append(min(len(buttons) / 10.0, 1.0))
        
        # Link quality
        links = interactive_analysis.get("links", [])
        quality_factors.append(min(len(links) / 20.0, 1.0))
        
        # Interactive components
        interactive_components = ['modals', 'dropdowns', 'sliders', 'tabs', 'accordions']
        component_count = sum(len(interactive_analysis.get(comp, [])) for comp in interactive_components)
        quality_factors.append(min(component_count / 5.0, 1.0))
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    # Placeholder methods for comprehensive analysis
    def _load_interaction_patterns(self) -> Dict[str, Any]:
        return {}
    
    def _load_form_validators(self) -> Dict[str, Any]:
        return {}
    
    def _analyze_contact_forms(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_lead_generation_forms(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_booking_forms(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_subscription_forms(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_form_accessibility(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_form_validation(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _calculate_form_quality_score(self, form_analysis: Dict[str, Any]) -> float:
        return 0.0
    
    def _discover_api_endpoints(self, website_data: WebsiteData) -> List[str]:
        return []
    
    def _analyze_ajax_interactions(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_third_party_integrations(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_data_submission_paths(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_authentication_mechanisms(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _calculate_api_readiness_score(self, api_analysis: Dict[str, Any]) -> float:
        return 0.0
    
    def _identify_entry_points(self, website_data: WebsiteData) -> List[str]:
        return []
    
    def _analyze_call_to_actions(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _identify_conversion_funnels(self, website_data: WebsiteData) -> List[Dict[str, Any]]:
        return []
    
    def _identify_user_flow_barriers(self, website_data: WebsiteData) -> List[str]:
        return []
    
    def _identify_engagement_triggers(self, website_data: WebsiteData) -> List[str]:
        return []
    
    def _calculate_journey_effectiveness(self, journey_analysis: Dict[str, Any]) -> float:
        return 0.0
    
    def _catalog_interactive_elements(self, website_data: WebsiteData) -> Dict[str, List]:
        return {}
    
    def _assess_usability(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _assess_accessibility_compliance(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_mobile_interaction(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _analyze_loading_performance(self, website_data: WebsiteData) -> Dict[str, Any]:
        return {}
    
    def _calculate_interaction_score(self, interaction_analysis: Dict[str, Any]) -> float:
        return 0.0
    
    def _check_form_validation(self, form) -> Dict[str, Any]:
        return {}
    
    def _check_form_accessibility(self, form) -> Dict[str, Any]:
        return {}
    
    def _assess_overall_form_quality(self, form_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}
    
    def _find_data_attributes(self, soup) -> List[str]:
        return []
    
    def _discover_rest_endpoints(self, website_data: WebsiteData) -> List[str]:
        return []
    
    def _discover_graphql_endpoints(self, soup) -> List[str]:
        return []
    
    def _find_newsletter_signup(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _find_booking_systems(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _find_chat_widgets(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _find_social_engagement(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _identify_primary_conversions(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _identify_secondary_conversions(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _identify_conversion_barriers(self, soup) -> List[str]:
        return []
    
    def _identify_trust_signals(self, soup) -> List[str]:
        return []
    
    def _identify_urgency_indicators(self, soup) -> List[str]:
        return []
    
    def _calculate_conversion_score(self, conversion_analysis: Dict[str, Any]) -> float:
        return 0.0
    
    def _analyze_buttons(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_links(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_modals(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_dropdowns(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_sliders(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_tabs(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_accordions(self, soup) -> List[Dict[str, Any]]:
        return []
    
    def _analyze_media_elements(self, soup) -> List[Dict[str, Any]]:
        return []