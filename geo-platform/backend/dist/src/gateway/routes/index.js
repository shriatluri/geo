"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.apiRoutes = void 0;
const express_1 = require("express");
const health_1 = require("./health");
const sites_1 = require("./sites");
const analysis_1 = require("./analysis");
const auth_1 = require("./auth");
const router = (0, express_1.Router)();
exports.apiRoutes = router;
// Mount route modules
router.use('/health', health_1.healthRoutes);
router.use('/auth', auth_1.authRoutes);
router.use('/sites', sites_1.siteRoutes);
router.use('/analysis', analysis_1.analysisRoutes);
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
//# sourceMappingURL=index.js.map