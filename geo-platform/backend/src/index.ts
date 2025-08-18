import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import Redis from 'ioredis';
import { Request, Response } from 'express';

import { logger } from './utils/logger';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';
import { rateLimiter } from './middleware/rateLimiter';
import { apiRoutes } from './gateway/routes';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const server = createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Set port
const PORT = process.env.PORT || 8000;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// CORS configuration
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3000",
  credentials: true,
}));

// Compression middleware
app.use(compression());

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(requestLogger);

// Rate limiting
app.use('/api', rateLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'geo-backend',
    version: process.env.npm_package_version || '1.0.0'
  });
});

// Redis Connection
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

async function performAIAnalysis(domain: string) {
  // Placeholder for the actual AI analysis logic
  return { domain, analysis: 'AI analysis result' };
}

async function getAIAnalysis(domain: string) {
  const cacheKey = `ai-analysis:${domain}`;
  const cachedResult = await redis.get(cacheKey);
  if (cachedResult) {
    logger.info('Cache hit');
    return JSON.parse(cachedResult);
  }

  logger.info('Cache miss');
  const analysisResult = await performAIAnalysis(domain);
  await redis.set(cacheKey, JSON.stringify(analysisResult), 'EX', 3600);

  return analysisResult;
}

async function handleRequest(req: Request, res: Response) {
  const domain = req.query.domain as string;
  try {
    const analysisResult = await getAIAnalysis(domain);
    res.json(analysisResult);
  } catch (error) {
    logger.error('Error fetching analysis', error);
    res.status(500).send('Error fetching analysis');
  }
}

app.get('/api/analyze', handleRequest);

// API routes
app.use('/api', apiRoutes);

// Socket.IO connection handling
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);
  
  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
  });
  
  // Join room for site-specific updates
  socket.on('join-site', (siteId: string) => {
    socket.join(`site-${siteId}`);
    logger.info(`Client ${socket.id} joined room: site-${siteId}`);
  });
});

// Make io available globally for other modules
app.set('io', io);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`,
    timestamp: new Date().toISOString()
  });
});

// Global error handler (must be last)
app.use(errorHandler);

// Start server
server.listen(PORT, () => {
  logger.info(`🚀 GEO Backend server running on port ${PORT}`);
  logger.info(`📊 Health check available at http://localhost:${PORT}/health`);
  logger.info(`🌐 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Process terminated');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  server.close(() => {
    logger.info('Process terminated');
    process.exit(0);
  });
});

export { app, server, io };
