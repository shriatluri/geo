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
    log: process.env.NODE_ENV === 'development'
        ? ['warn', 'error']
        : ['error'],
    errorFormat: 'minimal',
};
// Create Prisma client instance
exports.prisma = globalThis.__prisma || new client_1.PrismaClient(prismaClientConfig);
// In development, store Prisma client in global to prevent creating multiple instances
if (process.env.NODE_ENV === 'development') {
    globalThis.__prisma = exports.prisma;
}
// Note: Prisma logging is configured to output to stdout
// For more advanced logging, you can enable events in the config above
// Database connection health check
async function checkDatabaseConnection() {
    try {
        // Use $executeRaw instead of $queryRaw to avoid prepared statement conflicts
        await exports.prisma.$executeRaw `SELECT 1`;
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
        // Use sequential queries to avoid prepared statement conflicts in development
        const userCount = await exports.prisma.user.count();
        const siteCount = await exports.prisma.site.count();
        const analysisCount = await exports.prisma.analysis.count();
        return {
            users: userCount,
            sites: siteCount,
            analyses: analysisCount,
            timestamp: new Date().toISOString(),
        };
    }
    catch (error) {
        logger_1.logger.error('Error getting database metrics:', error);
        // Return default metrics instead of throwing
        return {
            users: 0,
            sites: 0,
            analyses: 0,
            timestamp: new Date().toISOString(),
            error: 'Could not fetch metrics'
        };
    }
}
// Export Prisma client as default
exports.default = exports.prisma;
//# sourceMappingURL=database.js.map