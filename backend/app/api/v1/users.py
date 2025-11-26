"""
Global Waqaf Tech - User Management API
Invite users, manage roles, user CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models_multitenant import User, Organization
from app.core.deps import (
    get_current_user,
    get_current_organization,
    get_super_admin,
    get_org_admin_or_super,
    get_pagination_params,
)
from app.core.security import (
    get_password_hash,
    generate_verification_token,
    sanitize_email,
    validate_password_strength,
)
from app.core.permissions import Role, can_manage_users


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UserInvite(BaseModel):
    """Invite a new user to the organization"""
    email: EmailStr
    full_name: str
    role: str = Role.ORG_USER

    @validator('role')
    def validate_role(cls, v):
        if v not in [Role.ORG_ADMIN, Role.ORG_USER]:
            raise ValueError(f"Invalid role. Must be {Role.ORG_ADMIN} or {Role.ORG_USER}")
        return v


class UserCreate(BaseModel):
    """Create user (super admin only)"""
    email: EmailStr
    password: str
    full_name: str
    role: str
    organization_id: Optional[uuid.UUID] = None

    @validator('password')
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

    @validator('role')
    def validate_role(cls, v):
        if v not in Role.all_roles():
            raise ValueError(f"Invalid role. Must be one of: {', '.join(Role.all_roles())}")
        return v


class UserUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None


class UserRoleUpdate(BaseModel):
    """Update user role"""
    role: str

    @validator('role')
    def validate_role(cls, v):
        if v not in Role.all_roles():
            raise ValueError(f"Invalid role. Must be one of: {', '.join(Role.all_roles())}")
        return v


class UserResponse(BaseModel):
    """User details response"""
    id: str
    email: str
    full_name: str
    role: str
    organization_id: Optional[str]
    organization_name: Optional[str] = None
    avatar_url: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """List of users with pagination"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# USER INVITATION & CREATION
# ============================================================================

@router.post("/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    request: UserInvite,
    current_user: User = Depends(get_org_admin_or_super),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Invite a new user to the organization (org admin or super admin)

    - Creates user account with temporary password
    - Sends invitation email (to be implemented)
    - User must verify email and set password
    """
    # Check permission
    if not can_manage_users(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite users"
        )

    # Sanitize email
    email = sanitize_email(request.email)

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Generate temporary password (user will need to reset)
    temp_password = str(uuid.uuid4())[:16]

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=get_password_hash(temp_password),
        full_name=request.full_name,
        role=request.role,
        organization_id=organization.id,
        is_active=True,
        is_verified=False,
        verification_token=generate_verification_token(),
        created_at=datetime.utcnow(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # TODO: Send invitation email with verification link and temp password
    # send_invitation_email(user.email, user.full_name, user.verification_token, temp_password)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=str(organization.id),
        organization_name=organization.name,
        avatar_url=user.avatar_url,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user (super admin only)

    - Can create users for any organization
    - Can create super admins
    """
    # Sanitize email
    email = sanitize_email(request.email)

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Validate organization if not super admin
    if request.role != Role.SUPER_ADMIN:
        if not request.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="organization_id is required for non-super-admin users"
            )

        organization = db.query(Organization).filter(
            Organization.id == request.organization_id
        ).first()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=request.role,
        organization_id=request.organization_id,
        is_active=True,
        is_verified=True,  # Super admin created users are auto-verified
        created_at=datetime.utcnow(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Get organization name if exists
    org_name = None
    if user.organization_id:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        org_name = org.name if org else None

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
        organization_name=org_name,
        avatar_url=user.avatar_url,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login=user.last_login,
        created_at=user.created_at,
    )


# ============================================================================
# USER LISTING & RETRIEVAL
# ============================================================================

@router.get("/", response_model=UserListResponse)
async def list_users(
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    List users

    - Super admin: Can see all users
    - Org admin: Can see users in their organization
    - Org user: Cannot access this endpoint
    """
    # Check permissions
    if current_user.role == Role.ORG_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to list users"
        )

    # Build query
    query = db.query(User)

    # Filter by organization for non-super-admins
    if current_user.role != Role.SUPER_ADMIN:
        query = query.filter(User.organization_id == current_user.organization_id)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_term)) |
            (User.email.ilike(search_term))
        )

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    users = query.order_by(User.created_at.desc()).offset(
        pagination["skip"]
    ).limit(pagination["limit"]).all()

    # Get organization names
    org_ids = [u.organization_id for u in users if u.organization_id]
    organizations = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
    org_map = {str(org.id): org.name for org in organizations}

    # Build response
    user_responses = []
    for user in users:
        user_responses.append(UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            organization_id=str(user.organization_id) if user.organization_id else None,
            organization_name=org_map.get(str(user.organization_id)),
            avatar_url=user.avatar_url,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login,
            created_at=user.created_at,
        ))

    return UserListResponse(
        users=user_responses,
        total=total,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID

    - Super admin: Can view any user
    - Org admin: Can view users in their organization
    - Users: Can only view themselves
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if current_user.role == Role.SUPER_ADMIN:
        # Super admin can view anyone
        pass
    elif current_user.role == Role.ORG_ADMIN:
        # Org admin can view users in their org
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your organization"
            )
    else:
        # Regular users can only view themselves
        if user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile"
            )

    # Get organization name
    org_name = None
    if user.organization_id:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        org_name = org.name if org else None

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
        organization_name=org_name,
        avatar_url=user.avatar_url,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login=user.last_login,
        created_at=user.created_at,
    )


# ============================================================================
# USER UPDATE & MANAGEMENT
# ============================================================================

@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    # Update fields
    update_data = request.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    # Get organization name
    org_name = None
    if current_user.organization_id:
        org = db.query(Organization).filter(
            Organization.id == current_user.organization_id
        ).first()
        org_name = org.name if org else None

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        organization_name=org_name,
        avatar_url=current_user.avatar_url,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
    )


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: uuid.UUID,
    request: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's role

    - Super admin: Can change any user's role
    - Org admin: Can change roles within their organization (except super_admin)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if current_user.role == Role.SUPER_ADMIN:
        # Super admin can change anyone
        pass
    elif current_user.role == Role.ORG_ADMIN:
        # Org admin can only change users in their org
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users in your organization"
            )

        # Org admin cannot create super admins
        if request.role == Role.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot assign super_admin role"
            )

        # Org admin cannot change their own role
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own role"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change user roles"
        )

    old_role = user.role
    user.role = request.role
    user.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": f"User role updated from {old_role} to {request.role}",
        "user_id": str(user.id),
        "old_role": old_role,
        "new_role": request.role
    }


@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_org_admin_or_super),
    db: Session = Depends(get_db)
):
    """
    Activate a user (org admin or super admin)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions for org admin
    if current_user.role != Role.SUPER_ADMIN:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users in your organization"
            )

    user.is_active = True
    user.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": "User activated successfully"
    }


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_org_admin_or_super),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (org admin or super admin)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions for org admin
    if current_user.role != Role.SUPER_ADMIN:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users in your organization"
            )

    # Cannot deactivate yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    user.is_active = False
    user.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": "User deactivated successfully"
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_org_admin_or_super),
    db: Session = Depends(get_db)
):
    """
    Delete a user (org admin or super admin)

    WARNING: This will permanently delete the user and their data
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions for org admin
    if current_user.role != Role.SUPER_ADMIN:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users in your organization"
            )

    # Cannot delete yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )

    user_email = user.email

    db.delete(user)
    db.commit()

    return {
        "success": True,
        "message": f"User {user_email} deleted successfully"
    }
