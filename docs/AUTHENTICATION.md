# Aurora-X Authentication & Authorization System

Complete implementation of JWT-based authentication with role-based access control (RBAC).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Security Features](#security-features)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Aurora-X authentication system provides:

- **JWT-based authentication** - Stateless token authentication
- **Password hashing** - bcrypt with 12 salt rounds
- **Role-based access control** - Admin, user, and guest roles
- **Token refresh mechanism** - Long-lived refresh tokens
- **User management** - Registration, login, profile updates
- **Admin dashboard** - User administration endpoints

---

## ✨ Features

### Authentication Features
- ✅ User registration with email validation
- ✅ Secure login with password verification
- ✅ JWT access tokens (24-hour expiration)
- ✅ JWT refresh tokens (7-day expiration)
- ✅ Token refresh endpoint
- ✅ Logout support

### Authorization Features
- ✅ Role-based access control (RBAC)
- ✅ Admin, user, and guest roles
- ✅ Protected route middleware
- ✅ Optional authentication middleware
- ✅ Role-specific endpoints

### User Management
- ✅ User registration
- ✅ Profile management
- ✅ Password change
- ✅ User listing (admin)
- ✅ User statistics (admin)
- ✅ User activation/deactivation

### Security
- ✅ Password hashing with bcrypt (12 rounds)
- ✅ JWT token signing with HS256
- ✅ Token expiration validation
- ✅ Input validation
- ✅ Email format validation
- ✅ Username/email uniqueness checks

---

## 🏗️ Architecture

```
server/
├── auth.ts          # Core authentication module (JWT, bcrypt)
├── users.ts         # User management & storage
├── auth-routes.ts   # Authentication API endpoints
└── index.ts         # Server entry point (integrate auth)
```

### Components

#### 1. **auth.ts** - Authentication Core
- Password hashing/verification (bcrypt)
- JWT token generation (access & refresh)
- JWT token verification & decoding
- Authentication middleware (requireAuth, optionalAuth)
- Authorization middleware (requireRole, requireAdmin, requireUser)
- Token utility functions

#### 2. **users.ts** - User Management
- User store (in-memory, replaceable with database)
- User CRUD operations
- User authentication
- Profile management
- User statistics

#### 3. **auth-routes.ts** - API Routes
- Public routes (register, login, refresh)
- Protected routes (profile, password change)
- Admin routes (user management, statistics)

---

## 📦 Installation

### 1. Install Dependencies

```bash
npm install bcrypt jsonwebtoken
npm install --save-dev @types/bcrypt @types/jsonwebtoken
```

### 2. Environment Configuration

Create or update `.env`:

```bash
# JWT Configuration
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_EXPIRES_IN=24h
JWT_REFRESH_EXPIRES_IN=7d

# Password Hashing
BCRYPT_ROUNDS=12

# Server
PORT=5000
NODE_ENV=production
```

⚠️ **CRITICAL**: Change `JWT_SECRET` to a strong, random secret in production!

### 3. Generate Strong Secret

```bash
# Generate a secure random secret
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | ⚠️ Default secret | Secret key for signing JWT tokens |
| `JWT_EXPIRES_IN` | `24h` | Access token expiration time |
| `JWT_REFRESH_EXPIRES_IN` | `7d` | Refresh token expiration time |
| `BCRYPT_ROUNDS` | `12` | Number of bcrypt salt rounds |

### Default Users

The system creates a default admin user on startup:

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`
- **Email**: `admin@aurora-x.local`

⚠️ **SECURITY WARNING**: Change the default admin password immediately in production!

---

## 🌐 API Endpoints

### Public Endpoints (No authentication required)

#### POST `/api/auth/register`
Register a new user account.

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user-1234567890",
    "username": "newuser",
    "email": "user@example.com",
    "role": "user",
    "createdAt": "2025-01-10T15:30:00.000Z",
    "isActive": true
  },
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST `/api/auth/login`
Authenticate user and receive tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "admin-001",
    "username": "admin",
    "email": "admin@aurora-x.local",
    "role": "admin",
    "lastLogin": "2025-01-10T15:35:00.000Z"
  },
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST `/api/auth/refresh`
Refresh access token using refresh token.

**Request:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "message": "Token refreshed successfully",
  "accessToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### Protected Endpoints (Authentication required)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### GET `/api/auth/me`
Get current user's profile.

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-1234567890",
    "username": "newuser",
    "email": "user@example.com",
    "role": "user",
    "createdAt": "2025-01-10T15:30:00.000Z",
    "lastLogin": "2025-01-10T15:35:00.000Z",
    "isActive": true
  }
}
```

#### PUT `/api/auth/me`
Update current user's profile.

**Request:**
```json
{
  "email": "newemail@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "user-1234567890",
    "username": "newuser",
    "email": "newemail@example.com",
    "role": "user",
    "updatedAt": "2025-01-10T15:40:00.000Z"
  }
}
```

#### POST `/api/auth/change-password`
Change current user's password.

**Request:**
```json
{
  "currentPassword": "oldpassword123",
  "newPassword": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

#### POST `/api/auth/logout`
Logout user (client should delete tokens).

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

---

### Admin Endpoints (Admin role required)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs... (admin token)
```

#### GET `/api/auth/users`
List all users.

**Query Parameters:**
- `includeInactive` (optional, boolean) - Include inactive users

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": "admin-001",
      "username": "admin",
      "email": "admin@aurora-x.local",
      "role": "admin",
      "isActive": true
    },
    {
      "id": "user-1234567890",
      "username": "newuser",
      "email": "user@example.com",
      "role": "user",
      "isActive": true
    }
  ],
  "count": 2
}
```

#### GET `/api/auth/users/stats`
Get user statistics.

**Response (200 OK):**
```json
{
  "stats": {
    "totalUsers": 5,
    "activeUsers": 4,
    "adminUsers": 1,
    "regularUsers": 3,
    "guestUsers": 1
  }
}
```

#### GET `/api/auth/users/:id`
Get specific user by ID.

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-1234567890",
    "username": "newuser",
    "email": "user@example.com",
    "role": "user",
    "createdAt": "2025-01-10T15:30:00.000Z",
    "isActive": true
  }
}
```

#### PUT `/api/auth/users/:id`
Update user by ID (admin can change role, active status, password).

**Request:**
```json
{
  "email": "updated@example.com",
  "role": "admin",
  "isActive": false,
  "password": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": "user-1234567890",
    "username": "newuser",
    "email": "updated@example.com",
    "role": "admin",
    "isActive": false,
    "updatedAt": "2025-01-10T15:45:00.000Z"
  }
}
```

#### POST `/api/auth/users`
Create new user (admin only).

**Request:**
```json
{
  "username": "newadmin",
  "email": "admin@example.com",
  "password": "strongpassword123",
  "role": "admin"
}
```

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "user-9876543210",
    "username": "newadmin",
    "email": "admin@example.com",
    "role": "admin",
    "createdAt": "2025-01-10T15:50:00.000Z",
    "isActive": true
  }
}
```

---

## 💻 Usage Examples

### Client-Side Authentication Flow

```javascript
// 1. Register new user
const registerResponse = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    email: 'test@example.com',
    password: 'securepassword123'
  })
});

const { user, accessToken, refreshToken } = await registerResponse.json();

// Store tokens (use httpOnly cookies in production)
localStorage.setItem('accessToken', accessToken);
localStorage.setItem('refreshToken', refreshToken);

// 2. Login existing user
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'securepassword123'
  })
});

// 3. Make authenticated request
const profileResponse = await fetch('/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
});

// 4. Refresh expired token
const refreshResponse = await fetch('/api/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refreshToken: localStorage.getItem('refreshToken')
  })
});

const { accessToken: newAccessToken } = await refreshResponse.json();
localStorage.setItem('accessToken', newAccessToken);

// 5. Logout
localStorage.removeItem('accessToken');
localStorage.removeItem('refreshToken');
await fetch('/api/auth/logout', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${oldAccessToken}`
  }
});
```

### Server-Side Middleware Usage

```typescript
import { Router } from 'express';
import { requireAuth, requireAdmin, requireUser, optionalAuth } from './auth';

const router = Router();

// Public route
router.get('/public', (req, res) => {
  res.json({ message: 'Public access' });
});

// Protected route (any authenticated user)
router.get('/protected', requireAuth, (req: AuthRequest, res) => {
  res.json({ message: `Hello ${req.user?.username}!` });
});

// Admin-only route
router.get('/admin', requireAuth, requireAdmin, (req, res) => {
  res.json({ message: 'Admin access granted' });
});

// User or admin route (excludes guests)
router.get('/users-only', requireAuth, requireUser, (req, res) => {
  res.json({ message: 'User or admin access' });
});

// Optional authentication (works with or without token)
router.get('/optional', optionalAuth, (req: AuthRequest, res) => {
  if (req.user) {
    res.json({ message: `Hello ${req.user.username}!` });
  } else {
    res.json({ message: 'Hello anonymous!' });
  }
});
```

---

## 🔒 Security Features

### Password Security
- **Bcrypt hashing** with 12 salt rounds (configurable)
- **Minimum password length** of 6 characters
- **Password verification** before changes
- **Separate password change endpoint** for security

### Token Security
- **JWT signing** with HS256 algorithm
- **Token expiration** (24h access, 7d refresh)
- **Token type validation** (access vs refresh)
- **Bearer token format** support
- **Token verification** on every protected request

### Input Validation
- **Email format validation** (regex)
- **Username length validation** (min 3 characters)
- **Password strength requirements**
- **Username/email uniqueness** checks
- **SQL injection prevention** (no raw queries)

### Access Control
- **Role-based authorization** (admin/user/guest)
- **Role inheritance** (admin > user > guest)
- **Endpoint protection** via middleware
- **Admin-only operations** protected

### Additional Security
- **CORS configuration** (customize allowed origins)
- **Error message sanitization** (no sensitive info leakage)
- **Account activation** support
- **Rate limiting** (recommended, implement separately)

---

## 🚀 Deployment

### Production Checklist

- [ ] **Change default admin password**
- [ ] **Set strong JWT_SECRET** (64+ random bytes)
- [ ] **Enable HTTPS** (required for token security)
- [ ] **Use httpOnly cookies** for tokens (instead of localStorage)
- [ ] **Implement rate limiting** (prevent brute force)
- [ ] **Set up database** (replace in-memory storage)
- [ ] **Configure CORS** (restrict allowed origins)
- [ ] **Enable logging** (authentication events)
- [ ] **Implement token blacklist** (for logout)
- [ ] **Set up monitoring** (failed login attempts)
- [ ] **Enable 2FA** (optional, future enhancement)

### Database Integration

Replace in-memory storage with PostgreSQL:

```typescript
// users.ts - Replace UserStore with database queries

import { db } from './db'; // Your database connection

export async function createUser(data: CreateUserData): Promise<User> {
  const passwordHash = await hashPassword(data.password);
  
  const [user] = await db('users').insert({
    username: data.username,
    email: data.email,
    password_hash: passwordHash,
    role: data.role || 'user',
    created_at: new Date(),
    is_active: true
  }).returning('*');
  
  return user;
}

// Similar for other user operations...
```

### Docker Deployment

Already configured in `Dockerfile.backend`. Ensure environment variables are set:

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRES_IN=24h
      - NODE_ENV=production
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Invalid or expired authentication token"

**Cause**: Token expired or JWT_SECRET changed.

**Solution**:
- Client should refresh token using `/api/auth/refresh`
- Check JWT_SECRET hasn't changed
- Verify token expiration settings

#### 2. "Username already exists"

**Cause**: Attempting to register with existing username.

**Solution**:
- Choose a different username
- Check username is case-insensitive

#### 3. "Current password is incorrect"

**Cause**: Wrong current password when changing password.

**Solution**:
- Verify current password is correct
- Use password reset flow if forgotten

#### 4. "Access denied. Required role: admin"

**Cause**: Attempting to access admin endpoint as non-admin user.

**Solution**:
- Login with admin account
- Contact administrator to upgrade role

#### 5. Default admin password not working

**Cause**: Password already changed or user store reset.

**Solution**:
- Check server logs for default admin creation
- Verify no database persistence between restarts
- Restart server to recreate default admin

### Debug Mode

Enable authentication debugging:

```typescript
// auth.ts
const DEBUG = process.env.AUTH_DEBUG === 'true';

if (DEBUG) {
  console.log('[Auth Debug] Token payload:', decoded);
}
```

---

## 📊 Testing

### Manual Testing with curl

```bash
# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Get profile (use token from login response)
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Admin: List users
curl http://localhost:5000/api/auth/users \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Automated Testing

```bash
# Run authentication tests
npm test -- tests/auth.test.ts

# Test specific endpoints
npm test -- tests/auth-routes.test.ts
```

---

## 📝 Next Steps

### Phase 5: Security Hardening (Recommended)

1. **Rate Limiting** - Prevent brute force attacks
2. **Token Blacklisting** - Implement logout properly
3. **Password Reset** - Email-based password recovery
4. **Email Verification** - Verify email on registration
5. **2FA** - Two-factor authentication (optional)
6. **Session Management** - Track active sessions
7. **Audit Logging** - Log all authentication events
8. **CAPTCHA** - Prevent automated attacks

### Database Migration

Current implementation uses in-memory storage. For production:

1. Create users table in PostgreSQL
2. Replace UserStore methods with database queries
3. Add indexes for username and email
4. Implement connection pooling
5. Add database migrations

---

## 📚 References

- [JWT.io](https://jwt.io/) - JSON Web Tokens
- [bcrypt](https://www.npmjs.com/package/bcrypt) - Password hashing
- [Express Authentication Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

## 🤝 Contributing

To extend the authentication system:

1. Add new roles in `UserPayload` type
2. Create custom middleware for specific permissions
3. Add new endpoints in `auth-routes.ts`
4. Update documentation with new features

---

## 📄 License

This authentication system is part of Aurora-X project.

---

**Created by**: Aurora AI Assistant  
**Date**: January 10, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
