"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.asyncHandler = exports.errorHandler = exports.CustomError = void 0;
const logger_1 = require("../utils/logger");
class CustomError extends Error {
    constructor(message, statusCode = 500) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = true;
        this.name = 'CustomError';
        Error.captureStackTrace(this, this.constructor);
    }
}
exports.CustomError = CustomError;
// Error handler middleware
const errorHandler = (err, req, res, next) => {
    let error = { ...err };
    error.message = err.message;
    // Log error
    logger_1.logger.error(`Error ${err.statusCode || 500}: ${err.message}`, {
        error: err,
        request: {
            method: req.method,
            url: req.url,
            headers: req.headers,
            body: req.body,
        },
    });
    // Mongoose bad ObjectId
    if (err.name === 'CastError') {
        const message = 'Resource not found';
        error = new CustomError(message, 404);
    }
    // Mongoose duplicate key
    if (err.name === 'MongoError' && err.code === 11000) {
        const message = 'Duplicate field value entered';
        error = new CustomError(message, 400);
    }
    // Mongoose validation error
    if (err.name === 'ValidationError') {
        const message = Object.values(err.errors).map((val) => val.message);
        error = new CustomError(message.join(', '), 400);
    }
    // JWT errors
    if (err.name === 'JsonWebTokenError') {
        const message = 'Invalid token';
        error = new CustomError(message, 401);
    }
    if (err.name === 'TokenExpiredError') {
        const message = 'Token expired';
        error = new CustomError(message, 401);
    }
    // Prisma errors
    if (err.name === 'PrismaClientKnownRequestError') {
        const prismaError = err;
        if (prismaError.code === 'P2002') {
            const message = 'Duplicate field value entered';
            error = new CustomError(message, 400);
        }
        else if (prismaError.code === 'P2025') {
            const message = 'Record not found';
            error = new CustomError(message, 404);
        }
    }
    res.status(error.statusCode || 500).json({
        success: false,
        error: {
            message: error.message || 'Server Error',
            ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
        },
        timestamp: new Date().toISOString(),
    });
};
exports.errorHandler = errorHandler;
// Async error handler wrapper
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
exports.asyncHandler = asyncHandler;
//# sourceMappingURL=errorHandler.js.map