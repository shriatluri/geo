"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestLogger = void 0;
const logger_1 = require("../utils/logger");
const requestLogger = (req, res, next) => {
    const start = Date.now();
    // Log the incoming request
    logger_1.logger.http(`${req.method} ${req.url}`, {
        method: req.method,
        url: req.url,
        userAgent: req.get('User-Agent'),
        ip: req.ip,
        timestamp: new Date().toISOString(),
    });
    // Override res.end to log response
    const originalEnd = res.end;
    res.end = function (...args) {
        const duration = Date.now() - start;
        logger_1.logger.http(`${req.method} ${req.url} - ${res.statusCode} - ${duration}ms`, {
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            duration,
            timestamp: new Date().toISOString(),
        });
        // Call original end with all arguments
        return originalEnd.apply(this, args);
    };
    next();
};
exports.requestLogger = requestLogger;
//# sourceMappingURL=requestLogger.js.map