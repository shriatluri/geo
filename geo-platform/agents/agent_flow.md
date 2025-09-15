# Technical Flow Analysis: AEO and GEO Agents

## Overview

This document provides a comprehensive technical analysis of the AEO and GEO agent architectures, their data flows, and implementation patterns within the GEO platform.

## AEO Agent (Search Engine Optimization) Flow

### Architecture Overview
The AEO agent follows a **legacy monolithic pattern** that needs to be understood alongside the **new modular pattern** that has been partially implemented.

### Current Flow (Legacy Pattern)
```
AEOAgent.analyze(website_data) →
├── Parse HTML with BeautifulSoup
├── 1. _analyze_schema_markup() 
├── 2. _generate_structured_data()
├── 3. _optimize_for_ai_responses()
├── 4. _analyze_content_structure()
├── 5. _analyze_meta_information()
└── Create AgentResponse with AnalysisResult[]
```

### Detailed Technical Flow

#### 1. Schema Markup Analysis (`_analyze_schema_markup`)
- **Input**: BeautifulSoup object, WebsiteData
- **Process**:
  - Scans for `<script type="application/ld+json">` tags
  - Parses JSON-LD content to identify existing schema types
  - Calls `_determine_required_schemas()` based on content analysis
  - Compares existing vs required schemas to identify gaps
  - Assesses schema quality using `_assess_schema_quality()`
- **Output**: AnalysisResult[] with schema gaps and quality issues

#### 2. Structured Data Generation (`_generate_structured_data`)
- **Input**: WebsiteData
- **Process**:
  - Extracts business name using `_extract_business_name()`
  - Creates Organization schema JSON-LD structure
  - Identifies FAQ opportunities using `_identify_faq_opportunities()`
  - Generates schema examples for implementation
- **Output**: AnalysisResult[] with generated schema recommendations

#### 3. AI Response Optimization (`_optimize_for_ai_responses`)
- **Input**: WebsiteData
- **Process**:
  - Analyzes content for AI-parseable structure
  - Checks for direct answers to common questions
  - Validates contact information clarity using `_has_clear_contact_info()`
  - Identifies optimization opportunities
- **Output**: AnalysisResult[] with AI optimization recommendations

#### 4. Content Structure Analysis (`_analyze_content_structure`)
- **Input**: BeautifulSoup object
- **Process**:
  - Scans heading tags (H1-H6)
  - Validates heading hierarchy using `_has_proper_heading_hierarchy()`
  - Checks for single H1 tag requirement
  - Identifies structural issues
- **Output**: AnalysisResult[] with content structure improvements

#### 5. Meta Information Analysis (`_analyze_meta_information`)
- **Input**: BeautifulSoup object, WebsiteData
- **Process**:
  - Validates title tag length (30-60 characters)
  - Checks meta description presence and length (120-160 characters)
  - Identifies meta optimization opportunities
- **Output**: AnalysisResult[] with meta tag recommendations

### New Modular Components (Implemented but Not Used)
- **AEOAnalyzer**: Modular analysis component (`src/aeo_agent/analyzer.py`)
- **AEOGenerator**: Content generation component (`src/aeo_agent/generator.py`)
- **AEOValidator**: Validation component (`src/aeo_agent/validator.py`)

---

## GEO Agent (Business Information Accuracy) Flow

### Architecture Overview
The GEO agent uses the **new modular pattern** with complete separation of concerns.

### Current Flow (New Modular Pattern)
```
GEOAgent.analyze(website_data, client_input?) →
├── ANALYSIS PHASE:
│   ├── analyzer.analyze_business_information()
│   ├── analyzer.analyze_contact_accuracy()
│   ├── analyzer.analyze_location_accuracy()
│   └── analyzer.analyze_business_credibility()
├── GENERATION PHASE:
│   ├── generator.generate_business_data()
│   ├── generator.generate_nap_standardization()
│   ├── generator.generate_contact_optimization()
│   ├── generator.generate_local_business_schema()
│   ├── generator.generate_accuracy_corrections()
│   └── generator.generate_verification_checklist()
├── VALIDATION PHASE:
│   ├── validator.validate_business_data()
│   ├── validator.validate_nap_consistency()
│   ├── validator.validate_contact_optimization()
│   ├── validator.validate_local_business_schema()
│   ├── validator.validate_accuracy_corrections()
│   ├── validator.validate_verification_checklist()
│   └── validator.validate_implementation_readiness()
└── Convert to AnalysisResult[] and create AgentResponse
```

### Detailed Technical Flow

#### ANALYSIS PHASE

**1. Business Information Analysis**
- **Method**: `analyzer.analyze_business_information(website_data)`
- **Process**:
  - Extracts business name from multiple sources (title, headers, schema, meta, footer)
  - Analyzes contact information completeness
  - Evaluates location data accuracy
  - Checks NAP consistency across page sections
  - Extracts business hours from text patterns and schema
- **Output**: Dict with accuracy_score, completeness_score, issues, recommendations

**2. Contact Accuracy Analysis**
- **Method**: `analyzer.analyze_contact_accuracy(website_data)`
- **Process**:
  - Validates phone number formats and types
  - Validates email address formats and categorizes types
  - Analyzes social media presence across platforms
  - Evaluates contact form quality and accessibility
- **Output**: Dict with validation results and contact optimization opportunities

**3. Location Accuracy Analysis**
- **Method**: `analyzer.analyze_location_accuracy(website_data)`
- **Process**:
  - Extracts and validates physical addresses
  - Identifies geographic indicators and service areas
  - Finds map embeds and location references
  - Checks location consistency across sources
- **Output**: Dict with location validation and accuracy assessment

**4. Business Credibility Analysis**
- **Method**: `analyzer.analyze_business_credibility(website_data)`
- **Process**:
  - Identifies trust signals (certifications, awards, testimonials)
  - Checks business registration information
  - Calculates credibility score based on indicators
- **Output**: Dict with credibility assessment and trust indicators

#### GENERATION PHASE

**1. Business Data Generation**
- **Method**: `generator.generate_business_data(analysis_result, client_input)`
- **Process**:
  - Creates standardized business profile
  - Generates contact data hierarchy
  - Standardizes location information
  - Creates operating hours structure
- **Output**: Dict with standardized business information

**2. NAP Standardization**
- **Method**: `generator.generate_nap_standardization(analysis_result)`
- **Process**:
  - Standardizes business name format
  - Formats addresses to USPS/Google standards
  - Standardizes phone number formats
  - Generates consistency guidelines
- **Output**: Dict with standardized NAP data

**3. Local Business Schema Generation**
- **Method**: `generator.generate_local_business_schema(analysis_result, client_input)`
- **Process**:
  - Creates LocalBusiness JSON-LD schema
  - Includes validated contact information
  - Adds address and operating hours
  - Provides implementation notes
- **Output**: Dict with schema markup and validation requirements

**4. Contact Optimization**
- **Method**: `generator.generate_contact_optimization(contact_analysis)`
- **Process**:
  - Identifies primary contact methods
  - Creates contact hierarchy
  - Recommends missing contact options
  - Suggests form improvements
- **Output**: Dict with contact optimization recommendations

**5. Accuracy Corrections**
- **Method**: `generator.generate_accuracy_corrections(analysis_result)`
- **Process**:
  - Generates name, address, phone, email corrections
  - Prioritizes corrections by impact
  - Creates implementation roadmap
- **Output**: Dict with correction recommendations

**6. Verification Checklist**
- **Method**: `generator.generate_verification_checklist(analysis_result)`
- **Process**:
  - Identifies critical and recommended verifications
  - Suggests verification sources and timeline
  - Creates automated check recommendations
- **Output**: Dict with verification checklist and procedures

#### VALIDATION PHASE

**1. Business Data Validation**
- **Method**: `validator.validate_business_data(generated_business_data)`
- **Process**:
  - Validates business profile completeness
  - Checks contact information formats
  - Validates location data accuracy
  - Calculates validation scores
- **Output**: Dict with validation results and error/warning lists

**2. NAP Consistency Validation**
- **Method**: `validator.validate_nap_consistency(nap_standardization)`
- **Process**:
  - Validates name standardization
  - Checks address format consistency
  - Validates phone number standardization
  - Calculates consistency scores
- **Output**: Dict with consistency validation results

**3. Contact Optimization Validation**
- **Method**: `validator.validate_contact_optimization(contact_optimization)`
- **Process**:
  - Validates primary contact methods
  - Checks contact hierarchy logic
  - Validates missing contact recommendations
  - Calculates optimization scores
- **Output**: Dict with contact optimization validation

**4. Local Business Schema Validation**
- **Method**: `validator.validate_local_business_schema(local_business_schema)`
- **Process**:
  - Validates schema structure and syntax
  - Checks LocalBusiness-specific requirements
  - Validates contact information in schema
  - Calculates schema quality scores
- **Output**: Dict with schema validation results

**5. Implementation Readiness Validation**
- **Method**: `validator.validate_implementation_readiness(all_generated_content)`
- **Process**:
  - Checks all validation results
  - Identifies blocking issues
  - Calculates readiness score
  - Generates implementation notes
- **Output**: Dict with implementation readiness assessment

### Result Conversion Phase

**Method**: `_convert_to_analysis_results()`
- **Process**:
  - Converts modular analysis results to legacy AnalysisResult format
  - Creates recommendations based on validation scores
  - Maintains backward compatibility with existing interfaces
- **Output**: List[AnalysisResult] for AgentResponse

---

## Key Technical Differences

### AEO Agent (Legacy Pattern)
- **Single-phase execution**: All analysis in one method
- **Direct HTML parsing**: BeautifulSoup operations scattered throughout
- **Immediate result generation**: Creates AnalysisResult objects directly
- **Limited validation**: Basic quality checks only
- **No client input integration**: Static analysis only
- **Monolithic structure**: All logic in main agent file

### GEO Agent (New Modular Pattern)
- **Three-phase execution**: Analysis → Generation → Validation
- **Centralized parsing**: HTML parsing in analyzer components
- **Intermediate data structures**: Rich data objects between phases
- **Comprehensive validation**: Multi-level validation with scores
- **Client input integration**: Accepts and utilizes client-specific data
- **Modular structure**: Separated concerns across multiple files

---

## Data Flow Objects

### AEO Agent Data Flow
```
WebsiteData → BeautifulSoup → AnalysisResult[] → AgentResponse
```

### GEO Agent Data Flow
```
WebsiteData + ClientInput → 
  Analysis Dicts → 
    Generation Dicts → 
      Validation Dicts → 
        AnalysisResult[] → 
          AgentResponse
```

---

## Component Responsibilities

### Analyzer Components
- **Purpose**: Extract and analyze raw data from website content
- **Input**: WebsiteData object
- **Output**: Structured analysis dictionaries
- **Responsibilities**:
  - HTML parsing and content extraction
  - Pattern matching and data validation
  - Quality scoring and issue identification
  - Business logic for analysis rules

### Generator Components
- **Purpose**: Create optimized content and recommendations
- **Input**: Analysis results and optional client input
- **Output**: Generated content and improvement recommendations
- **Responsibilities**:
  - Content standardization and formatting
  - Schema markup generation
  - Optimization recommendation creation
  - Implementation guidance

### Validator Components
- **Purpose**: Validate generated content before delivery
- **Input**: Generated content dictionaries
- **Output**: Validation results with scores and issues
- **Responsibilities**:
  - Content quality validation
  - Format and syntax checking
  - Implementation readiness assessment
  - Error and warning identification

---

## Migration Path

To complete the AEO agent restructure to match the GEO pattern:

1. **Update AEO Agent Main Method**:
   - Replace legacy single-phase analysis with three-phase flow
   - Integrate existing AEOAnalyzer, AEOGenerator, AEOValidator components
   - Add client input parameter support

2. **Enhance AEO Components**:
   - Complete AEOGenerator implementation
   - Add comprehensive validation to AEOValidator
   - Ensure data structure consistency

3. **Maintain Backward Compatibility**:
   - Keep legacy analyze method as analyze_legacy()
   - Provide conversion between data formats
   - Preserve existing AnalysisResult output format

This modular architecture provides better separation of concerns, enhanced validation, and improved maintainability while supporting future extensibility and client-specific customizations.