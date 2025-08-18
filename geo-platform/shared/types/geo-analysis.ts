// Core GEO Analysis Types
export interface GEOAnalysis {
  id: string;
  domain: string;
  crawl_timestamp: Date;
  
  // Core scores (0-100)
  visibility_score: number;    // Can AI engines find/cite content?
  accuracy_score: number;      // Is extracted info correct?
  actionability_score: number; // Can agents take actions?
  
  // Detailed findings
  schema_issues: SchemaIssue[];
  content_gaps: ContentGap[];
  api_endpoints: APIEndpoint[];
  
  // AI-generated recommendations
  recommendations: Recommendation[];
  
  // Raw data
  crawl_data: CrawlData;
  ai_analysis: AIAnalysisData;
  
  // Metadata
  created_at: Date;
  updated_at: Date;
  status: AnalysisStatus;
}

export interface Recommendation {
  id: string;
  type: 'schema' | 'content' | 'api' | 'structure';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  
  // Actionable fix
  fix_type: 'add_schema' | 'update_content' | 'expose_api';
  implementation: {
    code_example?: string;
    file_path?: string;
    automated_fix_available: boolean;
  };
  
  // Expected impact
  estimated_score_improvement: {
    visibility?: number;
    accuracy?: number;
    actionability?: number;
  };
}

export interface SchemaIssue {
  id: string;
  type: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  location: string;
  suggestion: string;
}

export interface ContentGap {
  id: string;
  type: 'missing_info' | 'outdated_info' | 'unclear_info';
  description: string;
  importance: 'high' | 'medium' | 'low';
  suggested_content: string;
}

export interface APIEndpoint {
  id: string;
  url: string;
  method: string;
  description: string;
  is_accessible: boolean;
  response_format: string;
  authentication_required: boolean;
}

export interface CrawlData {
  pages_crawled: number;
  total_content: string;
  schemas: Record<string, any>[];
  metadata: Record<string, any>;
  screenshots: string[];
  performance_metrics: PerformanceMetrics;
}

export interface AIAnalysisData {
  visibility_tests: VisibilityTest[];
  accuracy_tests: AccuracyTest[];
  actionability_tests: ActionabilityTest[];
  analysis_timestamp: Date;
  models_used: string[];
}

export interface PerformanceMetrics {
  page_load_time: number;
  total_size: number;
  resource_count: number;
  lighthouse_score?: number;
}

export interface VisibilityTest {
  platform: 'chatgpt' | 'claude' | 'gemini';
  query: string;
  found_content: boolean;
  citation_accuracy: number;
  response_quality: number;
}

export interface AccuracyTest {
  information_type: string;
  source_value: string;
  ai_extracted_value: string;
  accuracy_score: number;
  discrepancy_details?: string;
}

export interface ActionabilityTest {
  action_type: 'api_call' | 'form_submission' | 'navigation';
  success: boolean;
  error_details?: string;
  response_time?: number;
}

export type AnalysisStatus = 
  | 'pending'
  | 'crawling'
  | 'analyzing'
  | 'generating_recommendations'
  | 'completed'
  | 'failed';

// Job Queue Types
export interface CrawlJob {
  id: string;
  domain: string;
  depth: number;
  include_apis: boolean;
  status: JobStatus;
  progress: number;
  created_at: Date;
  started_at?: Date;
  completed_at?: Date;
  error_message?: string;
}

export interface AnalysisJob {
  id: string;
  crawl_job_id: string;
  domain: string;
  status: JobStatus;
  progress: number;
  created_at: Date;
  started_at?: Date;
  completed_at?: Date;
  error_message?: string;
}

export type JobStatus = 
  | 'pending'
  | 'active'
  | 'completed'
  | 'failed'
  | 'delayed'
  | 'paused';

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}
