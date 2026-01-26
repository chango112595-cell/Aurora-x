/**
 * Aurora-X User Management Module
 * Handles user registration, authentication, and profile management
 * Uses in-memory storage (replace with database in production)
 */

import { randomBytes } from "crypto";
import fs from "fs";
import path from "path";

import {
  hashPassword,
  verifyPassword,
  generateTokens,
  UserPayload,
} from "./auth";

// ══════════════════════════════════════════════════════════════
// 📦 TYPES
// ══════════════════════════════════════════════════════════════

export interface User {
  id: string;
  username: string;
  email: string;
  passwordHash: string;
  role: "admin" | "user" | "guest";
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
  isActive: boolean;
}

export interface CreateUserData {
  username: string;
  email: string;
  password: string;
  role?: "admin" | "user" | "guest";
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface UpdateUserData {
  email?: string;
  password?: string;
  role?: "admin" | "user" | "guest";
  isActive?: boolean;
}

const SECRETS_DIR =
  process.env.AURORA_SECRETS_DIR || path.join(process.cwd(), "secrets");
const ADMIN_PASSWORD_PATH = path.join(SECRETS_DIR, "admin_password");

function resolveAdminPassword(): string {
  const envPassword = process.env.ADMIN_PASSWORD?.trim();
  // Require ADMIN_PASSWORD to be set - no hardcoded fallback
  if (!envPassword) {
    throw new Error(
      "ADMIN_PASSWORD environment variable is required. Set it to a secure value before starting the server."
    );
  }

  // Reject known insecure defaults
  const insecureDefaults = ["Alebec95!", "admin", "admin123", "password"];
  if (insecureDefaults.includes(envPassword)) {
    throw new Error(
      "ADMIN_PASSWORD cannot use insecure default values. Please set a strong password."
    );
  }

  return envPassword;
}

// ══════════════════════════════════════════════════════════════
// 💾 IN-MEMORY USER STORAGE
// ══════════════════════════════════════════════════════════════
// NOTE: In production, replace this with a proper database (PostgreSQL, MongoDB, etc.)

class UserStore {
  private users: Map<string, User> = new Map();
  private usernameIndex: Map<string, string> = new Map(); // username -> id
  private emailIndex: Map<string, string> = new Map(); // email -> id

  constructor() {
    // Initialize with default admin user (password: admin123)
    this.initializeDefaultAdmin();
  }

  private async initializeDefaultAdmin(): Promise<void> {
    try {
      const adminPassword = resolveAdminPassword();
      const adminPasswordHash = await hashPassword(adminPassword);

      const adminUser: User = {
        id: "admin-001",
        username: "admin",
        email: "admin@aurora-x.local",
        passwordHash: adminPasswordHash,
        role: "admin",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isActive: true,
      };

      this.users.set(adminUser.id, adminUser);
      this.usernameIndex.set(adminUser.username.toLowerCase(), adminUser.id);
      this.emailIndex.set(adminUser.email.toLowerCase(), adminUser.id);

      console.log(
        "[UserStore] ✅ Default admin user created (username: admin)",
      );
      if (!process.env.ADMIN_PASSWORD) {
        console.log(
          `[UserStore] 🔐 Admin password loaded from ${ADMIN_PASSWORD_PATH}. Set ADMIN_PASSWORD to rotate.`,
        );
      }
    } catch (error: any) {
      console.error("[UserStore] Failed to create default admin:", error);
    }
  }

  /**
   * Create a new user
   */
  async createUser(data: CreateUserData): Promise<User> {
    // Validate input
    if (!data.username || data.username.length < 3) {
      throw new Error("Username must be at least 3 characters long");
    }

    if (!data.email || !this.isValidEmail(data.email)) {
      throw new Error("Invalid email address");
    }

    if (!data.password || data.password.length < 6) {
      throw new Error("Password must be at least 6 characters long");
    }

    // Check for existing username
    if (this.usernameIndex.has(data.username.toLowerCase())) {
      throw new Error("Username already exists");
    }

    // Check for existing email
    if (this.emailIndex.has(data.email.toLowerCase())) {
      throw new Error("Email already exists");
    }

    // Hash password
    const passwordHash = await hashPassword(data.password);

    // Generate unique ID
    const id = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Create user object
    const user: User = {
      id,
      username: data.username,
      email: data.email,
      passwordHash,
      role: data.role || "user",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true,
    };

    // Store user
    this.users.set(id, user);
    this.usernameIndex.set(data.username.toLowerCase(), id);
    this.emailIndex.set(data.email.toLowerCase(), id);

    console.log(
      `[UserStore] Created new user: ${user.username} (${user.role})`,
    );

    return user;
  }

  /**
   * Find user by ID
   */
  findById(id: string): User | undefined {
    return this.users.get(id);
  }

  /**
   * Find user by username
   */
  findByUsername(username: string): User | undefined {
    const id = this.usernameIndex.get(username.toLowerCase());
    return id ? this.users.get(id) : undefined;
  }

  /**
   * Find user by email
   */
  findByEmail(email: string): User | undefined {
    const id = this.emailIndex.get(email.toLowerCase());
    return id ? this.users.get(id) : undefined;
  }

  /**
   * Authenticate user with username and password
   */
  async authenticate(credentials: LoginCredentials): Promise<User | null> {
    const user = this.findByUsername(credentials.username);

    if (!user) {
      return null;
    }

    if (!user.isActive) {
      throw new Error("User account is disabled");
    }

    const isPasswordValid = await verifyPassword(
      credentials.password,
      user.passwordHash,
    );

    if (!isPasswordValid) {
      return null;
    }

    // Update last login
    user.lastLogin = new Date().toISOString();
    user.updatedAt = new Date().toISOString();

    console.log(`[UserStore] User authenticated: ${user.username}`);

    return user;
  }

  /**
   * Update user data
   */
  async updateUser(id: string, data: UpdateUserData): Promise<User | null> {
    const user = this.users.get(id);

    if (!user) {
      return null;
    }

    // Update email if provided
    if (data.email) {
      if (!this.isValidEmail(data.email)) {
        throw new Error("Invalid email address");
      }

      // Check if email is already taken by another user
      const existingEmailId = this.emailIndex.get(data.email.toLowerCase());
      if (existingEmailId && existingEmailId !== id) {
        throw new Error("Email already exists");
      }

      // Remove old email index
      this.emailIndex.delete(user.email.toLowerCase());

      // Update email
      user.email = data.email;
      this.emailIndex.set(data.email.toLowerCase(), id);
    }

    // Update password if provided
    if (data.password) {
      if (data.password.length < 6) {
        throw new Error("Password must be at least 6 characters long");
      }
      user.passwordHash = await hashPassword(data.password);
    }

    // Update role if provided
    if (data.role) {
      user.role = data.role;
    }

    // Update active status if provided
    if (data.isActive !== undefined) {
      user.isActive = data.isActive;
    }

    user.updatedAt = new Date().toISOString();

    console.log(`[UserStore] Updated user: ${user.username}`);

    return user;
  }

  /**
   * Delete user
   */
  deleteUser(id: string): boolean {
    const user = this.users.get(id);

    if (!user) {
      return false;
    }

    // Remove from indexes
    this.usernameIndex.delete(user.username.toLowerCase());
    this.emailIndex.delete(user.email.toLowerCase());

    // Remove user
    this.users.delete(id);

    console.log(`[UserStore] Deleted user: ${user.username}`);

    return true;
  }

  /**
   * List all users
   */
  listUsers(options?: { includeInactive?: boolean }): User[] {
    const users = Array.from(this.users.values());

    if (options?.includeInactive === false) {
      return users.filter((u) => u.isActive);
    }

    return users;
  }

  /**
   * Get user count
   */
  getUserCount(): number {
    return this.users.size;
  }

  /**
   * Validate email format
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}

// ══════════════════════════════════════════════════════════════
// 🌐 GLOBAL USER STORE INSTANCE
// ══════════════════════════════════════════════════════════════

export const userStore = new UserStore();

// ══════════════════════════════════════════════════════════════
// 🔐 USER SERVICE FUNCTIONS
// ══════════════════════════════════════════════════════════════

/**
 * Register a new user
 */
export async function registerUser(data: CreateUserData): Promise<{
  user: Omit<User, "passwordHash">;
  tokens: { accessToken: string; refreshToken: string };
}> {
  try {
    const user = await userStore.createUser(data);

    // Generate authentication tokens
    const userPayload: UserPayload = {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
    };

    const tokens = generateTokens(userPayload);

    // Return user without password hash
    const { passwordHash, ...userWithoutPassword } = user;

    return {
      user: userWithoutPassword,
      tokens,
    };
  } catch (error: any) {
    console.error("[UserService] Registration error:", error);
    throw error;
  }
}

/**
 * Login user with credentials
 */
export async function loginUser(credentials: LoginCredentials): Promise<{
  user: Omit<User, "passwordHash">;
  tokens: { accessToken: string; refreshToken: string };
} | null> {
  try {
    const user = await userStore.authenticate(credentials);

    if (!user) {
      return null;
    }

    // Generate authentication tokens
    const userPayload: UserPayload = {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
    };

    const tokens = generateTokens(userPayload);

    // Return user without password hash
    const { passwordHash, ...userWithoutPassword } = user;

    return {
      user: userWithoutPassword,
      tokens,
    };
  } catch (error: any) {
    console.error("[UserService] Login error:", error);
    throw error;
  }
}

/**
 * Get user profile by ID
 */
export function getUserProfile(id: string): Omit<User, "passwordHash"> | null {
  const user = userStore.findById(id);

  if (!user) {
    return null;
  }

  const { passwordHash, ...userWithoutPassword } = user;
  return userWithoutPassword;
}

/**
 * Update user profile
 */
export async function updateUserProfile(
  id: string,
  data: UpdateUserData,
): Promise<Omit<User, "passwordHash"> | null> {
  try {
    const user = await userStore.updateUser(id, data);

    if (!user) {
      return null;
    }

    const { passwordHash, ...userWithoutPassword } = user;
    return userWithoutPassword;
  } catch (error: any) {
    console.error("[UserService] Update error:", error);
    throw error;
  }
}

/**
 * Change user password
 */
export async function changePassword(
  id: string,
  oldPassword: string,
  newPassword: string,
): Promise<boolean> {
  try {
    const user = userStore.findById(id);

    if (!user) {
      return false;
    }

    // Verify old password
    const isOldPasswordValid = await verifyPassword(
      oldPassword,
      user.passwordHash,
    );

    if (!isOldPasswordValid) {
      throw new Error("Current password is incorrect");
    }

    // Update password
    await userStore.updateUser(id, { password: newPassword });

    return true;
  } catch (error: any) {
    console.error("[UserService] Password change error:", error);
    throw error;
  }
}

/**
 * List all users (admin only)
 */
export function listAllUsers(
  includeInactive: boolean = false,
): Omit<User, "passwordHash">[] {
  const users = userStore.listUsers({ includeInactive });

  return users.map(
    ({ passwordHash, ...userWithoutPassword }) => userWithoutPassword,
  );
}

/**
 * Get user statistics
 */
export function getUserStats(): {
  totalUsers: number;
  activeUsers: number;
  adminUsers: number;
  regularUsers: number;
  guestUsers: number;
} {
  const allUsers = userStore.listUsers({ includeInactive: true });
  const activeUsers = allUsers.filter((u) => u.isActive);

  return {
    totalUsers: allUsers.length,
    activeUsers: activeUsers.length,
    adminUsers: allUsers.filter((u) => u.role === "admin").length,
    regularUsers: allUsers.filter((u) => u.role === "user").length,
    guestUsers: allUsers.filter((u) => u.role === "guest").length,
  };
}

// ══════════════════════════════════════════════════════════════
// 📤 EXPORTS
// ══════════════════════════════════════════════════════════════

export default {
  userStore,
  registerUser,
  loginUser,
  getUserProfile,
  updateUserProfile,
  changePassword,
  listAllUsers,
  getUserStats,
};
