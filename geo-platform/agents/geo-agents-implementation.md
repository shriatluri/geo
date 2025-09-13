# GEO Agents Implementation Specification

## Overview

This document outlines the complete implementation specification for a 4-agent GEO (Generative Engine Optimization) system designed to optimize websites for AI search engines and agent interactions. The system consists of four specialized agents working in coordination to analyze, optimize, and enhance web content for maximum AI discoverability, accuracy, and actionability.

## System Architecture

```
Crawler Data Input
        ↓
   Coordinator Agent
   ↙     ↓     ↘
AEO Agent  GEO Agent  GEO+ Agent
(Visibility) (Accuracy) (Actionability)
   ↘     ↓     ↙
   Coordinator Agent
        ↓
  Final Output Plan
```

## Core Data Models

### CrawlerData
```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class CrawlerData(BaseModel):
    url: str
    title: Optional[str]
    meta_description: Optional[str]
    headers: Dict[str, str]
    content: str
    html: str
    structured_data: List[Dict[str, Any]]
    links: List[str]
    images: List[Dict[str, str]]
    forms: List[Dict[str, Any]]
    api_endpoints: List[str]
    timestamp: datetime
    page_type: Optional[str]  # homepage, product, contact, etc.
```

### AgentResult
```python
class AgentResult(BaseModel):
    agent_name: str
    status: str  # success, error, warning
    confidence_score: float  # 0.0 to 1.0
    recommendations: List[Dict[str, Any]]
    data_output: Dict[str, Any]
    execution_time: float
    errors: List[str]
    warnings: List[str]
```

### CoordinatedOutput
```python
class CoordinatedOutput(BaseModel):
    url: str
    priority_score: float
    implementation_plan: List[Dict[str, Any]]
    merged_recommendations: Dict[str, List[Dict[str, Any]]]
    conflicts_resolved: List[Dict[str, Any]]
    estimated_impact: Dict[str, float]
    timeline: Dict[str, str]
```

## Agent 1: AEO Agent (Visibility)

### Purpose
Optimize content discoverability by AI search engines through comprehensive schema markup, structured data generation, and content enhancement for AI-generated responses.

### Core Responsibilities
1. **Schema Analysis**: Analyze existing schema markup and identify gaps
2. **JSON-LD Generation**: Generate complete JSON-LD structured data for all page types
3. **AI Response Optimization**: Ensure content appears prominently in AI-generated responses
4. **Content Structure Enhancement**: Improve content hierarchy and semantic markup
5. **Knowledge Graph Integration**: Optimize for knowledge graph inclusion

### Input Requirements
- `CrawlerData` object containing page HTML, content, and existing structured data
- Page classification (homepage, product, service, contact, etc.)
- Business entity information (name, address, phone, etc.)

### Output Specifications
```python
class AEOAgentOutput(BaseModel):
    schema_gaps: List[Dict[str, Any]]
    generated_jsonld: List[Dict[str, Any]]
    content_optimizations: List[Dict[str, Any]]
    ai_response_targets: List[str]
    semantic_improvements: List[Dict[str, Any]]
    priority_recommendations: List[Dict[str, Any]]
```

### Technical Implementation

#### FastAPI Service Structure
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import List, Dict, Any

app = FastAPI(title="AEO Agent Service", version="1.0.0")

class AEOAgent:
    def __init__(self):
        self.schema_templates = self._load_schema_templates()
        self.ai_optimization_rules = self._load_ai_rules()
    
    def analyze_schema_gaps(self, crawler_data: CrawlerData) -> List[Dict[str, Any]]:
        """Identify missing or incomplete schema markup"""
        existing_schemas = self._extract_existing_schemas(crawler_data.structured_data)
        required_schemas = self._determine_required_schemas(crawler_data.page_type, crawler_data.content)
        gaps = []
        
        for schema_type in required_schemas:
            if schema_type not in existing_schemas:
                gaps.append({
                    "schema_type": schema_type,
                    "priority": "high",
                    "reason": f"Missing {schema_type} schema for {crawler_data.page_type} page",
                    "recommended_properties": self.schema_templates[schema_type]["required"]
                })
        
        return gaps
    
    def generate_jsonld(self, crawler_data: CrawlerData, business_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate complete JSON-LD structured data"""
        jsonld_objects = []
        
        # Generate Organization schema
        if crawler_data.page_type in ["homepage", "contact", "about"]:
            org_schema = self._generate_organization_schema(business_data, crawler_data)
            jsonld_objects.append(org_schema)
        
        # Generate WebPage schema
        webpage_schema = self._generate_webpage_schema(crawler_data)
        jsonld_objects.append(webpage_schema)
        
        # Generate page-specific schemas
        if crawler_data.page_type == "product":
            product_schema = self._generate_product_schema(crawler_data)
            jsonld_objects.append(product_schema)
        elif crawler_data.page_type == "service":
            service_schema = self._generate_service_schema(crawler_data)
            jsonld_objects.append(service_schema)
        
        return jsonld_objects
    
    def optimize_for_ai_responses(self, crawler_data: CrawlerData) -> List[Dict[str, Any]]:
        """Optimize content for AI-generated responses"""
        optimizations = []
        
        # Identify key information that should appear in AI responses
        key_info = self._extract_key_information(crawler_data.content)
        
        # Generate FAQ schema for common questions
        faq_schema = self._generate_faq_schema(key_info)
        if faq_schema:
            optimizations.append({
                "type": "faq_schema",
                "implementation": faq_schema,
                "priority": "medium",
                "impact": "Increases likelihood of appearing in AI Q&A responses"
            })
        
        # Suggest content restructuring for better AI parsing
        content_improvements = self._suggest_content_restructuring(crawler_data.content)
        optimizations.extend(content_improvements)
        
        return optimizations

@app.post("/analyze", response_model=AEOAgentOutput)
async def analyze_page(crawler_data: CrawlerData, business_data: Dict[str, Any]):
    try:
        agent = AEOAgent()
        
        schema_gaps = agent.analyze_schema_gaps(crawler_data)
        generated_jsonld = agent.generate_jsonld(crawler_data, business_data)
        content_optimizations = agent.optimize_for_ai_responses(crawler_data)
        
        # Generate AI response targets
        ai_targets = agent._generate_ai_targets(crawler_data.content)
        
        # Suggest semantic improvements
        semantic_improvements = agent._analyze_semantic_structure(crawler_data.html)
        
        # Prioritize recommendations
        priority_recommendations = agent._prioritize_recommendations(
            schema_gaps, content_optimizations, semantic_improvements
        )
        
        return AEOAgentOutput(
            schema_gaps=schema_gaps,
            generated_jsonld=generated_jsonld,
            content_optimizations=content_optimizations,
            ai_response_targets=ai_targets,
            semantic_improvements=semantic_improvements,
            priority_recommendations=priority_recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Agent 2: GEO Agent (Accuracy)

### Purpose
Ensure information accuracy and consistency across all web properties by cross-validating business data, detecting inconsistencies, and creating canonical business entity data.

### Core Responsibilities
1. **Data Consistency Validation**: Cross-validate business information across all pages
2. **Inconsistency Detection**: Identify discrepancies in contact info, pricing, and business details
3. **Canonical Data Creation**: Establish single source of truth for business entity data
4. **Quality Scoring**: Assign accuracy scores to different data elements
5. **Data Correction Recommendations**: Provide specific fixes for identified issues

### Input Requirements
- List of `CrawlerData` objects from multiple pages
- External business data sources (Google My Business, social profiles, etc.)
- Previous canonical data (if available)

### Output Specifications
```python
class GEOAgentOutput(BaseModel):
    consistency_report: Dict[str, Any]
    detected_inconsistencies: List[Dict[str, Any]]
    canonical_business_data: Dict[str, Any]
    accuracy_scores: Dict[str, float]
    correction_recommendations: List[Dict[str, Any]]
    data_confidence_levels: Dict[str, float]
```

### Technical Implementation

#### FastAPI Service Structure
```python
from fastapi import FastAPI
from typing import List
import difflib
from collections import Counter
import re

app = FastAPI(title="GEO Agent Service", version="1.0.0")

class GEOAgent:
    def __init__(self):
        self.data_validators = self._initialize_validators()
        self.canonicalization_rules = self._load_canonicalization_rules()
    
    def validate_consistency(self, crawler_data_list: List[CrawlerData]) -> Dict[str, Any]:
        """Cross-validate business data across multiple pages"""
        business_data_extracts = []
        
        for data in crawler_data_list:
            extracted = self._extract_business_data(data)
            business_data_extracts.append({
                "url": data.url,
                "data": extracted
            })
        
        consistency_report = {
            "total_pages": len(crawler_data_list),
            "data_fields_analyzed": [],
            "consistency_scores": {},
            "common_values": {},
            "outliers": {}
        }
        
        # Analyze each type of business data
        data_fields = ["business_name", "phone", "email", "address", "hours", "pricing"]
        
        for field in data_fields:
            field_values = [extract["data"].get(field) for extract in business_data_extracts if extract["data"].get(field)]
            
            if field_values:
                consistency_score = self._calculate_consistency_score(field_values)
                common_value = self._find_most_common_value(field_values)
                outliers = self._identify_outliers(field_values, common_value)
                
                consistency_report["data_fields_analyzed"].append(field)
                consistency_report["consistency_scores"][field] = consistency_score
                consistency_report["common_values"][field] = common_value
                consistency_report["outliers"][field] = outliers
        
        return consistency_report
    
    def detect_inconsistencies(self, crawler_data_list: List[CrawlerData]) -> List[Dict[str, Any]]:
        """Detect specific inconsistencies in business data"""
        inconsistencies = []
        
        # Extract business data from all pages
        all_business_data = {}
        for data in crawler_data_list:
            business_info = self._extract_business_data(data)
            all_business_data[data.url] = business_info
        
        # Check phone number inconsistencies
        phone_inconsistencies = self._check_phone_consistency(all_business_data)
        inconsistencies.extend(phone_inconsistencies)
        
        # Check address inconsistencies
        address_inconsistencies = self._check_address_consistency(all_business_data)
        inconsistencies.extend(address_inconsistencies)
        
        # Check pricing inconsistencies
        pricing_inconsistencies = self._check_pricing_consistency(all_business_data)
        inconsistencies.extend(pricing_inconsistencies)
        
        # Check business hours inconsistencies
        hours_inconsistencies = self._check_hours_consistency(all_business_data)
        inconsistencies.extend(hours_inconsistencies)
        
        return inconsistencies
    
    def create_canonical_data(self, crawler_data_list: List[CrawlerData], external_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Create canonical business entity data"""
        # Collect all business data variants
        collected_data = {}
        
        # Process crawler data
        for data in crawler_data_list:
            business_info = self._extract_business_data(data)
            for key, value in business_info.items():
                if key not in collected_data:
                    collected_data[key] = []
                collected_data[key].append({
                    "value": value,
                    "source": data.url,
                    "confidence": self._calculate_data_confidence(value, key)
                })
        
        # Add external source data
        for source, source_data in external_sources.items():
            for key, value in source_data.items():
                if key not in collected_data:
                    collected_data[key] = []
                collected_data[key].append({
                    "value": value,
                    "source": source,
                    "confidence": 0.9  # High confidence for external sources
                })
        
        # Create canonical values
        canonical_data = {}
        for field, variants in collected_data.items():
            canonical_value = self._determine_canonical_value(variants, field)
            canonical_data[field] = {
                "value": canonical_value["value"],
                "confidence": canonical_value["confidence"],
                "source": canonical_value["source"],
                "alternatives": [v for v in variants if v["value"] != canonical_value["value"]]
            }
        
        return canonical_data

@app.post("/analyze-accuracy", response_model=GEOAgentOutput)
async def analyze_accuracy(crawler_data_list: List[CrawlerData], external_sources: Dict[str, Any] = {}):
    try:
        agent = GEOAgent()
        
        consistency_report = agent.validate_consistency(crawler_data_list)
        inconsistencies = agent.detect_inconsistencies(crawler_data_list)
        canonical_data = agent.create_canonical_data(crawler_data_list, external_sources)
        
        # Calculate accuracy scores
        accuracy_scores = agent._calculate_accuracy_scores(consistency_report, inconsistencies)
        
        # Generate correction recommendations
        corrections = agent._generate_corrections(inconsistencies, canonical_data)
        
        # Calculate confidence levels
        confidence_levels = agent._calculate_confidence_levels(canonical_data)
        
        return GEOAgentOutput(
            consistency_report=consistency_report,
            detected_inconsistencies=inconsistencies,
            canonical_business_data=canonical_data,
            accuracy_scores=accuracy_scores,
            correction_recommendations=corrections,
            data_confidence_levels=confidence_levels
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Agent 3: GEO+ Agent (Actionability)

### Purpose
Enable AI agent interactions by analyzing API endpoints, testing form functionality for automation, and generating structured response formats for AI agent consumption.

### Core Responsibilities
1. **API Endpoint Analysis**: Discover and analyze available API endpoints
2. **Form Automation Testing**: Test forms for AI agent compatibility
3. **Interaction Pattern Generation**: Create structured formats for AI agent interactions
4. **Automation Readiness Assessment**: Evaluate how ready the site is for AI agent automation
5. **Integration Recommendations**: Suggest improvements for better AI agent integration

### Input Requirements
- `CrawlerData` object with forms and API endpoint information
- Site interaction requirements
- AI agent use case specifications

### Output Specifications
```python
class GEOPlusAgentOutput(BaseModel):
    api_analysis: Dict[str, Any]
    form_automation_results: List[Dict[str, Any]]
    interaction_patterns: List[Dict[str, Any]]
    automation_readiness_score: float
    integration_recommendations: List[Dict[str, Any]]
    structured_response_formats: Dict[str, Any]
```

### Technical Implementation

#### FastAPI Service Structure
```python
from fastapi import FastAPI
import requests
from typing import List, Dict, Any
import json
from urllib.parse import urljoin, urlparse

app = FastAPI(title="GEO+ Agent Service", version="1.0.0")

class GEOPlusAgent:
    def __init__(self):
        self.api_analyzers = self._initialize_api_analyzers()
        self.form_testers = self._initialize_form_testers()
    
    def analyze_api_endpoints(self, crawler_data: CrawlerData, base_url: str) -> Dict[str, Any]:
        """Analyze discovered API endpoints for AI agent compatibility"""
        api_analysis = {
            "discovered_endpoints": [],
            "endpoint_capabilities": {},
            "authentication_requirements": {},
            "rate_limits": {},
            "documentation_quality": {}
        }
        
        for endpoint in crawler_data.api_endpoints:
            full_url = urljoin(base_url, endpoint)
            
            # Test endpoint accessibility
            endpoint_info = self._test_endpoint_access(full_url)
            
            # Analyze endpoint capabilities
            capabilities = self._analyze_endpoint_capabilities(endpoint_info)
            
            # Check authentication requirements
            auth_requirements = self._check_authentication(full_url)
            
            # Assess documentation
            doc_quality = self._assess_api_documentation(endpoint_info)
            
            api_analysis["discovered_endpoints"].append({
                "endpoint": endpoint,
                "full_url": full_url,
                "status": endpoint_info["status"],
                "methods_supported": endpoint_info["methods"],
                "response_format": endpoint_info["content_type"]
            })
            
            api_analysis["endpoint_capabilities"][endpoint] = capabilities
            api_analysis["authentication_requirements"][endpoint] = auth_requirements
            api_analysis["documentation_quality"][endpoint] = doc_quality
        
        return api_analysis
    
    def test_form_automation(self, crawler_data: CrawlerData) -> List[Dict[str, Any]]:
        """Test forms for AI agent automation compatibility"""
        form_results = []
        
        for form in crawler_data.forms:
            form_analysis = {
                "form_id": form.get("id", "unnamed"),
                "action": form.get("action", ""),
                "method": form.get("method", "GET"),
                "fields": [],
                "automation_compatibility": {},
                "required_fields": [],
                "validation_rules": {},
                "success_indicators": []
            }
            
            # Analyze form fields
            for field in form.get("fields", []):
                field_analysis = self._analyze_form_field(field)
                form_analysis["fields"].append(field_analysis)
                
                if field_analysis.get("required", False):
                    form_analysis["required_fields"].append(field_analysis["name"])
            
            # Test automation compatibility
            automation_test = self._test_form_automation(form)
            form_analysis["automation_compatibility"] = automation_test
            
            # Identify validation rules
            validation_rules = self._extract_validation_rules(form)
            form_analysis["validation_rules"] = validation_rules
            
            # Find success indicators
            success_indicators = self._identify_success_indicators(form)
            form_analysis["success_indicators"] = success_indicators
            
            form_results.append(form_analysis)
        
        return form_results
    
    def generate_interaction_patterns(self, api_analysis: Dict[str, Any], form_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate structured interaction patterns for AI agents"""
        interaction_patterns = []
        
        # Generate API interaction patterns
        for endpoint_data in api_analysis["discovered_endpoints"]:
            if endpoint_data["status"] == "accessible":
                pattern = self._create_api_interaction_pattern(endpoint_data, api_analysis)
                interaction_patterns.append(pattern)
        
        # Generate form interaction patterns
        for form_result in form_results:
            if form_result["automation_compatibility"]["score"] > 0.7:
                pattern = self._create_form_interaction_pattern(form_result)
                interaction_patterns.append(pattern)
        
        # Generate composite interaction patterns
        composite_patterns = self._create_composite_patterns(api_analysis, form_results)
        interaction_patterns.extend(composite_patterns)
        
        return interaction_patterns
    
    def assess_automation_readiness(self, api_analysis: Dict[str, Any], form_results: List[Dict[str, Any]]) -> float:
        """Calculate overall automation readiness score"""
        scores = []
        
        # API readiness score
        if api_analysis["discovered_endpoints"]:
            api_scores = [
                self._calculate_endpoint_score(endpoint, api_analysis)
                for endpoint in api_analysis["discovered_endpoints"]
            ]
            api_readiness = sum(api_scores) / len(api_scores)
        else:
            api_readiness = 0.3  # Base score for sites without APIs
        
        scores.append(("api_readiness", api_readiness, 0.4))  # 40% weight
        
        # Form automation readiness
        if form_results:
            form_scores = [form["automation_compatibility"]["score"] for form in form_results]
            form_readiness = sum(form_scores) / len(form_scores)
        else:
            form_readiness = 0.5  # Neutral score for sites without forms
        
        scores.append(("form_readiness", form_readiness, 0.3))  # 30% weight
        
        # Documentation and discoverability
        doc_score = self._calculate_documentation_score(api_analysis)
        scores.append(("documentation", doc_score, 0.2))  # 20% weight
        
        # Security and authentication
        security_score = self._calculate_security_score(api_analysis, form_results)
        scores.append(("security", security_score, 0.1))  # 10% weight
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        return round(total_score, 2)

@app.post("/analyze-actionability", response_model=GEOPlusAgentOutput)
async def analyze_actionability(crawler_data: CrawlerData, base_url: str, use_cases: List[str] = []):
    try:
        agent = GEOPlusAgent()
        
        api_analysis = agent.analyze_api_endpoints(crawler_data, base_url)
        form_automation_results = agent.test_form_automation(crawler_data)
        interaction_patterns = agent.generate_interaction_patterns(api_analysis, form_automation_results)
        automation_readiness_score = agent.assess_automation_readiness(api_analysis, form_automation_results)
        
        # Generate integration recommendations
        integration_recommendations = agent._generate_integration_recommendations(
            api_analysis, form_automation_results, automation_readiness_score, use_cases
        )
        
        # Create structured response formats
        structured_formats = agent._create_structured_response_formats(
            api_analysis, form_automation_results, interaction_patterns
        )
        
        return GEOPlusAgentOutput(
            api_analysis=api_analysis,
            form_automation_results=form_automation_results,
            interaction_patterns=interaction_patterns,
            automation_readiness_score=automation_readiness_score,
            integration_recommendations=integration_recommendations,
            structured_response_formats=structured_formats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Agent 4: Coordinator Agent

### Purpose
Orchestrate all three specialized agents by merging their results, resolving conflicts between recommendations, and creating prioritized implementation plans.

### Core Responsibilities
1. **Agent Orchestration**: Coordinate execution of all three specialized agents
2. **Result Merging**: Combine outputs from all agents into coherent recommendations
3. **Conflict Resolution**: Resolve contradictions between agent recommendations
4. **Priority Assignment**: Create prioritized implementation plans based on impact and effort
5. **Timeline Generation**: Estimate implementation timelines and resource requirements
6. **Quality Assurance**: Validate final recommendations for completeness and feasibility

### Input Requirements
- `CrawlerData` objects (single or multiple pages)
- Business data and external sources
- Agent configuration parameters
- Implementation constraints and preferences

### Output Specifications
```python
class CoordinatorAgentOutput(BaseModel):
    execution_summary: Dict[str, Any]
    merged_recommendations: Dict[str, List[Dict[str, Any]]]
    resolved_conflicts: List[Dict[str, Any]]
    prioritized_plan: List[Dict[str, Any]]
    implementation_timeline: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    monitoring_metrics: List[str]
```

### Technical Implementation

#### FastAPI Service Structure
```python
from fastapi import FastAPI, BackgroundTasks
import asyncio
import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta

app = FastAPI(title="Coordinator Agent Service", version="1.0.0")

class CoordinatorAgent:
    def __init__(self):
        self.agent_endpoints = {
            "aeo": "http://aeo-agent:8000",
            "geo": "http://geo-agent:8000",
            "geo_plus": "http://geo-plus-agent:8000"
        }
        self.conflict_resolution_rules = self._load_conflict_rules()
        self.priority_weights = self._load_priority_weights()
    
    async def orchestrate_agents(
        self, 
        crawler_data: List[CrawlerData], 
        business_data: Dict[str, Any],
        external_sources: Dict[str, Any],
        base_url: str,
        use_cases: List[str]
    ) -> Dict[str, Any]:
        """Coordinate execution of all specialized agents"""
        
        execution_results = {}
        
        async with httpx.AsyncClient() as client:
            # Execute agents in parallel where possible
            tasks = []
            
            # AEO Agent - can run independently for each page
            for page_data in crawler_data:
                task = self._call_aeo_agent(client, page_data, business_data)
                tasks.append(("aeo", page_data.url, task))
            
            # GEO Agent - needs all pages for consistency analysis
            geo_task = self._call_geo_agent(client, crawler_data, external_sources)
            tasks.append(("geo", "all_pages", geo_task))
            
            # GEO+ Agent - can run independently for each page
            for page_data in crawler_data:
                task = self._call_geo_plus_agent(client, page_data, base_url, use_cases)
                tasks.append(("geo_plus", page_data.url, task))
            
            # Execute all tasks
            results = await asyncio.gather(*[task for _, _, task in tasks], return_exceptions=True)
            
            # Organize results
            for i, (agent_name, page_url, _) in enumerate(tasks):
                if not isinstance(results[i], Exception):
                    if agent_name not in execution_results:
                        execution_results[agent_name] = {}
                    execution_results[agent_name][page_url] = results[i]
                else:
                    # Handle errors
                    if "errors" not in execution_results:
                        execution_results["errors"] = []
                    execution_results["errors"].append({
                        "agent": agent_name,
                        "page": page_url,
                        "error": str(results[i])
                    })
        
        return execution_results
    
    def merge_recommendations(self, agent_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Merge recommendations from all agents"""
        merged = {
            "visibility": [],
            "accuracy": [],
            "actionability": [],
            "technical": [],
            "content": []
        }
        
        # Process AEO Agent results
        if "aeo" in agent_results:
            for page_url, aeo_result in agent_results["aeo"].items():
                visibility_recs = self._extract_visibility_recommendations(aeo_result, page_url)
                merged["visibility"].extend(visibility_recs)
                
                content_recs = self._extract_content_recommendations(aeo_result, page_url)
                merged["content"].extend(content_recs)
        
        # Process GEO Agent results
        if "geo" in agent_results:
            geo_result = agent_results["geo"]["all_pages"]
            accuracy_recs = self._extract_accuracy_recommendations(geo_result)
            merged["accuracy"].extend(accuracy_recs)
        
        # Process GEO+ Agent results
        if "geo_plus" in agent_results:
            for page_url, geo_plus_result in agent_results["geo_plus"].items():
                actionability_recs = self._extract_actionability_recommendations(geo_plus_result, page_url)
                merged["actionability"].extend(actionability_recs)
                
                technical_recs = self._extract_technical_recommendations(geo_plus_result, page_url)
                merged["technical"].extend(technical_recs)
        
        return merged
    
    def resolve_conflicts(self, merged_recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify and resolve conflicts between agent recommendations"""
        conflicts_resolved = []
        
        # Collect all recommendations with their sources
        all_recommendations = []
        for category, recs in merged_recommendations.items():
            for rec in recs:
                rec["category"] = category
                all_recommendations.append(rec)
        
        # Group potentially conflicting recommendations
        conflict_groups = self._identify_conflict_groups(all_recommendations)
        
        for group in conflict_groups:
            if len(group) > 1:  # Multiple recommendations for same element
                resolution = self._resolve_recommendation_conflict(group)
                conflicts_resolved.append({
                    "conflict_type": resolution["type"],
                    "conflicting_recommendations": [
                        {
                            "agent": rec.get("source_agent"),
                            "recommendation": rec.get("action"),
                            "priority": rec.get("priority")
                        } for rec in group
                    ],
                    "resolution": resolution["chosen_recommendation"],
                    "reasoning": resolution["reasoning"],
                    "discarded_alternatives": resolution["discarded"]
                })
                
                # Update merged recommendations with resolved version
                self._update_merged_recommendations(merged_recommendations, resolution)
        
        return conflicts_resolved
    
    def create_prioritized_plan(self, merged_recommendations: Dict[str, List[Dict[str, Any]]], conflicts_resolved: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create prioritized implementation plan"""
        all_tasks = []
        
        # Convert recommendations to implementation tasks
        for category, recs in merged_recommendations.items():
            for rec in recs:
                task = self._convert_recommendation_to_task(rec, category)
                all_tasks.append(task)
        
        # Calculate priority scores
        for task in all_tasks:
            task["priority_score"] = self._calculate_priority_score(task)
        
        # Sort by priority score (descending)
        prioritized_tasks = sorted(all_tasks, key=lambda x: x["priority_score"], reverse=True)
        
        # Group into implementation phases
        phases = self._group_tasks_into_phases(prioritized_tasks)
        
        # Add dependencies and sequencing
        sequenced_plan = self._add_task_sequencing(phases)
        
        return sequenced_plan
    
    def generate_implementation_timeline(self, prioritized_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate implementation timeline with estimates"""
        timeline = {
            "total_estimated_duration": 0,
            "phases": [],
            "milestones": [],
            "critical_path": [],
            "resource_allocation": {}
        }
        
        current_date = datetime.now()
        
        for i, phase in enumerate(prioritized_plan):
            phase_duration = sum(task.get("estimated_hours", 4) for task in phase.get("tasks", []))
            phase_info = {
                "phase": i + 1,
                "name": phase.get("name", f"Phase {i + 1}"),
                "start_date": current_date.isoformat(),
                "estimated_duration_hours": phase_duration,
                "estimated_duration_days": max(1, phase_duration / 8),  # 8 hours per day
                "end_date": (current_date + timedelta(days=phase_duration / 8)).isoformat(),
                "tasks": phase.get("tasks", []),
                "dependencies": phase.get("dependencies", [])
            }
            
            timeline["phases"].append(phase_info)
            current_date = datetime.fromisoformat(phase_info["end_date"])
            
            # Add milestones
            if phase_info["estimated_duration_days"] >= 3:  # Major phases
                timeline["milestones"].append({
                    "name": f"Complete {phase_info['name']}",
                    "date": phase_info["end_date"],
                    "deliverables": [task["title"] for task in phase.get("tasks", [])]
                })
        
        timeline["total_estimated_duration"] = (current_date - datetime.now()).days
        timeline["critical_path"] = self._identify_critical_path(prioritized_plan)
        
        return timeline

@app.post("/coordinate", response_model=CoordinatorAgentOutput)
async def coordinate_optimization(
    crawler_data: List[CrawlerData],
    business_data: Dict[str, Any],
    external_sources: Dict[str, Any] = {},
    base_url: str = "",
    use_cases: List[str] = [],
    background_tasks: BackgroundTasks = None
):
    try:
        coordinator = CoordinatorAgent()
        
        # Step 1: Orchestrate all agents
        agent_results = await coordinator.orchestrate_agents(
            crawler_data, business_data, external_sources, base_url, use_cases
        )
        
        # Step 2: Merge recommendations
        merged_recommendations = coordinator.merge_recommendations(agent_results)
        
        # Step 3: Resolve conflicts
        resolved_conflicts = coordinator.resolve_conflicts(merged_recommendations)
        
        # Step 4: Create prioritized plan
        prioritized_plan = coordinator.create_prioritized_plan(merged_recommendations, resolved_conflicts)
        
        # Step 5: Generate timeline
        implementation_timeline = coordinator.generate_implementation_timeline(prioritized_plan)
        
        # Step 6: Calculate resource requirements
        resource_requirements = coordinator._calculate_resource_requirements(prioritized_plan)
        
        # Step 7: Estimate expected outcomes
        expected_outcomes = coordinator._estimate_outcomes(merged_recommendations, prioritized_plan)
        
        # Step 8: Define monitoring metrics
        monitoring_metrics = coordinator._define_monitoring_metrics(merged_recommendations)
        
        # Create execution summary
        execution_summary = {
            "timestamp": datetime.now().isoformat(),
            "pages_analyzed": len(crawler_data),
            "agents_executed": len([k for k in agent_results.keys() if k != "errors"]),
            "total_recommendations": sum(len(recs) for recs in merged_recommendations.values()),
            "conflicts_resolved": len(resolved_conflicts),
            "implementation_phases": len(prioritized_plan),
            "estimated_completion": implementation_timeline.get("phases", [])[-1].get("end_date") if implementation_timeline.get("phases") else None
        }
        
        return CoordinatorAgentOutput(
            execution_summary=execution_summary,
            merged_recommendations=merged_recommendations,
            resolved_conflicts=resolved_conflicts,
            prioritized_plan=prioritized_plan,
            implementation_timeline=implementation_timeline,
            resource_requirements=resource_requirements,
            expected_outcomes=expected_outcomes,
            monitoring_metrics=monitoring_metrics
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Complete Workflow Implementation

### Workflow Orchestration
```python
class GEOWorkflow:
    def __init__(self):
        self.coordinator_client = httpx.AsyncClient(base_url="http://coordinator-agent:8000")
    
    async def execute_complete_workflow(
        self,
        website_url: str,
        crawl_depth: int = 2,
        business_data: Dict[str, Any] = {},
        external_sources: Dict[str, Any] = {},
        use_cases: List[str] = []
    ) -> CoordinatorAgentOutput:
        """Execute the complete GEO optimization workflow"""
        
        # Step 1: Crawl website
        crawler = WebCrawler()
        crawler_data = await crawler.crawl_website(website_url, depth=crawl_depth)
        
        # Step 2: Coordinate agent execution
        result = await self.coordinator_client.post("/coordinate", json={
            "crawler_data": [data.dict() for data in crawler_data],
            "business_data": business_data,
            "external_sources": external_sources,
            "base_url": website_url,
            "use_cases": use_cases
        })
        
        return CoordinatorAgentOutput(**result.json())
```

## Deployment Configuration

### Docker Compose Setup
```yaml
version: '3.8'

services:
  aeo-agent:
    build: ./agents/aeo
    ports:
      - "8001:8000"
    environment:
      - AGENT_NAME=AEO
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  geo-agent:
    build: ./agents/geo
    ports:
      - "8002:8000"
    environment:
      - AGENT_NAME=GEO
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  geo-plus-agent:
    build: ./agents/geo_plus
    ports:
      - "8003:8000"
    environment:
      - AGENT_NAME=GEO_PLUS
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  coordinator-agent:
    build: ./agents/coordinator
    ports:
      - "8000:8000"
    environment:
      - AGENT_NAME=COORDINATOR
      - LOG_LEVEL=INFO
      - AEO_AGENT_URL=http://aeo-agent:8000
      - GEO_AGENT_URL=http://geo-agent:8000
      - GEO_PLUS_AGENT_URL=http://geo-plus-agent:8000
    depends_on:
      - aeo-agent
      - geo-agent
      - geo-plus-agent
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: geo_agents
      POSTGRES_USER: geo_user
      POSTGRES_PASSWORD: geo_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Implementation Guidelines

### Development Phases

#### Phase 1: Core Agent Development (4-6 weeks)
1. Implement basic FastAPI structure for each agent
2. Create core data models and validation
3. Implement basic analysis functions for each agent
4. Set up inter-agent communication protocols

#### Phase 2: Coordinator Implementation (2-3 weeks)
1. Implement agent orchestration logic
2. Create conflict resolution mechanisms
3. Build prioritization and planning algorithms
4. Implement timeline generation

#### Phase 3: Integration and Testing (3-4 weeks)
1. Set up Docker containerization
2. Implement comprehensive test suites
3. Create integration tests for agent communication
4. Performance testing and optimization

#### Phase 4: Deployment and Monitoring (2-3 weeks)
1. Set up production deployment pipeline
2. Implement monitoring and logging
3. Create documentation and API specifications
4. User acceptance testing

### Quality Assurance Requirements

#### Code Quality Standards
- Minimum 85% test coverage for all agents
- Type hints for all functions and classes
- Comprehensive error handling and logging
- API documentation with OpenAPI/Swagger
- Code formatting with Black and linting with Flake8

#### Performance Requirements
- Maximum 30-second response time for single-page analysis
- Maximum 5-minute response time for multi-page analysis (up to 50 pages)
- Concurrent request handling for at least 10 simultaneous analyses
- Memory usage not to exceed 2GB per agent instance

#### Security Requirements
- Input validation for all API endpoints
- Rate limiting to prevent abuse
- Secure handling of sensitive business data
- Encrypted communication between agents
- Audit logging for all operations

### Monitoring and Maintenance

#### Key Metrics to Monitor
- Agent response times and success rates
- Recommendation quality and implementation success
- System resource utilization
- Error rates and failure patterns
- User satisfaction with recommendations

#### Maintenance Procedures
- Weekly performance reviews and optimization
- Monthly accuracy validation against known good data
- Quarterly model updates and retraining
- Annual security audits and penetration testing

This specification provides a comprehensive foundation for implementing the complete 4-agent GEO system with proper separation of concerns, clear integration points, and robust coordination mechanisms.