"""
Adapter to convert crawler output data to WebsiteData model.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from .models import WebsiteData, APIEndpoint, FormData, BusinessInfo


class CrawlerDataAdapter:
    """Adapter to convert crawler output to WebsiteData format."""
    
    def __init__(self, crawler_output_dir: str):
        self.output_dir = Path(crawler_output_dir)
        
    def load_summary_data(self) -> Dict[str, Any]:
        """Load summary.json from crawler output."""
        summary_path = self.output_dir / "summary.json"
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_api_endpoints(self) -> List[APIEndpoint]:
        """Load API endpoints from crawler output."""
        api_path = self.output_dir / "api_endpoints.json"
        endpoints = []
        
        if api_path.exists():
            with open(api_path, 'r') as f:
                data = json.load(f)
                
            for endpoint_data in data.get("discovered", []):
                endpoint = APIEndpoint(
                    url=endpoint_data.get("endpoint", ""),
                    method=endpoint_data.get("method", "GET"),
                    response_format=self._extract_response_format(
                        endpoint_data.get("content_type", "")
                    ),
                    authentication_required=self._requires_auth(endpoint_data),
                )
                endpoints.append(endpoint)
                
        return endpoints
    
    def load_health_data(self) -> Dict[str, Any]:
        """Load health check data."""
        # Find health check file in the crawler output directory
        health_files = list(self.output_dir.parent.parent.glob("health_checks/*_health.json"))
        
        if health_files:
            with open(health_files[0], 'r') as f:
                return json.load(f)
        return {}
    
    def convert_to_website_data(self, domain: str, page_content: str = "") -> WebsiteData:
        """Convert crawler output to WebsiteData model."""
        summary_data = self.load_summary_data()
        health_data = self.load_health_data()
        api_endpoints = self.load_api_endpoints()
        
        # Extract metadata from crawler output
        metadata = {
            "cms": summary_data.get("cms", ""),
            "pages_crawled": summary_data.get("pages_crawled", 0),
            "api_endpoints": [ep.dict() for ep in api_endpoints],
            "ssl_valid": health_data.get("ssl_valid", False),
            "mobile_friendly": health_data.get("mobile_friendly", False),
            "robots_txt_exists": health_data.get("robots_txt_exists", False),
            "response_time_ms": health_data.get("response_time_ms", 0),
            "sitemap_urls": health_data.get("sitemap_urls", [])
        }
        
        # return the website data model
        return WebsiteData(
            url=domain,
            html_content=page_content or f"<html><body>Content from {domain}</body></html>",
            title=f"Analysis for {domain}",
            meta_description=f"GEO analysis for {domain}",
            headers={"content-type": "text/html"},
            status_code=200,
            metadata=metadata
        )
    
    def extract_business_info_from_context(self, context_path: str) -> BusinessInfo:
        """Extract business information from context.md file."""
        context_file = Path(context_path)
        business_info = BusinessInfo(confidence=0.8)
        
        if context_file.exists():
            with open(context_file, 'r') as f:
                content = f.read()
                
            # Parse the context.md file to extract business information
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if '## 1. Required Inputs' in line:
                    current_section = 'required_inputs'
                elif '## 3. Contextual Details' in line:
                    current_section = 'contextual'
                elif line.startswith('### **Domain URL**'):
                    current_section = 'domain'
                elif line.startswith('### **CMS**'):
                    current_section = 'cms'
                elif line.startswith('### **Business Type**'):
                    current_section = 'business_type'
                elif line.startswith('### **Primary Goals**'):
                    current_section = 'goals'
                elif line.startswith('### **Target Audiences**'):
                    current_section = 'audiences'
                elif line.startswith('### **Conversion Actions**'):
                    current_section = 'conversions'
                
                # Extract domain URL
                if current_section == 'domain' and line.startswith('https://'):
                    business_info.website = line
                
                # Extract business name from context
                if 'PurdueTHINK' in line and not business_info.name:
                    business_info.name = "PurdueTHINK Consulting"
                    
        return business_info
    
    def _extract_response_format(self, content_type: str) -> str:
        """Extract response format from content type."""
        if 'json' in content_type.lower():
            return 'json'
        elif 'xml' in content_type.lower():
            return 'xml'
        elif 'javascript' in content_type.lower():
            return 'javascript'
        else:
            return 'unknown'
    
    def _requires_auth(self, endpoint_data: Dict[str, Any]) -> bool:
        """Determine if endpoint requires authentication."""
        # Simple heuristic - check for common auth indicators
        url = endpoint_data.get("endpoint", "").lower()
        return any(keyword in url for keyword in ["auth", "login", "api", "secure", "private"])
    
    @classmethod
    def from_client_docs(cls, client_name: str) -> 'CrawlerDataAdapter':
        """Create adapter from client docs directory."""
        base_path = Path("client docs/crawl_outputs") / client_name
        return cls(str(base_path))