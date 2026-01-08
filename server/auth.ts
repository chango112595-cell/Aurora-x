/**
 * Aurora-X Authentication Module
 * JWT-based authentication with bcrypt password hashing
 * Implements secure token generation and validation
 */

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { Request, Response, NextFunction } from 'express';
import { randomBytes } from 'crypto';
import fs from 'fs';
import path from 'path';

// ══════════════════════════════════════════════════════════════
// 🔐 CONFIGURATION
// ══════════════════════════════════════════════════════════════

const SECRETS_DIR = process.env.AURORA_SECRETS_DIR || path.join(process.cwd(), 'secrets');

function loadJwtSecret(): string {
  const envSecret = process.env.JWT_SECRET?.trim();
  if (envSecret && envSecret !== 'change-this-in-production-to-a-strong-secret') {
    return envSecret;
  }

  const secretPath = path.join(SECRETS_DIR, 'jwt_secret');

  try {
    if (fs.existsSync(secretPath)) {
      const storedSecret = fs.readFileSync(secretPath, 'utf8').trim();
      if (storedSecret) {
        return storedSecret;
      }
    }

    fs.mkdirSync(SECRETS_DIR, { recursive: true });
    const generatedSecret = randomBytes(48).toString('hex');
    fs.writeFileSync(secretPath, generatedSecret, { mode: 0o600 });
    console.warn(`[Auth] Generated secure JWT secret at ${secretPath}. Set JWT_SECRET to override.`);
    return generatedSecret;
  } catch (error) {
    throw new Error(
      'JWT secret unavailable. Set JWT_SECRET or ensure the secrets directory is writable.',
    );
  }
}

const JWT_SECRET = loadJwtSecret();
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';
const JWT_REFRESH_EXPIRES_IN = process.env.JWT_REFRESH_EXPIRES_IN || '7d';
const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12');

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
  iat?: number;
  exp?: number;
  type: 'access' | 'refresh';
}

export interface AuthRequest extends Request {
  user?: UserPayload;
}

interface JwtError extends Error {
  name: 'TokenExpiredError' | 'JsonWebTokenError' | string;
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
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
    const token = extractToken(req);

    if (!token) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Authentication token is required'
      });
      return;
    }

    const decoded = verifyToken(token);

    if (!decoded) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid or expired authentication token'
      });
      return;
    }

    if (decoded.type !== 'access') {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid token type. Access token required.'
      });
      return;
    }

    req.user = {
      id: decoded.id,
      username: decoded.username,
      email: decoded.email,
      role: decoded.role
    };

    next();
  } catch (error: unknown) {
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

    next();
  } catch (error: unknown) {
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

    if (decoded.type !== 'refresh') {
      return null;
    }

    const user: UserPayload = {
      id: decoded.id,
      username: decoded.username,
      email: decoded.email,
      role: decoded.role
    };

    const newAccessToken = generateAccessToken(user);
    return newAccessToken;
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
  hashPassword,
  verifyPassword,
  generateAccessToken,
  generateRefreshToken,
  generateTokens,
  verifyToken,
  extractToken,
  requireAuth,
  optionalAuth,
  requireRole,
  requireAdmin,
  requireUser,
  refreshAccessToken,
  getTokenExpiration,
  isTokenExpired,
  getTokenTTL
};
