"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.healthRoutes = void 0;
const express_1 = require("express");
const logger_1 = require("../../utils/logger");
const database_1 = require("../../utils/database");
const router = (0, express_1.Router)();
exports.healthRoutes = router;
// Basic health check
router.get('/', (req, res) => {
    res.status(200).json({
        status: 'healthy',
        service: 'geo-backend',
        version: process.env.npm_package_version || '1.0.0',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
    });
});
// Detailed health check with dependencies
router.get('/detailed', async (req, res) => {
    const healthChecks = {
        service: 'healthy',
        database: 'unknown',
        redis: 'unknown',
        queues: 'unknown',
    };
    try {
        // Database connection check
        healthChecks.database = await (0, database_1.checkDatabaseConnection)() ? 'healthy' : 'unhealthy';
        // TODO: Add Redis connection check when Redis is set up
        // healthChecks.redis = await checkRedisConnection() ? 'healthy' : 'unhealthy';
        // TODO: Add queue system check when BullMQ is set up
        // healthChecks.queues = await checkQueuesConnection() ? 'healthy' : 'unhealthy';
        // Get database metrics if database is healthy
        let metrics;
        if (healthChecks.database === 'healthy') {
            try {
                metrics = await (0, database_1.getDatabaseMetrics)();
            }
            catch (error) {
                logger_1.logger.warn('Could not fetch database metrics:', error);
            }
        }
        const isHealthy = Object.values(healthChecks).every(status => status === 'healthy' || status === 'unknown');
        res.status(isHealthy ? 200 : 503).json({
            status: isHealthy ? 'healthy' : 'degraded',
            checks: healthChecks,
            metrics,
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            environment: process.env.NODE_ENV || 'development',
        });
    }
    catch (error) {
        logger_1.logger.error('Health check failed:', error);
        res.status(503).json({
            status: 'unhealthy',
            checks: healthChecks,
            error: 'Health check failed',
            timestamp: new Date().toISOString(),
        });
    }
});
//# sourceMappingURL=health.js.map