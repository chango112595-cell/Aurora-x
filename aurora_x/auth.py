"""
Aurora-X Python Authentication Module
JWT token verification for Python services (Bridge, Self-Learn, Chat)
"""

import os
from functools import wraps
from typing import Any

import jwt
from flask import jsonify, request

# ══════════════════════════════════════════════════════════════
# 🔐 CONFIGURATION
# ══════════════════════════════════════════════════════════════

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-production-to-a-strong-secret")
JWT_ALGORITHM = "HS256"

# Warn if using default secret
if JWT_SECRET == "change-this-in-production-to-a-strong-secret":
    print("[Auth] ⚠️  WARNING: Using default JWT secret. Set JWT_SECRET environment variable in production!")

# ══════════════════════════════════════════════════════════════
# 📦 TYPES
# ══════════════════════════════════════════════════════════════


class UserPayload:
    """User information from JWT token"""

    def __init__(self, data: dict[str, Any]):
        self.id = data.get("id")
        self.username = data.get("username")
        self.email = data.get("email")
        self.role = data.get("role", "guest")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "username": self.username, "email": self.email, "role": self.role}

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"

    def is_user(self) -> bool:
        """Check if user has user or admin role"""
        return self.role in ["admin", "user"]


# ══════════════════════════════════════════════════════════════
# ✅ JWT TOKEN VERIFICATION
# ══════════════════════════════════════════════════════════════


def verify_token(token: str) -> UserPayload | None:
    """
    Verify and decode a JWT token

    Args:
        token: The JWT token to verify

    Returns:
        UserPayload if valid, None otherwise
    """
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Check token type (should be access token)
        if decoded.get("type") != "access":
            print(f"[Auth] Invalid token type: {decoded.get('type')}")
            return None

        return UserPayload(decoded)

    except jwt.ExpiredSignatureError:
        print("[Auth] Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[Auth] Invalid token: {e}")
        return None
    except Exception as e:
        print(f"[Auth] Token verification error: {e}")
        return None


def extract_token(headers: dict[str, str]) -> str | None:
    """
    Extract token from Authorization header (Bearer token)

    Args:
        headers: Request headers dictionary

    Returns:
        The extracted token or None if not found
    """
    auth_header = headers.get("Authorization", headers.get("authorization"))

    if not auth_header:
        return None

    # Support both "Bearer TOKEN" and just "TOKEN"
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return auth_header


# ══════════════════════════════════════════════════════════════
# 🛡️ FLASK AUTHENTICATION DECORATORS
# ══════════════════════════════════════════════════════════════


def require_auth(f):
    """
    Flask decorator to require authentication for protected routes
    Validates JWT token and passes user to route function

    Usage:
        @app.route("/protected")
        @require_auth
        def protected_route(user):
            return {"message": f"Hello {user.username}!"}
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from header
        token = extract_token(dict(request.headers))

        if not token:
            return jsonify({"error": "Unauthorized", "message": "Authentication token is required"}), 401

        # Verify token
        user = verify_token(token)

        if not user:
            return jsonify({"error": "Unauthorized", "message": "Invalid or expired authentication token"}), 401

        # Pass user to route function
        return f(user, *args, **kwargs)

    return decorated_function


def optional_auth(f):
    """
    Flask decorator for optional authentication
    Passes user if valid token provided, otherwise passes None

    Usage:
        @app.route("/optional")
        @optional_auth
        def optional_route(user):
            if user:
                return {"message": f"Hello {user.username}!"}
            return {"message": "Hello anonymous!"}
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from header
        token = extract_token(dict(request.headers))

        user = None
        if token:
            user = verify_token(token)

        # Pass user (or None) to route function
        return f(user, *args, **kwargs)

    return decorated_function


def require_role(*allowed_roles: str):
    """
    Flask decorator to require specific role for access
    Must be used AFTER require_auth decorator

    Usage:
        @app.route("/admin")
        @require_auth
        @require_role("admin")
        def admin_route(user):
            return {"message": "Admin access granted"}
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(user: UserPayload, *args, **kwargs):
            if not user:
                return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

            if user.role not in allowed_roles:
                return (
                    jsonify(
                        {"error": "Forbidden", "message": f"Access denied. Required role: {' or '.join(allowed_roles)}"}
                    ),
                    403,
                )

            return f(user, *args, **kwargs)

        return decorated_function

    return decorator


def require_admin(f):
    """
    Flask decorator to require admin role
    Convenience function for require_role("admin")

    Usage:
        @app.route("/admin")
        @require_auth
        @require_admin
        def admin_route(user):
            return {"message": "Admin access granted"}
    """
    return require_role("admin")(f)


def require_user(f):
    """
    Flask decorator to require user or admin role (excludes guests)
    Convenience function for require_role("admin", "user")

    Usage:
        @app.route("/users-only")
        @require_auth
        @require_user
        def users_route(user):
            return {"message": "User or admin access"}
    """
    return require_role("admin", "user")(f)


# ══════════════════════════════════════════════════════════════
# 🔄 FASTAPI DEPENDENCIES
# ══════════════════════════════════════════════════════════════

try:
    from typing import Annotated

    from fastapi import Header, HTTPException

    async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> UserPayload:
        """
        FastAPI dependency to get current authenticated user

        Usage:
            from fastapi import Depends

            @app.get("/protected")
            async def protected_route(user: UserPayload = Depends(get_current_user)):
                return {"message": f"Hello {user.username}!"}
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Authentication token is required")

        # Extract token
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization

        # Verify token
        user = verify_token(token)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        return user

    async def get_optional_user(authorization: Annotated[str | None, Header()] = None) -> UserPayload | None:
        """
        FastAPI dependency for optional authentication

        Usage:
            from fastapi import Depends

            @app.get("/optional")
            async def optional_route(user: Optional[UserPayload] = Depends(get_optional_user)):
                if user:
                    return {"message": f"Hello {user.username}!"}
                return {"message": "Hello anonymous!"}
        """
        if not authorization:
            return None

        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
        return verify_token(token)

    def require_role_fastapi(*allowed_roles: str):
        """
        FastAPI dependency to require specific role

        Usage:
            from fastapi import Depends

            @app.get("/admin")
            async def admin_route(user: UserPayload = Depends(require_role_fastapi("admin"))):
                return {"message": "Admin access granted"}
        """

        async def role_checker(user: UserPayload = Depends(get_current_user)) -> UserPayload:
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403, detail=f"Access denied. Required role: {' or '.join(allowed_roles)}"
                )
            return user

        return role_checker

    # Convenience functions
    require_admin_fastapi = require_role_fastapi("admin")
    require_user_fastapi = require_role_fastapi("admin", "user")

except ImportError:
    # FastAPI not installed, skip FastAPI dependencies
    pass

# ══════════════════════════════════════════════════════════════
# 📤 EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = [
    # Core functions
    "verify_token",
    "extract_token",
    "UserPayload",
    # Flask decorators
    "require_auth",
    "optional_auth",
    "require_role",
    "require_admin",
    "require_user",
    # FastAPI dependencies (if available)
    "get_current_user",
    "get_optional_user",
    "require_role_fastapi",
    "require_admin_fastapi",
    "require_user_fastapi",
]
