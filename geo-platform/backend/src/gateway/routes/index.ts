import { Router } from 'express';
import { healthRoutes } from './health';
import { siteRoutes } from './sites';
import { analysisRoutes } from './analysis';
import { authRoutes } from './auth';

const router = Router();

// Mount route modules
router.use('/health', healthRoutes);
router.use('/auth', authRoutes);
router.use('/sites', siteRoutes);
router.use('/analysis', analysisRoutes);

// API info endpoint
router.get('/', (req, res) => {
  res.json({
    name: 'GEO Platform API',
    version: '1.0.0',
    description: 'Generative Engine Optimization Platform API Gateway',
    endpoints: {
      health: '/api/health',
      auth: '/api/auth',
      sites: '/api/sites',
      analysis: '/api/analysis',
    },
    documentation: '/api/docs',
    timestamp: new Date().toISOString(),
  });
});

export { router as apiRoutes };
