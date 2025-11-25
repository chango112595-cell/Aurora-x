/**
 * Aurora-X Authentication Module
 * JWT-based authentication with bcrypt password hashing
 * Implements secure token generation and validation
 */

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { Request, Response, NextFunction } from 'express';

// ══════════════════════════════════════════════════════════════
// 🔐 CONFIGURATION
// ══════════════════════════════════════════════════════════════

const JWT_SECRET = process.env.JWT_SECRET || 'change-this-in-production-to-a-strong-secret';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h'; // Token expiration
const JWT_REFRESH_EXPIRES_IN = process.env.JWT_REFRESH_EXPIRES_IN || '7d'; // Refresh token expiration
const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12'); // Salt rounds for bcrypt

// Warn if using default secret
if (JWT_SECRET === 'change-this-in-production-to-a-strong-secret') {
  console.warn('[Auth] ⚠️  WARNING: Using default JWT secret. Set JWT_SECRET environment variable in production!');
}

// ══════════════════════════════════════════════════════════════
// 📦 TYPES
// ══════════════════════════════════════════════════════════════

export interface UserPayload {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

export interface TokenPayload extends UserPayload {
  iat?: number; // Issued at
  exp?: number; // Expiration
  type: 'access' | 'refresh';
}

export interface AuthRequest extends Request {
  user?: UserPayload;
}

// ══════════════════════════════════════════════════════════════
// 🔑 PASSWORD HASHING
// ══════════════════════════════════════════════════════════════

/**
 * Hash a plaintext password using bcrypt
 * @param password - The plaintext password to hash
 * @returns Promise resolving to the hashed password
 */
export async function hashPassword(password: string): Promise<string> {
  try {
    const hash = await bcrypt.hash(password, BCRYPT_ROUNDS);
    return hash;
  } catch (error: any) {
    console.error('[Auth] Password hashing error:', error);
    throw new Error('Failed to hash password');
  }
}

/**
 * Verify a plaintext password against a hashed password
 * @param password - The plaintext password to verify
 * @param hash - The hashed password to compare against
 * @returns Promise resolving to true if password matches, false otherwise
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  try {
    const match = await bcrypt.compare(password, hash);
    return match;
  } catch (error: any) {
    console.error('[Auth] Password verification error:', error);
    return false;
  }
}

// ══════════════════════════════════════════════════════════════
// 🎫 JWT TOKEN GENERATION
// ══════════════════════════════════════════════════════════════

/**
 * Generate a JWT access token for a user
 * @param user - The user payload to encode in the token
 * @returns The generated JWT token
 */
export function generateAccessToken(user: UserPayload): string {
  try {
    const payload: TokenPayload = {
      ...user,
      type: 'access'
    };

    const token = jwt.sign(payload, JWT_SECRET, {
      expiresIn: JWT_EXPIRES_IN,
      algorithm: 'HS256'
    } as jwt.SignOptions);

    return token;
  } catch (error: any) {
    console.error('[Auth] Token generation error:', error);
    throw new Error('Failed to generate access token');
  }
}

/**
 * Generate a JWT refresh token for a user
 * @param user - The user payload to encode in the token
 * @returns The generated refresh token
 */
export function generateRefreshToken(user: UserPayload): string {
  try {
    const payload: TokenPayload = {
      ...user,
      type: 'refresh'
    };

    const token = jwt.sign(payload, JWT_SECRET, {
      expiresIn: JWT_REFRESH_EXPIRES_IN,
      algorithm: 'HS256'
    } as jwt.SignOptions);

    return token;
  } catch (error: any) {
    console.error('[Auth] Refresh token generation error:', error);
    throw new Error('Failed to generate refresh token');
  }
}

/**
 * Generate both access and refresh tokens for a user
 * @param user - The user payload to encode in the tokens
 * @returns Object containing both access and refresh tokens
 */
export function generateTokens(user: UserPayload): { accessToken: string; refreshToken: string } {
  return {
    accessToken: generateAccessToken(user),
    refreshToken: generateRefreshToken(user)
  };
}

// ══════════════════════════════════════════════════════════════
// ✅ JWT TOKEN VERIFICATION
// ══════════════════════════════════════════════════════════════

/**
 * Verify and decode a JWT token
 * @param token - The JWT token to verify
 * @returns The decoded token payload if valid, null otherwise
 */
export function verifyToken(token: string): TokenPayload | null {
  try {
    const decoded = jwt.verify(token, JWT_SECRET, {
      algorithms: ['HS256']
    }) as TokenPayload;

    return decoded;
  } catch (error: any) {
    if (error.name === 'TokenExpiredError') {
      console.log('[Auth] Token expired:', error.message);
    } else if (error.name === 'JsonWebTokenError') {
      console.log('[Auth] Invalid token:', error.message);
    } else {
      console.error('[Auth] Token verification error:', error);
    }
    return null;
  }
}

/**
 * Extract token from Authorization header (Bearer token)
 * @param req - Express request object
 * @returns The extracted token or null if not found
 */
export function extractToken(req: Request): string | null {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return null;
  }

  // Support both "Bearer TOKEN" and just "TOKEN"
  if (authHeader.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }

  return authHeader;
}

// ══════════════════════════════════════════════════════════════
// 🛡️ AUTHENTICATION MIDDLEWARE
// ══════════════════════════════════════════════════════════════

/**
 * Middleware to require authentication for protected routes
 * Validates JWT token and attaches user to request
 */
export function requireAuth(req: AuthRequest, res: Response, next: NextFunction): void {
  try {
    // Extract token from header
    const token = extractToken(req);

    if (!token) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication token is required'
      });
      return;
    }

    // Verify token
    const decoded = verifyToken(token);

    if (!decoded) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid or expired authentication token'
      });
      return;
    }

    // Check token type (should be access token)
    if (decoded.type !== 'access') {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid token type. Access token required.'
      });
      return;
    }

    // Attach user to request
    req.user = {
      id: decoded.id,
      username: decoded.username,
      email: decoded.email,
      role: decoded.role
    };

    // Continue to next middleware/route handler
    next();
  } catch (error: any) {
    console.error('[Auth] Authentication middleware error:', error);
    res.status(500).json({
      error: 'Internal Server Error',
      message: 'Authentication failed'
    });
  }
}

/**
 * Middleware to optionally authenticate (for routes that work with or without auth)
 * Attaches user to request if valid token provided, otherwise continues without user
 */
export function optionalAuth(req: AuthRequest, res: Response, next: NextFunction): void {
  try {
    const token = extractToken(req);

    if (token) {
      const decoded = verifyToken(token);

      if (decoded && decoded.type === 'access') {
        req.user = {
          id: decoded.id,
          username: decoded.username,
          email: decoded.email,
          role: decoded.role
        };
      }
    }

    // Continue regardless of auth status
    next();
  } catch (error: any) {
    console.error('[Auth] Optional authentication middleware error:', error);
    // Continue even on error
    next();
  }
}

// ══════════════════════════════════════════════════════════════
// 🔐 ROLE-BASED ACCESS CONTROL (RBAC)
// ══════════════════════════════════════════════════════════════

/**
 * Middleware to require a specific role for access
 * Must be used AFTER requireAuth middleware
 * @param allowedRoles - Array of roles that are allowed access
 */
export function requireRole(...allowedRoles: ('admin' | 'user' | 'guest')[]): 
  (req: AuthRequest, res: Response, next: NextFunction) => void {
  
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication required'
      });
      return;
    }

    if (!allowedRoles.includes(req.user.role)) {
      res.status(403).json({
        error: 'Forbidden',
        message: `Access denied. Required role: ${allowedRoles.join(' or ')}`
      });
      return;
    }

    next();
  };
}

/**
 * Check if user has admin role
 * Convenience function for requireRole('admin')
 */
export const requireAdmin = requireRole('admin');

/**
 * Check if user has admin or user role (excludes guests)
 * Convenience function for requireRole('admin', 'user')
 */
export const requireUser = requireRole('admin', 'user');

// ══════════════════════════════════════════════════════════════
// 🔄 TOKEN REFRESH
// ══════════════════════════════════════════════════════════════

/**
 * Validate refresh token and generate new access token
 * @param refreshToken - The refresh token to validate
 * @returns New access token if refresh token is valid, null otherwise
 */
export function refreshAccessToken(refreshToken: string): string | null {
  try {
    const decoded = verifyToken(refreshToken);

    if (!decoded) {
      return null;
    }

    // Check token type (should be refresh token)
    if (decoded.type !== 'refresh') {
      console.log('[Auth] Invalid token type for refresh:', decoded.type);
      return null;
    }

    // Generate new access token with same user data
    const user: UserPayload = {
      id: decoded.id,
      username: decoded.username,
      email: decoded.email,
      role: decoded.role
    };

    const newAccessToken = generateAccessToken(user);
    return newAccessToken;
  } catch (error: any) {
    console.error('[Auth] Token refresh error:', error);
    return null;
  }
}

// ══════════════════════════════════════════════════════════════
// 📊 UTILITY FUNCTIONS
// ══════════════════════════════════════════════════════════════

/**
 * Get token expiration timestamp from a JWT
 * @param token - The JWT token to inspect
 * @returns Expiration timestamp (Unix epoch) or null if invalid
 */
export function getTokenExpiration(token: string): number | null {
  try {
    const decoded = jwt.decode(token) as TokenPayload | null;
    return decoded?.exp || null;
  } catch (error: any) {
    return null;
  }
}

/**
 * Check if a token is expired
 * @param token - The JWT token to check
 * @returns True if expired, false if still valid
 */
export function isTokenExpired(token: string): boolean {
  const exp = getTokenExpiration(token);
  if (!exp) return true;
  
  return Date.now() >= exp * 1000;
}

/**
 * Get remaining time until token expiration
 * @param token - The JWT token to check
 * @returns Remaining seconds until expiration, 0 if expired or invalid
 */
export function getTokenTTL(token: string): number {
  const exp = getTokenExpiration(token);
  if (!exp) return 0;
  
  const remaining = Math.floor(exp - (Date.now() / 1000));
  return Math.max(0, remaining);
}

// ══════════════════════════════════════════════════════════════
// 📤 EXPORTS
// ══════════════════════════════════════════════════════════════

export default {
  // Password functions
  hashPassword,
  verifyPassword,

  // Token generation
  generateAccessToken,
  generateRefreshToken,
  generateTokens,

  // Token verification
  verifyToken,
  extractToken,

  // Middleware
  requireAuth,
  optionalAuth,
  requireRole,
  requireAdmin,
  requireUser,

  // Token refresh
  refreshAccessToken,

  // Utilities
  getTokenExpiration,
  isTokenExpired,
  getTokenTTL
};
