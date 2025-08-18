import rateLimit from 'express-rate-limit';
import { logger } from '../utils/logger';

// General API rate limiter
export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  handler: (req, res) => {
    logger.warn(`Rate limit exceeded for IP: ${req.ip}`, {
      ip: req.ip,
      url: req.url,
      userAgent: req.get('User-Agent'),
    });
    
    res.status(429).json({
      error: 'Too many requests from this IP, please try again later.',
      retryAfter: '15 minutes',
      timestamp: new Date().toISOString()
    });
  },
});

// Strict rate limiter for sensitive endpoints
export const strictRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  message: {
    error: 'Too many attempts from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    logger.warn(`Strict rate limit exceeded for IP: ${req.ip}`, {
      ip: req.ip,
      url: req.url,
      userAgent: req.get('User-Agent'),
    });
    
    res.status(429).json({
      error: 'Too many attempts from this IP, please try again later.',
      retryAfter: '15 minutes',
      timestamp: new Date().toISOString()
    });
  },
});

// Analysis rate limiter (for expensive operations)
export const analysisRateLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 10, // Limit each IP to 10 analysis requests per hour
  message: {
    error: 'Too many analysis requests from this IP, please try again later.',
    retryAfter: '1 hour'
  },
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    logger.warn(`Analysis rate limit exceeded for IP: ${req.ip}`, {
      ip: req.ip,
      url: req.url,
      userAgent: req.get('User-Agent'),
    });
    
    res.status(429).json({
      error: 'Too many analysis requests from this IP, please try again later.',
      retryAfter: '1 hour',
      timestamp: new Date().toISOString()
    });
  },
});
