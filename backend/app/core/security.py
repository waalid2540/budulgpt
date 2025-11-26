"""
Global Waqaf Tech - Security & Authentication
JWT tokens, password hashing, and security utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
# TODO: Move these to environment variables
SECRET_KEY = "your-secret-key-here-change-in-production"  # CHANGE THIS!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary of data to encode in token (user_id, org_id, role, etc.)
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT access token

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


def generate_verification_token() -> str:
    """
    Generate a random token for email verification

    Returns:
        str: Random secure token
    """
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """
    Generate a random token for password reset

    Returns:
        str: Random secure token
    """
    return secrets.token_urlsafe(32)


def create_user_token_data(user_id: str, organization_id: Optional[str], role: str, email: str) -> Dict[str, Any]:
    """
    Create the data payload for a user's JWT token

    Args:
        user_id: User's UUID as string
        organization_id: Organization UUID as string (None for super_admin)
        role: User's role (super_admin, org_admin, org_user)
        email: User's email

    Returns:
        dict: Token data payload
    """
    return {
        "sub": user_id,  # Subject (user ID)
        "org_id": organization_id,
        "role": role,
        "email": email,
    }


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Args:
        password: Plain text password to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"

    return True, ""


def sanitize_email(email: str) -> str:
    """
    Sanitize and normalize email address

    Args:
        email: Email address to sanitize

    Returns:
        str: Sanitized email (lowercase, trimmed)
    """
    return email.lower().strip()
