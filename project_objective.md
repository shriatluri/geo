# GEO Platform - Generative Engine Optimization

> **Take control of how AI sees you, be visible, accurate, and future-ready**

## 🎯 Project Overview

**GEO (Generative Engine Optimization)** is an AI-powered platform that prepares websites for the new world of AI-driven discovery and action. Unlike traditional SEO (Google rankings) or AEO (Answer Engine visibility), GEO ensures websites are not just visible but also **accurately understood** and **actionable** by AI agents and copilots.

### 🚀 Mission Statement
Our mission is to boost your website's visibility in AI searches across platforms like ChatGPT, Claude, and Gemini, ensure that the answers generated from your content are accurate and trustworthy, and prepare you for a future where the majority of searches and conversations happen through LLMs.

### 🔮 Vision
To prepare businesses for the shift where AI engines replace traditional search, ensuring they are not just seen, but understood and relied upon.

### Core Value Proposition
- **Visibility**: Ensure AI engines can discover and cite your content across ChatGPT, Claude, Gemini, and future LLMs
- **Accuracy**: Validate that AI extracts correct information (pricing, policies, etc.) and generates trustworthy answers
- **Future-Ready**: Prepare for a world where AI conversations replace traditional search queries

---

## 🏗️ Architecture Overview

### Multi-Service Architecture
```
Frontend (Next.js) ↔ API Gateway (Node.js) ↔ AI Agents (Python)
                           ↕
                  Database (PostgreSQL + Redis)
```

### Service Responsibilities
- **Node.js Backend**: Web crawling, API endpoints, job queues, real-time updates
- **Python Agents**: AI analysis, content validation, automated optimization
- **Next.js Frontend**: Dashboards, reports, user management
- **PostgreSQL**: Structured data, analysis results, user data
- **Redis**: Job queues, caching, session management

---

## 📁 Project Structure

```
geo-platform/
├── frontend/                 # Next.js dashboard
│   ├── app/                 # Next.js 14 app router
│   ├── components/          # Reusable UI components
│   ├── lib/                 # Utilities and hooks
│   └── types/               # TypeScript definitions
├── backend/                 # Node.js API gateway
│   ├── src/
│   │   ├── controllers/     # Route handlers
│   │   ├── services/        # Business logic
│   │   ├── models/          # Database models
│   │   ├── queues/          # Job queue definitions
│   │   └── utils/           # Helper functions
│   └── tests/
├── agents/                  # Python AI agents
│   ├── src/
│   │   ├── agents/          # LangChain agents
│   │   ├── tools/           # Agent tools
│   │   ├── models/          # AI model wrappers
│   │   └── tasks/           # Celery tasks
│   └── tests/
├── shared/                  # Shared types and schemas
│   ├── types/               # TypeScript interfaces
│   └── schemas/             # JSON schemas
└── infrastructure/          # Deployment configs
    ├── docker/
    ├── k8s/
    └── terraform/
```

---

## 🔧 Tech Stack

### Backend (Node.js/TypeScript)
- **Framework**: Express.js or Fastify
- **Database ORM**: Prisma or TypeORM
- **Queue System**: BullMQ (Redis-based)
- **Web Crawling**: Puppeteer + Playwright
- **Validation**: Zod for schema validation
- **Testing**: Jest + Supertest

### AI Agents (Python)
- **Framework**: FastAPI for agent APIs
- **AI Orchestration**: LangChain + LangGraph
- **Task Queue**: Celery with Redis broker
- **AI Models**: OpenAI SDK, Anthropic SDK
- **Web Scraping**: BeautifulSoup, Scrapy
- **Testing**: pytest + httpx

### Frontend (Next.js/React)
- **Framework**: Next.js 14+ with App Router
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand + React Query
- **Charts**: Recharts for analytics
- **Real-time**: Socket.io for live updates
- **Testing**: Vitest + React Testing Library

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Databases**: PostgreSQL 15+ + Redis 7+
- **Monitoring**: Winston (logs) + Prometheus (metrics)
- **Deployment**: Kubernetes or Docker Swarm

---

## 🚀 Core Workflows

### 1. Site Analysis Pipeline
```typescript
// Example flow
const analyzeWebsite = async (domain: string) => {
  // 1. Queue crawling job (Node.js)
  const crawlJob = await crawlQueue.add('crawl-site', { domain });
  
  // 2. Trigger AI analysis (Python agent)
  const aiJob = await aiQueue.add('geo-analysis', { 
    crawlJobId: crawlJob.id, 
    domain 
  });
  
  // 3. Return job tracking info
  return { jobId: aiJob.id, status: 'processing' };
};
```

### 2. AI Agent Analysis
```python
# Python agent workflow
class GEOAgent:
    async def analyze_site(self, domain: str, crawl_data: dict):
        # 1. Validate schema.org markup
        schema_score = await self.validate_schemas(crawl_data.schemas)
        
        # 2. Test AI visibility (can ChatGPT find this content?)
        visibility_score = await self.test_ai_visibility(crawl_data.content)
        
        # 3. Check actionability (can agents use APIs?)
        action_score = await self.test_actionability(crawl_data.apis)
        
        # 4. Generate specific recommendations
        recommendations = await self.generate_improvements(
            schema_score, visibility_score, action_score
        )
        
        return GEOAnalysis(
            visibility_score=visibility_score,
            accuracy_score=schema_score, 
            actionability_score=action_score,
            recommendations=recommendations
        )
```

### 3. Real-time Dashboard Updates
```tsx
// Frontend component with live updates
export default function SiteAnalysisDashboard({ siteId }: { siteId: string }) {
  const [analysis, setAnalysis] = useState<GEOAnalysis | null>(null);
  
  useEffect(() => {
    const socket = io();
    socket.on(`analysis-${siteId}`, setAnalysis);
    return () => socket.disconnect();
  }, [siteId]);
  
  return (
    <div className="grid grid-cols-3 gap-6">
      <ScoreCard title="Visibility" score={analysis?.visibility_score} />
      <ScoreCard title="Accuracy" score={analysis?.accuracy_score} />
      <ScoreCard title="Actionability" score={analysis?.actionability_score} />
    </div>
  );
}
```

---

## 📊 Key Data Models

### Site Analysis Result
```typescript
interface GEOAnalysis {
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
}
```

### Recommendation System
```typescript
interface Recommendation {
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
```

---

## 🔌 API Endpoints

### Core Analysis API
```typescript
// Start site analysis
POST /api/sites/analyze
{
  "domain": "example.com",
  "depth": 3,
  "include_apis": true
}

// Get analysis results
GET /api/sites/{siteId}/analysis
Response: GEOAnalysis

// Get real-time status
GET /api/sites/{siteId}/status
Response: { status: 'crawling' | 'analyzing' | 'complete', progress: number }

// Apply automated fixes
POST /api/sites/{siteId}/apply-fixes
{
  "recommendation_ids": ["rec_1", "rec_2"],
  "github_integration": {
    "repo": "owner/repo",
    "create_pr": true
  }
}
```

### AI Agent Integration
```python
# Python FastAPI endpoints for agent communication
@app.post("/agents/analyze")
async def trigger_analysis(request: AnalysisRequest):
    task = geo_analysis_agent.delay(request.crawl_job_id, request.domain)
    return {"task_id": task.id}

@app.get("/agents/status/{task_id}")
async def get_analysis_status(task_id: str):
    result = AsyncResult(task_id)
    return {"status": result.status, "result": result.result}
```

---

## 🧪 Testing Strategy

### Backend Testing (Node.js)
```typescript
// Example service test
describe('WebCrawler', () => {
  it('should extract schema.org data correctly', async () => {
    const crawler = new WebCrawler();
    const result = await crawler.crawlPage('https://example.com');
    
    expect(result.schemas).toHaveLength(1);
    expect(result.schemas[0]['@type']).toBe('Organization');
  });
});
```

### AI Agent Testing (Python)
```python
# Example agent test
@pytest.mark.asyncio
async def test_schema_validation():
    agent = GEOAgent()
    invalid_schema = {"@type": "InvalidType"}
    
    result = await agent.validate_schema(invalid_schema)
    assert result.is_valid == False
    assert "InvalidType" in result.errors[0]
```

### Frontend Testing (React)
```tsx
// Example component test
test('displays analysis scores correctly', () => {
  const mockAnalysis = {
    visibility_score: 85,
    accuracy_score: 92,
    actionability_score: 78
  };
  
  render(<ScoreCard analysis={mockAnalysis} />);
  
  expect(screen.getByText('85')).toBeInTheDocument();
  expect(screen.getByText('Visibility')).toBeInTheDocument();
});
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Quick Start
```bash
# Clone and setup
git clone <repo-url>
cd geo-platform

# Start infrastructure
docker-compose up -d postgres redis

# Setup backend
cd backend
npm install
npm run db:migrate
npm run dev

# Setup agents
cd ../agents
pip install -r requirements.txt
celery -A src.tasks worker --loglevel=info

# Setup frontend
cd ../frontend
npm install
npm run dev
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/geo_db
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...

# Python Agents (.env)
CELERY_BROKER_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost:5432/geo_db
OPENAI_API_KEY=sk-...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📈 Key Metrics & Monitoring

### Performance Metrics
- **Crawl Speed**: Pages/minute processed
- **Analysis Latency**: Time from crawl to AI analysis completion
- **Accuracy Rate**: How often AI recommendations improve actual scores
- **User Engagement**: Dashboard usage, report exports

### System Health
- **Queue Depth**: Pending jobs in Redis queues
- **Error Rates**: Failed crawls, AI API timeouts
- **Resource Usage**: CPU/memory across services
- **Database Performance**: Query times, connection pools

---

## 🔄 Development Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes

### Code Standards
- **TypeScript**: Strict mode enabled
- **Python**: Black formatter + pylint
- **Testing**: 80%+ coverage required
- **Documentation**: JSDoc/docstrings for all public functions

### CI/CD Pipeline
1. **Pre-commit**: Lint, format, type check
2. **CI**: Run tests, build containers
3. **Staging**: Deploy to staging environment
4. **Production**: Manual approval + deploy

---

## 🤝 Contributing

### Adding New AI Agents
1. Create agent class in `agents/src/agents/`
2. Define tools in `agents/src/tools/`
3. Add Celery task in `agents/src/tasks/`
4. Update API endpoints
5. Add comprehensive tests

### Adding New Analysis Types
1. Define data models in `shared/types/`
2. Update crawling logic in `backend/src/services/`
3. Create analysis agent in Python
4. Update frontend components
5. Add database migrations
