/**
 * Aurora-X Authentication API Routes
 * Handles user registration, login, token refresh, and profile management
 */

import { Router, type Request, Response } from 'express';
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

    // Validate required fields
    if (!username || !email || !password) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Username, email, and password are required'
      });
    }

    // Prevent non-admins from creating admin users via public endpoint
    const sanitizedRole = role === 'admin' ? 'user' : role;

    // Register user
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
  } catch (error: any) {
    console.error('[Auth API] Registration error:', error);
    
    return res.status(400).json({
      error: 'Registration Failed',
      message: error.message || 'Failed to register user'
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

    // Validate required fields
    if (!username || !password) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Username and password are required'
      });
    }

    // Authenticate user
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
  } catch (error: any) {
    console.error('[Auth API] Login error:', error);

    if (error.message === 'User account is disabled') {
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

    // Generate new access token
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
  } catch (error: any) {
    console.error('[Auth API] Token refresh error:', error);
    
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
router.get('/me', requireAuth, (req: AuthRequest, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'User not found in request'
      });
    }

    const user = getUserProfile(req.user.id);

    if (!user) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User profile not found'
      });
    }

    return res.json({
      user
    });
  } catch (error: any) {
    console.error('[Auth API] Get profile error:', error);
    
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
router.put('/me', requireAuth, async (req: AuthRequest, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'User not found in request'
      });
    }

    const { email }: UpdateUserData = req.body;

    // Users can only update their email via this endpoint
    // Password changes use separate endpoint for security
    const updatedUser = await updateUserProfile(req.user.id, { email });

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
  } catch (error: any) {
    console.error('[Auth API] Update profile error:', error);
    
    return res.status(400).json({
      error: 'Update Failed',
      message: error.message || 'Failed to update profile'
    });
  }
});

/**
 * POST /api/auth/change-password
 * Change current user's password
 */
router.post('/change-password', requireAuth, async (req: AuthRequest, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'User not found in request'
      });
    }

    const { currentPassword, newPassword } = req.body;

    // Validate required fields
    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Current password and new password are required'
      });
    }

    // Change password
    const success = await changePassword(req.user.id, currentPassword, newPassword);

    if (!success) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'User not found'
      });
    }

    return res.json({
      message: 'Password changed successfully'
    });
  } catch (error: any) {
    console.error('[Auth API] Password change error:', error);
    
    if (error.message === 'Current password is incorrect') {
      return res.status(401).json({
        error: 'Invalid Password',
        message: 'Current password is incorrect'
      });
    }
    
    return res.status(400).json({
      error: 'Password Change Failed',
      message: error.message || 'Failed to change password'
    });
  }
});

/**
 * POST /api/auth/logout
 * Logout user (client should delete tokens)
 */
router.post('/logout', requireAuth, (req: AuthRequest, res: Response) => {
  // In a stateless JWT system, logout is handled client-side by deleting tokens
  // If you implement token blacklisting in the future, add it here
  
  console.log(`[Auth API] User logged out: ${req.user?.username}`);
  
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
router.get('/users', requireAuth, requireAdmin, (req: Request, res: Response) => {
  try {
    const includeInactive = req.query.includeInactive === 'true';
    const users = listAllUsers(includeInactive);

    return res.json({
      users,
      count: users.length
    });
  } catch (error: any) {
    console.error('[Auth API] List users error:', error);
    
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
router.get('/users/stats', requireAuth, requireAdmin, (req: Request, res: Response) => {
  try {
    const stats = getUserStats();

    return res.json({
      stats
    });
  } catch (error: any) {
    console.error('[Auth API] Get stats error:', error);
    
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
router.get('/users/:id', requireAuth, requireAdmin, (req: Request, res: Response) => {
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
  } catch (error: any) {
    console.error('[Auth API] Get user error:', error);
    
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
router.put('/users/:id', requireAuth, requireAdmin, async (req: Request, res: Response) => {
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
  } catch (error: any) {
    console.error('[Auth API] Update user error:', error);
    
    return res.status(400).json({
      error: 'Update Failed',
      message: error.message || 'Failed to update user'
    });
  }
});

/**
 * POST /api/auth/users
 * Create new user (admin only)
 */
router.post('/users', requireAuth, requireAdmin, async (req: Request, res: Response) => {
  try {
    const { username, email, password, role }: CreateUserData = req.body;

    // Validate required fields
    if (!username || !email || !password) {
      return res.status(400).json({
        error: 'Validation Error',
        message: 'Username, email, and password are required'
      });
    }

    // Admins can create users with any role
    const result = await registerUser({
      username,
      email,
      password,
      role: role || 'user'
    });

    return res.status(201).json({
      message: 'User created successfully',
      user: result.user
      // Don't return tokens for admin-created users
    });
  } catch (error: any) {
    console.error('[Auth API] Create user error:', error);
    
    return res.status(400).json({
      error: 'User Creation Failed',
      message: error.message || 'Failed to create user'
    });
  }
});

// ══════════════════════════════════════════════════════════════
// 📤 EXPORT ROUTER
// ══════════════════════════════════════════════════════════════

export default router;
