import { z } from 'zod';

// Core Analysis Schemas
export const GEOAnalysisSchema = z.object({
  id: z.string().uuid(),
  domain: z.string().url(),
  crawl_timestamp: z.date(),
  visibility_score: z.number().min(0).max(100),
  accuracy_score: z.number().min(0).max(100),
  actionability_score: z.number().min(0).max(100),
  schema_issues: z.array(z.any()),
  content_gaps: z.array(z.any()),
  api_endpoints: z.array(z.any()),
  recommendations: z.array(z.any()),
  crawl_data: z.any(),
  ai_analysis: z.any(),
  created_at: z.date(),
  updated_at: z.date(),
  status: z.enum(['pending', 'crawling', 'analyzing', 'generating_recommendations', 'completed', 'failed'])
});

export const RecommendationSchema = z.object({
  id: z.string().uuid(),
  type: z.enum(['schema', 'content', 'api', 'structure']),
  priority: z.enum(['high', 'medium', 'low']),
  title: z.string().min(1).max(200),
  description: z.string().min(1).max(1000),
  fix_type: z.enum(['add_schema', 'update_content', 'expose_api']),
  implementation: z.object({
    code_example: z.string().optional(),
    file_path: z.string().optional(),
    automated_fix_available: z.boolean()
  }),
  estimated_score_improvement: z.object({
    visibility: z.number().min(0).max(100).optional(),
    accuracy: z.number().min(0).max(100).optional(),
    actionability: z.number().min(0).max(100).optional()
  })
});

// Job Schemas
export const CrawlJobSchema = z.object({
  id: z.string().uuid(),
  domain: z.string().url(),
  depth: z.number().min(1).max(10),
  include_apis: z.boolean(),
  status: z.enum(['pending', 'active', 'completed', 'failed', 'delayed', 'paused']),
  progress: z.number().min(0).max(100),
  created_at: z.date(),
  started_at: z.date().optional(),
  completed_at: z.date().optional(),
  error_message: z.string().optional()
});

export const AnalysisJobSchema = z.object({
  id: z.string().uuid(),
  crawl_job_id: z.string().uuid(),
  domain: z.string().url(),
  status: z.enum(['pending', 'active', 'completed', 'failed', 'delayed', 'paused']),
  progress: z.number().min(0).max(100),
  created_at: z.date(),
  started_at: z.date().optional(),
  completed_at: z.date().optional(),
  error_message: z.string().optional()
});

// API Request Schemas
export const AnalyzeSiteRequestSchema = z.object({
  domain: z.string().url(),
  depth: z.number().min(1).max(10).default(3),
  include_apis: z.boolean().default(true)
});

export const ApplyFixesRequestSchema = z.object({
  recommendation_ids: z.array(z.string().uuid()).min(1),
  github_integration: z.object({
    repo: z.string().regex(/^[\w-]+\/[\w-]+$/),
    create_pr: z.boolean().default(true)
  }).optional()
});

// Site Management Schemas
export const SiteSchema = z.object({
  id: z.string().uuid(),
  domain: z.string().url(),
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  owner_id: z.string().uuid(),
  created_at: z.date(),
  updated_at: z.date(),
  last_analyzed: z.date().optional(),
  is_active: z.boolean().default(true)
});

export const CreateSiteRequestSchema = z.object({
  domain: z.string().url(),
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional()
});

export const UpdateSiteRequestSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().max(500).optional(),
  is_active: z.boolean().optional()
});

// User Management Schemas
export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(['admin', 'user']),
  created_at: z.date(),
  updated_at: z.date(),
  last_login: z.date().optional(),
  is_active: z.boolean().default(true)
});

export const RegisterRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  name: z.string().min(1).max(100)
});

export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1)
});

// Pagination Schema
export const PaginationSchema = z.object({
  page: z.number().min(1).default(1),
  limit: z.number().min(1).max(100).default(20),
  sort: z.string().optional(),
  order: z.enum(['asc', 'desc']).default('desc')
});

// Export type inference
export type GEOAnalysisInput = z.infer<typeof GEOAnalysisSchema>;
export type RecommendationInput = z.infer<typeof RecommendationSchema>;
export type CrawlJobInput = z.infer<typeof CrawlJobSchema>;
export type AnalysisJobInput = z.infer<typeof AnalysisJobSchema>;
export type AnalyzeSiteRequest = z.infer<typeof AnalyzeSiteRequestSchema>;
export type ApplyFixesRequest = z.infer<typeof ApplyFixesRequestSchema>;
export type SiteInput = z.infer<typeof SiteSchema>;
export type CreateSiteRequest = z.infer<typeof CreateSiteRequestSchema>;
export type UpdateSiteRequest = z.infer<typeof UpdateSiteRequestSchema>;
export type UserInput = z.infer<typeof UserSchema>;
export type RegisterRequest = z.infer<typeof RegisterRequestSchema>;
export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type PaginationInput = z.infer<typeof PaginationSchema>;
