"""
Global Waqaf Tech - FastAPI Dependencies
Authentication, authorization, and dependency injection helpers
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import decode_access_token
from app.core.permissions import (
    require_role,
    check_organization_access,
    check_subscription_active,
    Role
)
from app.db.database import get_db
from app.db.models_multitenant import User, Organization


# HTTP Bearer token security scheme
security = HTTPBearer()


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract and validate JWT token, return user data

    Returns:
        dict: Token payload with user_id, org_id, role, email
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return payload

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(
    token_data: dict = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from database

    Returns:
        User: Current user object

    Raises:
        HTTPException: 401 if user not found or inactive
    """
    user_id = token_data.get("sub")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are active

    Returns:
        User: Current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# ORGANIZATION DEPENDENCIES
# ============================================================================

async def get_current_organization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get the current user's organization

    Returns:
        Organization: Current user's organization

    Raises:
        HTTPException: 403 if user is super_admin (no org) or org not found
    """
    if current_user.role == Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admins don't belong to an organization. Please specify an organization ID."
        )

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization"
        )

    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization is inactive. Please contact support."
        )

    # Check subscription status
    check_subscription_active(
        organization.subscription_status,
        organization.subscription_expires
    )

    return organization


async def get_optional_organization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Optional[Organization]:
    """
    Get current organization (optional - returns None for super_admin)

    Returns:
        Optional[Organization]: Current organization or None
    """
    if current_user.role == Role.SUPER_ADMIN:
        return None

    if not current_user.organization_id:
        return None

    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    return organization


async def get_organization_by_id(
    organization_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get an organization by ID (with access control)

    Args:
        organization_id: UUID of the organization

    Returns:
        Organization: The requested organization

    Raises:
        HTTPException: 403 if user doesn't have access, 404 if not found
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Check access permissions
    check_organization_access(
        current_user.organization_id,
        organization_id,
        current_user.role
    )

    return organization


# ============================================================================
# ROLE-BASED DEPENDENCIES
# ============================================================================

def require_roles(allowed_roles: List[str]):
    """
    Create a dependency that requires specific roles

    Args:
        allowed_roles: List of allowed role names

    Returns:
        Dependency function

    Example:
        @router.get("/admin-only")
        async def admin_endpoint(
            user: User = Depends(require_roles([Role.SUPER_ADMIN, Role.ORG_ADMIN]))
        ):
            ...
    """
    async def check_user_role(current_user: User = Depends(get_current_active_user)) -> User:
        require_role(current_user.role, allowed_roles)
        return current_user

    return check_user_role


async def get_super_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to be super admin

    Returns:
        User: Current user (super admin)

    Raises:
        HTTPException: 403 if user is not super admin
    """
    require_role(current_user.role, [Role.SUPER_ADMIN])
    return current_user


async def get_org_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to be organization admin

    Returns:
        User: Current user (org admin)

    Raises:
        HTTPException: 403 if user is not org admin
    """
    require_role(current_user.role, [Role.ORG_ADMIN])
    return current_user


async def get_org_admin_or_super(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to be either org admin or super admin

    Returns:
        User: Current user

    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    require_role(current_user.role, [Role.SUPER_ADMIN, Role.ORG_ADMIN])
    return current_user


# ============================================================================
# UTILITY DEPENDENCIES
# ============================================================================

async def get_pagination_params(
    skip: int = 0,
    limit: int = 20,
    max_limit: int = 100
) -> dict:
    """
    Get pagination parameters with validation

    Args:
        skip: Number of records to skip (offset)
        limit: Number of records to return
        max_limit: Maximum allowed limit

    Returns:
        dict: Validated pagination params
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter cannot be negative"
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be at least 1"
        )

    if limit > max_limit:
        limit = max_limit

    return {"skip": skip, "limit": limit}


# ============================================================================
# FEATURE ACCESS DEPENDENCIES
# ============================================================================

def require_feature(feature_name: str, capability: Optional[str] = None):
    """
    Create a dependency that checks feature access for current organization

    Args:
        feature_name: Name of the feature (e.g., "dua_studio")
        capability: Optional specific capability within feature

    Returns:
        Dependency function

    Example:
        @router.post("/duas/generate")
        async def generate_dua(
            org: Organization = Depends(require_feature("dua_studio"))
        ):
            ...
    """
    async def check_feature_access_dep(
        organization: Organization = Depends(get_current_organization)
    ) -> Organization:
        from app.core.permissions import check_feature_access

        check_feature_access(
            organization.plan,
            feature_name,
            capability
        )

        return organization

    return check_feature_access_dep


# ============================================================================
# CONTEXT DEPENDENCIES (For logging, tracking, etc.)
# ============================================================================

async def get_request_context(
    current_user: User = Depends(get_current_active_user),
    organization: Optional[Organization] = Depends(get_optional_organization)
) -> dict:
    """
    Get request context for logging and tracking

    Returns:
        dict: Context with user and organization info
    """
    return {
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_role": current_user.role,
        "organization_id": str(organization.id) if organization else None,
        "organization_name": organization.name if organization else None,
        "organization_plan": organization.plan if organization else None,
    }
