"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.prisma = void 0;
exports.checkDatabaseConnection = checkDatabaseConnection;
exports.disconnectDatabase = disconnectDatabase;
exports.getDatabaseMetrics = getDatabaseMetrics;
const client_1 = require("@prisma/client");
const logger_1 = require("./logger");
// Prisma client configuration
const prismaClientConfig = {
    log: [
        { level: 'query', emit: 'event' },
        { level: 'error', emit: 'event' },
        { level: 'info', emit: 'event' },
        { level: 'warn', emit: 'event' },
    ],
};
// Create Prisma client instance
exports.prisma = globalThis.__prisma || new client_1.PrismaClient(prismaClientConfig);
// In development, store Prisma client in global to prevent creating multiple instances
if (process.env.NODE_ENV === 'development') {
    globalThis.__prisma = exports.prisma;
}
// Set up logging for Prisma events
exports.prisma.$on('query', (e) => {
    logger_1.logger.debug(`Prisma Query: ${e.query}`, {
        query: e.query,
        params: e.params,
        duration: `${e.duration}ms`,
        timestamp: e.timestamp,
    });
});
exports.prisma.$on('error', (e) => {
    logger_1.logger.error(`Prisma Error: ${e.message}`, {
        target: e.target,
        timestamp: e.timestamp,
    });
});
exports.prisma.$on('info', (e) => {
    logger_1.logger.info(`Prisma Info: ${e.message}`, {
        target: e.target,
        timestamp: e.timestamp,
    });
});
exports.prisma.$on('warn', (e) => {
    logger_1.logger.warn(`Prisma Warning: ${e.message}`, {
        target: e.target,
        timestamp: e.timestamp,
    });
});
// Database connection health check
async function checkDatabaseConnection() {
    try {
        await exports.prisma.$queryRaw `SELECT 1`;
        logger_1.logger.info('Database connection successful');
        return true;
    }
    catch (error) {
        logger_1.logger.error('Database connection failed:', error);
        return false;
    }
}
// Graceful shutdown
async function disconnectDatabase() {
    try {
        await exports.prisma.$disconnect();
        logger_1.logger.info('Database disconnected successfully');
    }
    catch (error) {
        logger_1.logger.error('Error disconnecting from database:', error);
    }
}
// Database metrics for monitoring
async function getDatabaseMetrics() {
    try {
        const [userCount, siteCount, analysisCount] = await Promise.all([
            exports.prisma.user.count(),
            exports.prisma.site.count(),
            exports.prisma.analysis.count(),
        ]);
        return {
            users: userCount,
            sites: siteCount,
            analyses: analysisCount,
            timestamp: new Date().toISOString(),
        };
    }
    catch (error) {
        logger_1.logger.error('Error getting database metrics:', error);
        throw error;
    }
}
// Export Prisma client as default
exports.default = exports.prisma;
//# sourceMappingURL=database.js.map