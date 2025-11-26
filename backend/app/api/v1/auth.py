"""
Global Waqaf Tech - Authentication API Endpoints
User registration, login, password reset, email verification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.db.models_multitenant import User, Organization
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_verification_token,
    generate_reset_token,
    validate_password_strength,
    sanitize_email,
    create_user_token_data,
)
from app.core.permissions import Role
from app.core.deps import get_current_user


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str
    organization_name: Optional[str] = None
    organization_type: Optional[str] = "masjid"  # masjid, organization, school, business

    @validator('password')
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """User login response"""
    access_token: str
    token_type: str = "bearer"
    user: dict
    organization: Optional[dict] = None


class PasswordResetRequest(BaseModel):
    """Request password reset email"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""
    token: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class ChangePasswordRequest(BaseModel):
    """Change password for logged-in user"""
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    full_name: str
    role: str
    organization_id: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user and optionally create their organization

    - Creates a new user account
    - If organization_name provided, creates new organization and makes user org_admin
    - Returns access token for immediate login
    """
    # Sanitize email
    email = sanitize_email(request.email)

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Create organization if name provided
    organization = None
    user_role = Role.ORG_ADMIN  # Default role when creating org

    if request.organization_name:
        # Generate unique slug from organization name
        base_slug = request.organization_name.lower().replace(" ", "-").replace("_", "-")
        slug = base_slug
        counter = 1

        while db.query(Organization).filter(Organization.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create organization
        organization = Organization(
            id=uuid.uuid4(),
            name=request.organization_name,
            slug=slug,
            type=request.organization_type,
            plan="basic",  # Start with basic plan
            subscription_status="trial",  # Start with trial
            trial_ends_at=datetime.utcnow() + timedelta(days=14),  # 14-day trial
            is_active=True,
            is_verified=False,
        )
        db.add(organization)
        db.flush()  # Get organization ID

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=user_role,
        organization_id=organization.id if organization else None,
        is_active=True,
        is_verified=False,  # Require email verification
        verification_token=generate_verification_token(),
        created_at=datetime.utcnow(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    token_data = create_user_token_data(
        user_id=str(user.id),
        organization_id=str(organization.id) if organization else None,
        role=user.role,
        email=user.email
    )
    access_token = create_access_token(token_data)

    # Prepare response
    user_dict = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "organization_id": str(organization.id) if organization else None,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }

    organization_dict = None
    if organization:
        organization_dict = {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "type": organization.type,
            "plan": organization.plan,
            "subscription_status": organization.subscription_status,
        }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict,
        "organization": organization_dict
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token

    - Validates email and password
    - Returns JWT access token
    - Includes user and organization info
    """
    # Sanitize email
    email = sanitize_email(request.email)

    # Find user
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    # Update last login
    user.last_login = datetime.utcnow()
    user.login_count = (user.login_count or 0) + 1
    db.commit()

    # Get organization if exists
    organization = None
    if user.organization_id:
        organization = db.query(Organization).filter(
            Organization.id == user.organization_id
        ).first()

    # Create access token
    token_data = create_user_token_data(
        user_id=str(user.id),
        organization_id=str(organization.id) if organization else None,
        role=user.role,
        email=user.email
    )
    access_token = create_access_token(token_data)

    # Prepare response
    user_dict = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "organization_id": str(organization.id) if organization else None,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }

    organization_dict = None
    if organization:
        organization_dict = {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "type": organization.type,
            "plan": organization.plan,
            "subscription_status": organization.subscription_status,
        }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict,
        "organization": organization_dict
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.post("/request-password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email

    - Generates reset token
    - In production, would send email with reset link
    - For now, returns success (implement email sending later)
    """
    email = sanitize_email(request.email)

    user = db.query(User).filter(User.email == email).first()

    # Always return success to prevent email enumeration
    # But only generate token if user exists
    if user:
        user.reset_token = generate_reset_token()
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        # TODO: Send password reset email
        # send_password_reset_email(user.email, user.reset_token)

    return {
        "success": True,
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email
    """
    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired
    if user.reset_token_expires and datetime.utcnow() > user.reset_token_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )

    # Update password and clear reset token
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {
        "success": True,
        "message": "Password has been reset successfully. You can now log in with your new password."
    }


@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify user's email address using token
    """
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    if user.is_verified:
        return {
            "success": True,
            "message": "Email already verified"
        }

    # Verify email
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.verification_token = None
    db.commit()

    return {
        "success": True,
        "message": "Email verified successfully!"
    }


@router.post("/resend-verification")
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resend verification email to current user
    """
    if current_user.is_verified:
        return {
            "success": True,
            "message": "Email is already verified"
        }

    # Generate new verification token
    current_user.verification_token = generate_verification_token()
    db.commit()

    # TODO: Send verification email
    # send_verification_email(current_user.email, current_user.verification_token)

    return {
        "success": True,
        "message": "Verification email has been sent"
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (client should discard token)
    """
    # In a stateless JWT system, logout is handled client-side
    # Optionally, implement token blacklist here

    return {
        "success": True,
        "message": "Logged out successfully"
    }
