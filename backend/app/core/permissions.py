"""
Global Waqaf Tech - Role-Based Access Control (RBAC) & Permissions
Authorization helpers and plan-based feature access
"""

from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from datetime import datetime


# ============================================================================
# ROLE DEFINITIONS
# ============================================================================

class Role:
    """User role constants"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    ORG_USER = "org_user"

    @classmethod
    def all_roles(cls) -> List[str]:
        return [cls.SUPER_ADMIN, cls.ORG_ADMIN, cls.ORG_USER]

    @classmethod
    def org_roles(cls) -> List[str]:
        """Roles that belong to an organization"""
        return [cls.ORG_ADMIN, cls.ORG_USER]


# ============================================================================
# PLAN DEFINITIONS & FEATURE ACCESS
# ============================================================================

class Plan:
    """Subscription plan constants"""
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    @classmethod
    def all_plans(cls) -> List[str]:
        return [cls.BASIC, cls.PRO, cls.ENTERPRISE]


# Feature access configuration by plan
PLAN_FEATURES = {
    Plan.BASIC: {
        "dua_studio": {
            "enabled": True,
            "limit": 10,  # Per month
            "ai_generation": True,
        },
        "story_studio": {
            "enabled": True,
            "limit": 5,
            "ai_generation": True,
        },
        "umrah_finder": {
            "enabled": True,
            "limit": 5,  # 5 searches per month
            "save_searches": False,  # Cannot save searches
        },
        "grant_finder": {
            "enabled": True,
            "limit": -1,  # Can view unlimited
            "ai_summary": False,  # No AI features
            "ai_draft": False,
            "save_limit": 5,  # Can only save 5 grants
        },
        "marketplace": {
            "enabled": True,
            "view": True,
            "create_listing": False,  # Cannot create listings
        },
        "learning_hub": {
            "enabled": True,
            "free_courses_only": True,
        },
        "social_studio": {
            "enabled": False,  # Not available on Basic
        },
    },
    Plan.PRO: {
        "dua_studio": {
            "enabled": True,
            "limit": 100,
            "ai_generation": True,
        },
        "story_studio": {
            "enabled": True,
            "limit": 50,
            "ai_generation": True,
        },
        "umrah_finder": {
            "enabled": True,
            "limit": 50,  # 50 searches per month
            "save_searches": True,  # Can save searches with alerts
        },
        "grant_finder": {
            "enabled": True,
            "limit": -1,
            "ai_summary": True,
            "ai_draft": True,
            "save_limit": -1,  # Unlimited
        },
        "marketplace": {
            "enabled": True,
            "view": True,
            "create_listing": True,
            "listing_limit": 1,  # Can create 1 listing
        },
        "learning_hub": {
            "enabled": True,
            "free_courses_only": False,  # Access to all courses
        },
        "social_studio": {
            "enabled": True,
            "limit": 50,  # 50 posts per month
        },
    },
    Plan.ENTERPRISE: {
        "dua_studio": {
            "enabled": True,
            "limit": -1,  # Unlimited
            "ai_generation": True,
        },
        "story_studio": {
            "enabled": True,
            "limit": -1,
            "ai_generation": True,
        },
        "umrah_finder": {
            "enabled": True,
            "limit": -1,  # Unlimited searches
            "save_searches": True,  # Can save unlimited searches with alerts
        },
        "grant_finder": {
            "enabled": True,
            "limit": -1,
            "ai_summary": True,
            "ai_draft": True,
            "save_limit": -1,
            "priority_support": True,
        },
        "marketplace": {
            "enabled": True,
            "view": True,
            "create_listing": True,
            "listing_limit": -1,  # Unlimited listings
            "featured_listing": True,  # Can have featured listings
        },
        "learning_hub": {
            "enabled": True,
            "free_courses_only": False,
            "create_courses": True,  # Can create their own courses
        },
        "social_studio": {
            "enabled": True,
            "limit": -1,  # Unlimited
            "advanced_templates": True,
        },
    },
}


# ============================================================================
# PERMISSION CHECKING FUNCTIONS
# ============================================================================

def check_role(user_role: str, allowed_roles: List[str]) -> bool:
    """
    Check if user role is in allowed roles

    Args:
        user_role: The user's role
        allowed_roles: List of allowed roles

    Returns:
        bool: True if user has required role
    """
    return user_role in allowed_roles


def require_role(user_role: str, allowed_roles: List[str]) -> None:
    """
    Require user to have one of the allowed roles (raises exception if not)

    Args:
        user_role: The user's role
        allowed_roles: List of allowed roles

    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    if not check_role(user_role, allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of these roles: {', '.join(allowed_roles)}"
        )


def is_super_admin(user_role: str) -> bool:
    """Check if user is super admin"""
    return user_role == Role.SUPER_ADMIN


def is_org_admin(user_role: str) -> bool:
    """Check if user is organization admin"""
    return user_role == Role.ORG_ADMIN


def can_manage_organization(user_role: str) -> bool:
    """Check if user can manage organization settings"""
    return user_role in [Role.SUPER_ADMIN, Role.ORG_ADMIN]


def can_manage_users(user_role: str) -> bool:
    """Check if user can manage other users"""
    return user_role in [Role.SUPER_ADMIN, Role.ORG_ADMIN]


# ============================================================================
# PLAN-BASED FEATURE ACCESS
# ============================================================================

def get_plan_features(plan: str) -> Dict[str, Any]:
    """
    Get all features for a given plan

    Args:
        plan: Plan name (basic, pro, enterprise)

    Returns:
        dict: Feature configuration for the plan
    """
    return PLAN_FEATURES.get(plan, PLAN_FEATURES[Plan.BASIC])


def can_use_feature(plan: str, feature_name: str) -> bool:
    """
    Check if a plan allows access to a feature

    Args:
        plan: Organization's plan (basic, pro, enterprise)
        feature_name: Name of the feature to check

    Returns:
        bool: True if feature is enabled for this plan
    """
    plan_config = get_plan_features(plan)
    feature_config = plan_config.get(feature_name, {"enabled": False})
    return feature_config.get("enabled", False)


def get_feature_limit(plan: str, feature_name: str, limit_key: str = "limit") -> int:
    """
    Get the usage limit for a feature in a plan

    Args:
        plan: Organization's plan
        feature_name: Name of the feature
        limit_key: The key for the limit (default: "limit")

    Returns:
        int: Limit value (-1 means unlimited, 0 means disabled)
    """
    plan_config = get_plan_features(plan)
    feature_config = plan_config.get(feature_name, {})
    return feature_config.get(limit_key, 0)


def check_feature_access(
    plan: str,
    feature_name: str,
    required_capability: Optional[str] = None
) -> None:
    """
    Check if organization can access a feature (raises exception if not)

    Args:
        plan: Organization's plan
        feature_name: Feature to check
        required_capability: Optional specific capability within the feature

    Raises:
        HTTPException: 403 if feature is not accessible
    """
    if not can_use_feature(plan, feature_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The {feature_name} feature is not available on your current plan. Please upgrade to access this feature."
        )

    # Check specific capability if provided
    if required_capability:
        plan_config = get_plan_features(plan)
        feature_config = plan_config.get(feature_name, {})

        if not feature_config.get(required_capability, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The {required_capability} capability is not available on your current plan. Please upgrade."
            )


def check_usage_limit(
    plan: str,
    feature_name: str,
    current_usage: int,
    limit_key: str = "limit"
) -> None:
    """
    Check if organization has reached their usage limit for a feature

    Args:
        plan: Organization's plan
        feature_name: Feature to check
        current_usage: Current usage count
        limit_key: The key for the limit to check

    Raises:
        HTTPException: 429 if usage limit exceeded
    """
    limit = get_feature_limit(plan, feature_name, limit_key)

    # -1 means unlimited
    if limit == -1:
        return

    # Check if over limit
    if current_usage >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have reached your monthly limit for {feature_name}. Please upgrade your plan or wait until next month."
        )


def check_subscription_active(subscription_status: str, subscription_expires: Optional[datetime] = None) -> None:
    """
    Check if organization's subscription is active

    Args:
        subscription_status: Status of subscription (active, suspended, cancelled, trial)
        subscription_expires: Optional expiration date

    Raises:
        HTTPException: 403 if subscription is not active
    """
    if subscription_status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your subscription has been suspended. Please contact support or update your payment method."
        )

    if subscription_status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your subscription has been cancelled. Please reactivate your subscription to continue."
        )

    # Check expiration for trial accounts
    if subscription_status == "trial" and subscription_expires:
        if datetime.utcnow() > subscription_expires:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your trial period has expired. Please subscribe to continue using Global Waqaf Tech."
            )


# ============================================================================
# ORGANIZATION ACCESS CONTROL
# ============================================================================

def check_organization_access(user_org_id: Optional[str], target_org_id: str, user_role: str) -> None:
    """
    Check if user can access data from target organization

    Args:
        user_org_id: User's organization ID (None for super admin)
        target_org_id: Organization ID being accessed
        user_role: User's role

    Raises:
        HTTPException: 403 if user cannot access target organization
    """
    # Super admins can access any organization
    if is_super_admin(user_role):
        return

    # Other users can only access their own organization
    if str(user_org_id) != str(target_org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this organization's data"
        )


# ============================================================================
# PLAN COMPARISON HELPERS
# ============================================================================

def get_plan_hierarchy() -> Dict[str, int]:
    """Get plan hierarchy for comparisons (higher number = better plan)"""
    return {
        Plan.BASIC: 1,
        Plan.PRO: 2,
        Plan.ENTERPRISE: 3,
    }


def is_plan_upgrade(current_plan: str, target_plan: str) -> bool:
    """Check if target plan is an upgrade from current plan"""
    hierarchy = get_plan_hierarchy()
    return hierarchy.get(target_plan, 0) > hierarchy.get(current_plan, 0)


def get_upgrade_plans(current_plan: str) -> List[str]:
    """Get list of plans that are upgrades from current plan"""
    hierarchy = get_plan_hierarchy()
    current_level = hierarchy.get(current_plan, 0)

    return [
        plan for plan, level in hierarchy.items()
        if level > current_level
    ]
