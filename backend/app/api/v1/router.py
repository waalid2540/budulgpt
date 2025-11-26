"""
Main API router for Global Waqaf Tech v2
Multi-tenant platform with authentication and role-based access
"""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    organizations,
    users,
    duas_multitenant,
    stories_multitenant,
    grants,
    marketplace,
    learning_hub,
    social_studio,
    umrah_hajj,
    islamic_content,
    chat,
    islamic_chat,
    simple_chat
)

api_router = APIRouter()

# ============================================================================
# CORE PLATFORM ROUTES (Multi-tenant)
# ============================================================================

# Authentication & Authorization
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Organization Management
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

# User Management
api_router.include_router(users.router, prefix="/users", tags=["users"])


# ============================================================================
# FEATURE MODULES (Multi-tenant)
# ============================================================================

# Du'a & Dhikr Studio
api_router.include_router(duas_multitenant.router, prefix="/duas", tags=["dua-studio"])

# Kids Story Studio
api_router.include_router(stories_multitenant.router, prefix="/stories", tags=["story-studio"])

# Grant Finder
api_router.include_router(grants.router, prefix="/grants", tags=["grant-finder"])

# Marketplace
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])

# Learning Hub
api_router.include_router(learning_hub.router, prefix="/learning", tags=["learning-hub"])

# Social Media Studio
api_router.include_router(social_studio.router, prefix="/social", tags=["social-studio"])

# Umrah & Hajj Alerts
api_router.include_router(umrah_hajj.router, prefix="/umrah", tags=["umrah-hajj"])


# ============================================================================
# LEGACY ROUTES (To be refactored for multi-tenancy)
# ============================================================================

# Islamic Content (Keep for backward compatibility)
api_router.include_router(islamic_content.router, prefix="/content", tags=["islamic-content"])

# Chat endpoints (To be refactored)
api_router.include_router(chat.router, prefix="/chat", tags=["budul-gpt"])
api_router.include_router(islamic_chat.router, prefix="/islamic-chat", tags=["islamic-ai"])
api_router.include_router(simple_chat.router, prefix="/budul-ai", tags=["budul-ai-trained"])