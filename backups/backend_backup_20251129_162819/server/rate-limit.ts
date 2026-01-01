/**
 * Rate Limiting Middleware
 * Protects API endpoints from abuse and excessive requests
 */

import rateLimit from 'express-rate-limit';

// General API rate limiter
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});

// Stricter rate limit for authentication endpoints
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // Limit each IP to 10 login attempts per windowMs
  message: 'Too many login attempts from this IP, please try again after 15 minutes.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Aurora chat rate limiter - more generous for conversations
export const chatLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 20, // 20 messages per minute
  message: 'Slow down! You can send up to 20 messages per minute.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Synthesis/code generation rate limiter
export const synthesisLimiter = rateLimit({
  windowMs: 5 * 60 * 1000, // 5 minutes
  max: 10, // 10 synthesis requests per 5 minutes
  message: 'Code synthesis limit reached. Please wait a few minutes before trying again.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Search rate limiter
export const searchLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 30, // 30 searches per minute
  message: 'Search limit reached. Please wait a moment before searching again.',
  standardHeaders: true,
  legacyHeaders: false,
});
