"""
Islamic AI SaaS Platform Dashboard API
Comprehensive dashboard for organizations to manage their Islamic AI usage and settings
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import (
    APIRouter, Depends, HTTPException, Query, 
    Path, BackgroundTasks, UploadFile, File
)
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

# Core services
from ...core.saas_platform import saas_platform, SubscriptionTier, APIPermission
from ...core.auth import get_current_user_optional
from ...core.rate_limiting import rate_limit
from ...db.database import get_db

# Monitoring
import structlog
from prometheus_client import Counter

# Dashboard Models
class DashboardOverview(BaseModel):
    """Dashboard overview data"""
    organization_name: str
    subscription_tier: str
    current_usage: Dict[str, Any]
    quota_limits: Dict[str, Any]
    recent_activity: List[Dict]
    billing_status: Dict[str, Any]
    api_performance: Dict[str, Any]
    
class UsageSummary(BaseModel):
    """Usage summary model"""
    period: str
    api_calls_total: int
    api_calls_limit: int
    video_generations_total: int
    video_generations_limit: int
    quota_percentage: float
    overage_charges: float
    estimated_monthly_cost: float
    top_endpoints: List[Dict]
    
class APIKeyManagement(BaseModel):
    """API key management model"""
    api_keys: List[Dict]
    total_keys: int
    active_keys: int
    last_used: Optional[datetime]
    
class BillingDashboard(BaseModel):
    """Billing dashboard model"""
    current_subscription: Dict[str, Any]
    payment_method: Optional[Dict]
    billing_history: List[Dict]
    upcoming_invoice: Optional[Dict]
    usage_based_charges: Dict[str, float]
    
class TeamMember(BaseModel):
    """Team member model"""
    user_id: str
    email: str
    full_name: str
    role: str
    permissions: List[str]
    last_active: Optional[datetime]
    created_at: datetime
    
class OrganizationSettings(BaseModel):
    """Organization settings model"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    billing_email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    preferences: Dict = Field(default_factory=dict)
    
class WhiteLabelSettings(BaseModel):
    """White-label customization settings"""
    enabled: bool = False
    brand_name: str = Field("Budul AI", max_length=100)
    logo_url: Optional[str] = None
    primary_color: str = Field("#0d4f3c")  # Islamic green
    secondary_color: str = Field("#c9b037")  # Gold
    custom_domain: Optional[str] = None
    custom_css: Optional[str] = None
    footer_text: Optional[str] = None
    contact_email: Optional[str] = None
    support_url: Optional[str] = None
    
class APIKeyRequest(BaseModel):
    """API key creation request"""
    key_name: str = Field(..., min_length=1, max_length=200)
    permissions: List[APIPermission] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)

# Router setup
router = APIRouter(prefix="/dashboard", tags=["SaaS Dashboard"])
logger = structlog.get_logger(__name__)

# Metrics
dashboard_requests_counter = Counter('islamic_ai_dashboard_requests_total', 'Dashboard requests', ['endpoint'])

@router.get("/overview", response_model=DashboardOverview)
@rate_limit(calls=100, period=60)
async def get_dashboard_overview(
    user_id: str = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> DashboardOverview:
    """
    Get comprehensive dashboard overview
    
    Returns organization overview, usage statistics, billing status, and performance metrics.
    """
    dashboard_requests_counter.labels(endpoint='overview').inc()
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get organization ID from user
        organization_id = await _get_user_organization(user_id)
        
        # Get organization details
        org_data = await saas_platform._get_organization(organization_id)
        
        # Get usage analytics
        analytics = await saas_platform.get_organization_analytics(organization_id, days=30)
        
        # Get recent activity
        recent_activity = await _get_recent_activity(organization_id, limit=10)
        
        # Get billing status
        billing_status = await _get_billing_status(organization_id)
        
        return DashboardOverview(
            organization_name=org_data.get("name", "Unknown Organization"),
            subscription_tier=org_data.get("subscription_tier", "free"),
            current_usage={
                "api_calls": analytics["total_api_calls"],
                "video_generations": analytics["total_video_generations"],
                "quota_used_percentage": analytics["current_month_quota_used"]
            },
            quota_limits=analytics["tier_limits"],
            recent_activity=recent_activity,
            billing_status=billing_status,
            api_performance={
                "average_response_time": analytics["average_response_time_ms"],
                "error_rate": analytics["error_rate_percentage"],
                "uptime": 99.9
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Error loading dashboard")

@router.get("/usage", response_model=UsageSummary)
@rate_limit(calls=100, period=60)
async def get_usage_summary(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    user_id: str = Depends(get_current_user_optional)
) -> UsageSummary:
    """
    Get detailed usage summary for specified period
    
    Provides comprehensive usage analytics, quota tracking, and cost estimates.
    """
    dashboard_requests_counter.labels(endpoint='usage').inc()
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Calculate period days
        period_days = {"day": 1, "week": 7, "month": 30, "year": 365}[period]
        
        # Get analytics for period
        analytics = await saas_platform.get_organization_analytics(organization_id, days=period_days)
        
        # Calculate overage charges
        overage_charges = await _calculate_overage_charges(organization_id, analytics)
        
        # Estimate monthly cost
        estimated_cost = await _estimate_monthly_cost(organization_id, analytics)
        
        return UsageSummary(
            period=period,
            api_calls_total=analytics["total_api_calls"],
            api_calls_limit=analytics["tier_limits"]["monthly_api_calls"],
            video_generations_total=analytics["total_video_generations"],
            video_generations_limit=analytics["tier_limits"]["video_generations_monthly"],
            quota_percentage=analytics["current_month_quota_used"],
            overage_charges=overage_charges,
            estimated_monthly_cost=estimated_cost,
            top_endpoints=analytics["usage_by_endpoint"]
        )
        
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        raise HTTPException(status_code=500, detail="Error loading usage data")

@router.get("/api-keys", response_model=APIKeyManagement)
@rate_limit(calls=50, period=60)
async def get_api_keys(
    user_id: str = Depends(get_current_user_optional)
) -> APIKeyManagement:
    """
    Get API key management information
    
    Lists all API keys for the organization with usage statistics.
    """
    dashboard_requests_counter.labels(endpoint='api_keys').inc()
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Get API keys for organization
        api_keys = await _get_organization_api_keys(organization_id)
        
        # Format API keys for display
        formatted_keys = []
        active_count = 0
        last_used = None
        
        for key in api_keys:
            if key["is_active"]:
                active_count += 1
            
            if key["last_used"] and (not last_used or key["last_used"] > last_used):
                last_used = key["last_used"]
            
            formatted_keys.append({
                "id": key["id"],
                "name": key["key_name"],
                "prefix": key["key_prefix"],
                "created_at": key["created_at"],
                "last_used": key["last_used"],
                "total_requests": key["total_requests"],
                "is_active": key["is_active"],
                "expires_at": key.get("expires_at")
            })
        
        return APIKeyManagement(
            api_keys=formatted_keys,
            total_keys=len(api_keys),
            active_keys=active_count,
            last_used=last_used
        )
        
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        raise HTTPException(status_code=500, detail="Error loading API keys")

@router.post("/api-keys")
@rate_limit(calls=10, period=60)
async def create_api_key(
    request: APIKeyRequest,
    user_id: str = Depends(get_current_user_optional)
):
    """
    Create new API key for organization
    
    Generates a new API key with specified permissions and expiration.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Generate API key
        api_key = await saas_platform.generate_api_key(organization_id, request.key_name)
        
        return {
            "message": "API key created successfully",
            "api_key": api_key,
            "key_name": request.key_name,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail="Error creating API key")

@router.delete("/api-keys/{key_id}")
@rate_limit(calls=20, period=60)
async def revoke_api_key(
    key_id: str = Path(...),
    user_id: str = Depends(get_current_user_optional)
):
    """
    Revoke API key
    
    Permanently disables the specified API key.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        await saas_platform.revoke_api_key(organization_id, key_id)
        
        return {"message": "API key revoked successfully"}
        
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail="Error revoking API key")

@router.get("/billing", response_model=BillingDashboard)
@rate_limit(calls=50, period=60)
async def get_billing_dashboard(
    user_id: str = Depends(get_current_user_optional)
) -> BillingDashboard:
    """
    Get billing dashboard information
    
    Provides subscription details, payment methods, billing history, and invoices.
    """
    dashboard_requests_counter.labels(endpoint='billing').inc()
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Get current subscription
        org_data = await saas_platform._get_organization(organization_id)
        current_subscription = {
            "tier": org_data.get("subscription_tier"),
            "billing_cycle": org_data.get("billing_cycle"),
            "started": org_data.get("subscription_started"),
            "expires": org_data.get("subscription_expires")
        }
        
        # Get billing history
        billing_history = await _get_billing_history(organization_id)
        
        # Get upcoming invoice
        upcoming_invoice = await _get_upcoming_invoice(organization_id)
        
        # Calculate usage-based charges
        usage_charges = await _calculate_usage_charges(organization_id)
        
        return BillingDashboard(
            current_subscription=current_subscription,
            payment_method=None,  # Would integrate with Stripe
            billing_history=billing_history,
            upcoming_invoice=upcoming_invoice,
            usage_based_charges=usage_charges
        )
        
    except Exception as e:
        logger.error(f"Error getting billing dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error loading billing data")

@router.post("/subscription/upgrade")
@rate_limit(calls=5, period=60)
async def upgrade_subscription(
    new_tier: SubscriptionTier,
    billing_cycle: str = Query("monthly", regex="^(monthly|yearly)$"),
    user_id: str = Depends(get_current_user_optional)
):
    """
    Upgrade subscription tier
    
    Upgrades organization to higher subscription tier with immediate effect.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        from ...core.saas_platform import BillingCycle
        cycle = BillingCycle.YEARLY if billing_cycle == "yearly" else BillingCycle.MONTHLY
        
        result = await saas_platform.upgrade_subscription(organization_id, new_tier, cycle)
        
        return {
            "message": "Subscription upgraded successfully",
            "new_tier": new_tier.value,
            "billing_cycle": billing_cycle,
            "effective_immediately": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        raise HTTPException(status_code=500, detail="Error upgrading subscription")

@router.get("/settings", response_model=OrganizationSettings)
@rate_limit(calls=100, period=60)
async def get_organization_settings(
    user_id: str = Depends(get_current_user_optional)
) -> OrganizationSettings:
    """
    Get organization settings
    
    Returns current organization configuration and preferences.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        org_data = await saas_platform._get_organization(organization_id)
        
        return OrganizationSettings(
            name=org_data.get("name", ""),
            description=org_data.get("description"),
            website=org_data.get("website"),
            industry=org_data.get("industry"),
            country=org_data.get("country"),
            billing_email=org_data.get("billing_email", ""),
            preferences=org_data.get("settings", {})
        )
        
    except Exception as e:
        logger.error(f"Error getting organization settings: {e}")
        raise HTTPException(status_code=500, detail="Error loading settings")

@router.put("/settings")
@rate_limit(calls=20, period=60)
async def update_organization_settings(
    settings: OrganizationSettings,
    user_id: str = Depends(get_current_user_optional)
):
    """
    Update organization settings
    
    Updates organization configuration and preferences.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Update organization settings
        # This would use actual database operations
        logger.info(f"Updated settings for organization {organization_id}: {settings}")
        
        return {"message": "Organization settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating organization settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating settings")

@router.get("/white-label", response_model=WhiteLabelSettings)
@rate_limit(calls=50, period=60)
async def get_white_label_settings(
    user_id: str = Depends(get_current_user_optional)
) -> WhiteLabelSettings:
    """
    Get white-label customization settings
    
    Returns current white-label branding configuration.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Check if organization has white-label permissions
        org_data = await saas_platform._get_organization(organization_id)
        tier_info = await saas_platform._get_organization_tier(organization_id)
        
        from ...core.saas_platform import SUBSCRIPTION_TIERS
        tier_limits = SUBSCRIPTION_TIERS[tier_info["tier"]]
        
        if not tier_limits.white_label:
            raise HTTPException(
                status_code=403, 
                detail="White-label customization not available in current tier"
            )
        
        # Get white-label settings
        settings = org_data.get("settings", {}).get("white_label", {})
        
        return WhiteLabelSettings(**settings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting white-label settings: {e}")
        raise HTTPException(status_code=500, detail="Error loading white-label settings")

@router.put("/white-label")
@rate_limit(calls=10, period=60)
async def update_white_label_settings(
    settings: WhiteLabelSettings,
    user_id: str = Depends(get_current_user_optional)
):
    """
    Update white-label customization settings
    
    Updates branding and customization for white-label deployment.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Verify white-label permissions
        tier_info = await saas_platform._get_organization_tier(organization_id)
        from ...core.saas_platform import SUBSCRIPTION_TIERS
        tier_limits = SUBSCRIPTION_TIERS[tier_info["tier"]]
        
        if not tier_limits.white_label:
            raise HTTPException(
                status_code=403,
                detail="White-label customization requires Professional or Enterprise tier"
            )
        
        # Update white-label settings
        logger.info(f"Updated white-label settings for organization {organization_id}")
        
        return {"message": "White-label settings updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating white-label settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating white-label settings")

@router.post("/white-label/logo")
@rate_limit(calls=5, period=60)
async def upload_white_label_logo(
    logo: UploadFile = File(...),
    user_id: str = Depends(get_current_user_optional)
):
    """
    Upload custom logo for white-label branding
    
    Uploads and processes custom logo for white-label deployment.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Validate file type
        if not logo.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 2MB)
        content = await logo.read()
        if len(content) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 2MB")
        
        organization_id = await _get_user_organization(user_id)
        
        # Save logo and return URL
        logo_url = await _save_white_label_logo(organization_id, content, logo.content_type)
        
        return {
            "message": "Logo uploaded successfully",
            "logo_url": logo_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        raise HTTPException(status_code=500, detail="Error uploading logo")

@router.get("/analytics/export")
@rate_limit(calls=10, period=60)
async def export_analytics(
    format: str = Query("csv", regex="^(csv|json|pdf)$"),
    period_days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user_optional)
):
    """
    Export analytics data
    
    Exports comprehensive analytics data in specified format.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        organization_id = await _get_user_organization(user_id)
        
        # Get comprehensive analytics
        analytics = await saas_platform.get_organization_analytics(organization_id, days=period_days)
        
        # Generate export file
        export_file = await _generate_analytics_export(analytics, format, period_days)
        
        return {
            "message": "Analytics export generated",
            "download_url": export_file["url"],
            "format": format,
            "period_days": period_days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail="Error exporting analytics")

# Utility functions
async def _get_user_organization(user_id: str) -> str:
    """Get organization ID for user"""
    # This would query user's organization from database
    return "default_org_id"  # Placeholder

async def _get_recent_activity(organization_id: str, limit: int = 10) -> List[Dict]:
    """Get recent organization activity"""
    return []  # Placeholder

async def _get_billing_status(organization_id: str) -> Dict:
    """Get billing status"""
    return {
        "status": "active",
        "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "amount_due": 0.0
    }

async def _calculate_overage_charges(organization_id: str, analytics: Dict) -> float:
    """Calculate overage charges"""
    return 0.0  # Placeholder

async def _estimate_monthly_cost(organization_id: str, analytics: Dict) -> float:
    """Estimate monthly cost"""
    return 49.0  # Placeholder

async def _get_organization_api_keys(organization_id: str) -> List[Dict]:
    """Get API keys for organization"""
    return []  # Placeholder

async def _get_billing_history(organization_id: str) -> List[Dict]:
    """Get billing history"""
    return []  # Placeholder

async def _get_upcoming_invoice(organization_id: str) -> Optional[Dict]:
    """Get upcoming invoice"""
    return None  # Placeholder

async def _calculate_usage_charges(organization_id: str) -> Dict[str, float]:
    """Calculate usage-based charges"""
    return {"overage": 0.0, "estimated_month": 49.0}

async def _save_white_label_logo(organization_id: str, content: bytes, content_type: str) -> str:
    """Save white-label logo"""
    return f"/static/logos/{organization_id}_logo.png"  # Placeholder

async def _generate_analytics_export(analytics: Dict, format: str, period_days: int) -> Dict:
    """Generate analytics export file"""
    return {"url": f"/exports/analytics_{period_days}d.{format}"}  # Placeholder