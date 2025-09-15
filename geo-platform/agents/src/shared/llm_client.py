"""
LLM client for interacting with language models.
Real implementation using Anthropic's Claude API.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
import logging
from dotenv import load_dotenv
import anthropic
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()


class LLMClient:
    """
    LLM client for language model interactions using Anthropic's Claude.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.logger = logging.getLogger("geo.llm_client")
        
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Claude.
        
        Args:
            prompt: Input prompt for text generation
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Generated text response
        """
        try:
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            temperature = kwargs.get('temperature', self.temperature)
            
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            self.logger.info(f"LLM response generated successfully ({len(response_text)} chars)")
            return response_text
            
        except Exception as e:
            self.logger.error(f"LLM generation error: {str(e)}")
            raise
    
    async def analyze_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze content using Claude for specific analysis types.
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results as dictionary
        """
        try:
            prompt = self._build_analysis_prompt(content, analysis_type)
            response = await self.generate_text(prompt)
            
            # Try to parse as JSON, fallback to structured parsing
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return self._parse_analysis_response(response, analysis_type)
                
        except Exception as e:
            self.logger.error(f"Content analysis error: {str(e)}")
            return {
                "analysis_type": analysis_type,
                "error": str(e),
                "confidence": 0.0
            }
    
    async def extract_business_info(self, html_content: str) -> Dict[str, Any]:
        """
        Extract business information from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Extracted business information
        """
        prompt = f"""
        Analyze the following HTML content and extract business information. Return a JSON object with the following structure:

        {{
            "business_name": "extracted business name",
            "contact_info": {{
                "phone": "phone number if found",
                "email": "email address if found",
                "address": "physical address if found"
            }},
            "business_hours": "operating hours if found",
            "services": ["list", "of", "services"],
            "social_media": {{
                "facebook": "url if found",
                "linkedin": "url if found",
                "twitter": "url if found"
            }},
            "confidence_score": 0.95
        }}

        HTML Content:
        {html_content[:8000]}  # Limit content to avoid token limits

        Respond only with valid JSON.
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=2000)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Business info extraction error: {str(e)}")
            return {"error": str(e), "confidence_score": 0.0}
    
    async def generate_schema_markup(self, business_info: Dict[str, Any], schema_type: str = "LocalBusiness") -> Dict[str, Any]:
        """
        Generate schema markup based on business information.
        
        Args:
            business_info: Business information dictionary
            schema_type: Type of schema to generate
            
        Returns:
            Generated schema markup
        """
        prompt = f"""
        Generate JSON-LD schema markup for a {schema_type} based on the following business information:

        Business Information:
        {json.dumps(business_info, indent=2)}

        Requirements:
        - Use schema.org vocabulary
        - Include all available information
        - Ensure proper structure and syntax
        - Return only valid JSON-LD

        Generate schema markup:
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=1500)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Schema generation error: {str(e)}")
            return {"error": str(e)}
    
    async def validate_and_improve_content(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """
        Validate and suggest improvements for generated content.
        
        Args:
            content: Content to validate
            content_type: Type of content (schema, nap_data, etc.)
            
        Returns:
            Validation results with improvement suggestions
        """
        prompt = f"""
        Validate the following {content_type} and provide improvement suggestions:

        Content:
        {json.dumps(content, indent=2)}

        Analyze for:
        - Completeness
        - Accuracy
        - Best practices compliance
        - Missing required fields
        - Format consistency

        Return JSON with this structure:
        {{
            "is_valid": true/false,
            "validation_score": 0.85,
            "issues": ["list of issues found"],
            "suggestions": ["list of improvement suggestions"],
            "missing_fields": ["list of missing required fields"]
        }}
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=1000)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Content validation error: {str(e)}")
            return {
                "is_valid": False,
                "validation_score": 0.0,
                "error": str(e)
            }
    
    async def analyze_nap_consistency(self, nap_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze NAP (Name, Address, Phone) consistency across sources.
        
        Args:
            nap_data: List of NAP data from different sources
            
        Returns:
            Consistency analysis results
        """
        prompt = f"""
        Analyze the consistency of Name, Address, Phone (NAP) information across these sources:

        NAP Data:
        {json.dumps(nap_data, indent=2)}

        Evaluate:
        - Name consistency and standardization
        - Address format consistency
        - Phone number format consistency
        - Overall consistency score

        Return JSON with this structure:
        {{
            "consistency_score": 0.85,
            "name_issues": ["list of name inconsistencies"],
            "address_issues": ["list of address inconsistencies"],
            "phone_issues": ["list of phone inconsistencies"],
            "recommendations": ["standardization recommendations"]
        }}
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=1200)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"NAP consistency analysis error: {str(e)}")
            return {
                "consistency_score": 0.0,
                "error": str(e)
            }
    
    def _build_analysis_prompt(self, content: str, analysis_type: str) -> str:
        """Build analysis prompt based on type."""
        prompts = {
            "seo": f"Analyze this content for SEO optimization opportunities:\n\n{content}",
            "schema": f"Identify schema markup opportunities in this content:\n\n{content}",
            "business_info": f"Extract business information from this content:\n\n{content}",
            "contact_validation": f"Validate and analyze contact information in this content:\n\n{content}"
        }
        
        return prompts.get(analysis_type, f"Analyze this content for {analysis_type}:\n\n{content}")
    
    def _parse_analysis_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse non-JSON analysis response."""
        return {
            "analysis_type": analysis_type,
            "raw_response": response,
            "confidence": 0.7,
            "parsed": True
        }


# Convenience functions for common operations
async def extract_business_info_from_html(html_content: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to extract business info from HTML."""
    client = LLMClient(api_key=api_key)
    return await client.extract_business_info(html_content)

async def generate_local_business_schema(business_info: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to generate LocalBusiness schema."""
    client = LLMClient(api_key=api_key)
    return await client.generate_schema_markup(business_info, "LocalBusiness")

async def validate_generated_content(content: Dict[str, Any], content_type: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to validate generated content."""
    client = LLMClient(api_key=api_key)
    return await client.validate_and_improve_content(content, content_type)