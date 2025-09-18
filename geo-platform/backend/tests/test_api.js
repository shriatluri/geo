/**
 * API endpoint tests for GEO Platform backend.
 */

const request = require('supertest');
const app = require('../src/app');

describe('API Endpoints', () => {
  describe('Health Check', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('services');
    });
  });

  describe('Analysis Endpoints', () => {
    it('should accept analysis request', async () => {
      const analysisRequest = {
        url: 'https://example.com',
        options: {
          depth: 1,
          include_apis: false
        }
      };

      const response = await request(app)
        .post('/api/v1/analysis')
        .send(analysisRequest)
        .expect(202);

      expect(response.body).toHaveProperty('job_id');
      expect(response.body).toHaveProperty('status', 'queued');
    });

    it('should validate analysis request', async () => {
      const invalidRequest = {
        url: 'not-a-url'
      };

      const response = await request(app)
        .post('/api/v1/analysis')
        .send(invalidRequest)
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should get analysis status', async () => {
      // First create an analysis job
      const analysisRequest = {
        url: 'https://example.com',
        options: { depth: 1 }
      };

      const createResponse = await request(app)
        .post('/api/v1/analysis')
        .send(analysisRequest)
        .expect(202);

      const jobId = createResponse.body.job_id;

      // Then check its status
      const statusResponse = await request(app)
        .get(`/api/v1/analysis/${jobId}`)
        .expect(200);

      expect(statusResponse.body).toHaveProperty('job_id', jobId);
      expect(statusResponse.body).toHaveProperty('status');
    });

    it('should return 404 for non-existent job', async () => {
      await request(app)
        .get('/api/v1/analysis/non-existent-id')
        .expect(404);
    });
  });

  describe('Agent Endpoints', () => {
    it('should list available agents', async () => {
      const response = await request(app)
        .get('/api/v1/agents')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body.length).toBeGreaterThan(0);

      // Check agent structure
      const agent = response.body[0];
      expect(agent).toHaveProperty('name');
      expect(agent).toHaveProperty('type');
      expect(agent).toHaveProperty('status');
    });

    it('should get agent health', async () => {
      const response = await request(app)
        .get('/api/v1/agents/health')
        .expect(200);

      expect(response.body).toHaveProperty('total_agents');
      expect(response.body).toHaveProperty('healthy_agents');
      expect(response.body).toHaveProperty('agents');
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits', async () => {
      const requests = [];

      // Make multiple requests quickly
      for (let i = 0; i < 20; i++) {
        requests.push(
          request(app)
            .get('/health')
        );
      }

      const responses = await Promise.all(requests);

      // Some requests should be rate limited
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle internal server errors', async () => {
      // This endpoint should trigger an error for testing
      const response = await request(app)
        .get('/api/v1/test-error')
        .expect(500);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('Internal server error');
    });

    it('should handle validation errors', async () => {
      const response = await request(app)
        .post('/api/v1/analysis')
        .send({}) // Empty body should trigger validation error
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body).toHaveProperty('validation_errors');
    });
  });

  describe('CORS', () => {
    it('should include CORS headers', async () => {
      const response = await request(app)
        .options('/api/v1/analysis')
        .expect(200);

      expect(response.headers).toHaveProperty('access-control-allow-origin');
      expect(response.headers).toHaveProperty('access-control-allow-methods');
    });
  });

  describe('Authentication', () => {
    it('should require authentication for protected routes', async () => {
      await request(app)
        .get('/api/v1/admin/stats')
        .expect(401);
    });

    it('should accept valid authentication', async () => {
      // This would need a valid token for the test environment
      const token = 'test-token';

      await request(app)
        .get('/api/v1/admin/stats')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
    });
  });
});