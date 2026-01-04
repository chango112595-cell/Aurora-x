/**
 * Aurora-X Authentication API Routes
 * Handles user registration, login, token refresh, and profile management
 */

import { Router, type Request, Response, type RequestHandler } from 'express';
import {
  requireAuth,
  requireAdmin,
  refreshAccessToken,
  type AuthRequest
} from './auth';
import {
  registerUser,
  loginUser,
  getUserProfile,
  updateUserProfile,
  changePassword,
  listAllUsers,
  getUserStats,
  type CreateUserData,
  type LoginCredentials,
  type UpdateUserData
} from './users';

const router = Router();

// ══════════════════════════════════════════════════════════════
// 🔓 PUBLIC ROUTES (No authentication required)
// ══════════════════════════════════════════════════════════════

/**
 * POST /api/auth/register
 * Register a new user account
 */
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { username, email, password, role }: CreateUserData = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Username, email, and password are required'
      });
    }

    const sanitizedRole = role === 'admin' ? 'user' : role;

    const result = await registerUser({
      username,
      email,
      password,
      role: sanitizedRole
    });

    return res.status(201).json({
      message: 'User registered successfully',
      user: result.user,
      accessToken: result.tokens.accessToken,
      refreshToken: result.tokens.refreshToken
    });
  } catch (error: unknown) {
    const err = error as Error;
    
    return res.status(400).json({
      error: 'Registration Failed',
      message: err.message || 'Failed to register user'
    });
  }
});

/**
 * POST /api/auth/login
 * Authenticate user and return tokens
 */
router.post('/login', async (req: Request, res: Response) => {
  try {
    const { username, password }: LoginCredentials = req.body;

    if (!username || !password) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Username and password are required'
      });
    }

    const result = await loginUser({ username, password });

    if (!result) {
      return res.status(401).json({
        error: 'Authentication Failed',
        message: 'Invalid username or password'
      });
    }

    return res.json({
      message: 'Login successful',
      user: result.user,
      accessToken: result.tokens.accessToken,
      refreshToken: result.tokens.refreshToken
    });
  } catch (error: unknown) {
    const err = error as Error;

    if (err.message === 'User account is disabled') {
      return res.status(403).json({
        error: 'Account Disabled',
        message: 'Your account has been disabled. Please contact an administrator.'
      });
    }
    
    return res.status(500).json({
      error: 'Login Failed',
      message: 'An error occurred during login'
    });
  }
});

/**
 * POST /api/auth/refresh
 * Refresh access token using refresh token
 */
router.post('/refresh', (req: Request, res: Response) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Refresh token is required'
      });
    }

    const newAccessToken = refreshAccessToken(refreshToken);

    if (!newAccessToken) {
      return res.status(401).json({
        error: 'Invalid Token',
        message: 'Invalid or expired refresh token'
      });
    }

    return res.json({
      message: 'Token refreshed successfully',
      accessToken: newAccessToken
    });
  } catch (error: unknown) {
    return res.status(500).json({
      error: 'Token Refresh Failed',
      message: 'An error occurred while refreshing token'
    });
  }
});

// ══════════════════════════════════════════════════════════════
// 🔐 PROTECTED ROUTES (Authentication required)
// ══════════════════════════════════════════════════════════════

/**
 * GET /api/auth/me
 * Get current user's profile
 */
router.get('/me', requireAuth as RequestHandler, (req: Request, res: Response) => {
  const authReq = req as AuthRequest;
  try {
    if (!authReq.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'User not found in request'
      });
    }

    const user = getUserProfile(authReq.user.id);

    if (!user) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User profile not found'
      });
    }

    return res.json({
      user
    });
  } catch (error: unknown) {
    return res.status(500).json({
      error: 'Failed to Fetch Profile',
      message: 'An error occurred while fetching user profile'
    });
  }
});

/**
 * PUT /api/auth/me
 * Update current user's profile
 */
router.put('/me', requireAuth as RequestHandler, async (req: Request, res: Response) => {
  const authReq = req as AuthRequest;
  try {
    if (!authReq.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'User not found in request'
      });
    }

    const { email }: UpdateUserData = req.body;

    const updatedUser = await updateUserProfile(authReq.user.id, { email });

    if (!updatedUser) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User profile not found'
      });
    }

    return res.json({
      message: 'Profile updated successfully',
      user: updatedUser
    });
  } catch (error: unknown) {
    const err = error as Error;
    
    return res.status(400).json({
      error: 'Update Failed',
      message: err.message || 'Failed to update profile'
    });
  }
});

/**
 * POST /api/auth/change-password
 * Change current user's password
 */
router.post('/change-password', requireAuth as RequestHandler, async (req: Request, res: Response) => {
  const authReq = req as AuthRequest;
  try {
    if (!authReq.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'User not found in request'
      });
    }

    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Current password and new password are required'
      });
    }

    const success = await changePassword(authReq.user.id, currentPassword, newPassword);

    if (!success) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User not found'
      });
    }

    return res.json({
      message: 'Password changed successfully'
    });
  } catch (error: unknown) {
    const err = error as Error;
    
    if (err.message === 'Current password is incorrect') {
      return res.status(401).json({
        error: 'Invalid Password',
        message: 'Current password is incorrect'
      });
    }
    
    return res.status(400).json({
      error: 'Password Change Failed',
      message: err.message || 'Failed to change password'
    });
  }
});

/**
 * POST /api/auth/logout
 * Logout user (client should delete tokens)
 */
router.post('/logout', requireAuth as RequestHandler, (req: Request, res: Response) => {
  return res.json({
    message: 'Logout successful'
  });
});

// ══════════════════════════════════════════════════════════════
// 👑 ADMIN ROUTES (Admin role required)
// ══════════════════════════════════════════════════════════════

/**
 * GET /api/auth/users
 * List all users (admin only)
 */
router.get('/users', requireAuth as RequestHandler, requireAdmin as RequestHandler, (req: Request, res: Response) => {
  try {
    const includeInactive = req.query.includeInactive === 'true';
    const users = listAllUsers(includeInactive);

    return res.json({
      users,
      count: users.length
    });
  } catch (error: unknown) {
    return res.status(500).json({
      error: 'Failed to List Users',
      message: 'An error occurred while fetching users'
    });
  }
});

/**
 * GET /api/auth/users/stats
 * Get user statistics (admin only)
 */
router.get('/users/stats', requireAuth as RequestHandler, requireAdmin as RequestHandler, (req: Request, res: Response) => {
  try {
    const stats = getUserStats();

    return res.json({
      stats
    });
  } catch (error: unknown) {
    return res.status(500).json({
      error: 'Failed to Get Statistics',
      message: 'An error occurred while fetching statistics'
    });
  }
});

/**
 * GET /api/auth/users/:id
 * Get specific user by ID (admin only)
 */
router.get('/users/:id', requireAuth as RequestHandler, requireAdmin as RequestHandler, (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const user = getUserProfile(id);

    if (!user) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User not found'
      });
    }

    return res.json({
      user
    });
  } catch (error: unknown) {
    return res.status(500).json({
      error: 'Failed to Fetch User',
      message: 'An error occurred while fetching user'
    });
  }
});

/**
 * PUT /api/auth/users/:id
 * Update user by ID (admin only)
 */
router.put('/users/:id', requireAuth as RequestHandler, requireAdmin as RequestHandler, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { email, role, isActive, password }: UpdateUserData = req.body;

    const updatedUser = await updateUserProfile(id, {
      email,
      role,
      isActive,
      password
    });

    if (!updatedUser) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User not found'
      });
    }

    return res.json({
      message: 'User updated successfully',
      user: updatedUser
    });
  } catch (error: unknown) {
    const err = error as Error;
    
    return res.status(400).json({
      error: 'Update Failed',
      message: err.message || 'Failed to update user'
    });
  }
});

/**
 * POST /api/auth/users
 * Create new user (admin only)
 */
router.post('/users', requireAuth as RequestHandler, requireAdmin as RequestHandler, async (req: Request, res: Response) => {
  try {
    const { username, email, password, role }: CreateUserData = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Username, email, and password are required'
      });
    }

    const result = await registerUser({
      username,
      email,
      password,
      role: role || 'user'
    });

    return res.status(201).json({
      message: 'User created successfully',
      user: result.user
    });
  } catch (error: unknown) {
    const err = error as Error;
    
    return res.status(400).json({
      error: 'User Creation Failed',
      message: err.message || 'Failed to create user'
    });
  }
});

// ══════════════════════════════════════════════════════════════
// 📤 EXPORT ROUTER
// ══════════════════════════════════════════════════════════════

export default router;
