"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.analysisRateLimiter = exports.strictRateLimiter = exports.rateLimiter = void 0;
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const logger_1 = require("../utils/logger");
// General API rate limiter
exports.rateLimiter = (0, express_rate_limit_1.default)({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: {
        error: 'Too many requests from this IP, please try again later.',
        retryAfter: '15 minutes'
    },
    standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
    legacyHeaders: false, // Disable the `X-RateLimit-*` headers
    handler: (req, res) => {
        logger_1.logger.warn(`Rate limit exceeded for IP: ${req.ip}`, {
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
exports.strictRateLimiter = (0, express_rate_limit_1.default)({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // Limit each IP to 5 requests per windowMs
    message: {
        error: 'Too many attempts from this IP, please try again later.',
        retryAfter: '15 minutes'
    },
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
        logger_1.logger.warn(`Strict rate limit exceeded for IP: ${req.ip}`, {
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
exports.analysisRateLimiter = (0, express_rate_limit_1.default)({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 10, // Limit each IP to 10 analysis requests per hour
    message: {
        error: 'Too many analysis requests from this IP, please try again later.',
        retryAfter: '1 hour'
    },
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
        logger_1.logger.warn(`Analysis rate limit exceeded for IP: ${req.ip}`, {
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
//# sourceMappingURL=rateLimiter.js.map