import { PrismaClient } from '@prisma/client';
import { logger } from './logger';

// Global singleton for Prisma client to prevent multiple instances
declare global {
  var __prisma: PrismaClient | undefined;
}

// Prisma client configuration
const prismaClientConfig = {
  log: process.env.NODE_ENV === 'development' 
    ? ['warn' as const, 'error' as const] 
    : ['error' as const],
  errorFormat: 'minimal' as const,
};

// Create Prisma client instance
export const prisma = globalThis.__prisma || new PrismaClient(prismaClientConfig);

// In development, store Prisma client in global to prevent creating multiple instances
if (process.env.NODE_ENV === 'development') {
  globalThis.__prisma = prisma;
}

// Note: Prisma logging is configured to output to stdout
// For more advanced logging, you can enable events in the config above

// Database connection health check
export async function checkDatabaseConnection(): Promise<boolean> {
  try {
    // Use $executeRaw instead of $queryRaw to avoid prepared statement conflicts
    await prisma.$executeRaw`SELECT 1`;
    logger.info('Database connection successful');
    return true;
  } catch (error) {
    logger.error('Database connection failed:', error);
    return false;
  }
}

// Graceful shutdown
export async function disconnectDatabase(): Promise<void> {
  try {
    await prisma.$disconnect();
    logger.info('Database disconnected successfully');
  } catch (error) {
    logger.error('Error disconnecting from database:', error);
  }
}

// Database metrics for monitoring
export async function getDatabaseMetrics() {
  try {
    // Use sequential queries to avoid prepared statement conflicts in development
    const userCount = await prisma.user.count();
    const siteCount = await prisma.site.count();
    const analysisCount = await prisma.analysis.count();

    return {
      users: userCount,
      sites: siteCount,
      analyses: analysisCount,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    logger.error('Error getting database metrics:', error);
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
export default prisma;
