"""
Comprehensive Islamic AI SaaS Platform
Complete business platform with tiered API access, billing, and enterprise features
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import stripe
from decimal import Decimal

# FastAPI and database
from fastapi import HTTPException
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Authentication and security
import jwt
from passlib.context import CryptContext
import secrets
import hashlib

# Monitoring and analytics
import structlog
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

# Business logic
from .islamic_ai_config import settings

# Subscription tiers
class SubscriptionTier(str, Enum):
    FREE = "free"
    DEVELOPER = "developer"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class APIPermission(str, Enum):
    CHAT_BASIC = "chat_basic"
    CHAT_ADVANCED = "chat_advanced"
    VIDEO_GENERATION = "video_generation"
    BULK_PROCESSING = "bulk_processing"
    CUSTOM_MODELS = "custom_models"
    WHITE_LABEL = "white_label"
    ANALYTICS_ADVANCED = "analytics_advanced"
    PRIORITY_SUPPORT = "priority_support"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

@dataclass
class TierLimits:
    """Subscription tier limits and features"""
    name: str
    monthly_api_calls: int
    daily_api_calls: int
    video_generations_monthly: int
    max_concurrent_requests: int
    max_video_duration: int  # seconds
    custom_models: bool
    priority_support: bool
    white_label: bool
    advanced_analytics: bool
    bulk_processing: bool
    sla_uptime: float  # percentage
    rate_limit_per_minute: int
    permissions: List[APIPermission]
    monthly_price_usd: Decimal
    yearly_price_usd: Decimal

# Define subscription tiers
SUBSCRIPTION_TIERS = {
    SubscriptionTier.FREE: TierLimits(
        name="Free Tier",
        monthly_api_calls=1000,
        daily_api_calls=50,
        video_generations_monthly=5,
        max_concurrent_requests=2,
        max_video_duration=30,
        custom_models=False,
        priority_support=False,
        white_label=False,
        advanced_analytics=False,
        bulk_processing=False,
        sla_uptime=99.0,
        rate_limit_per_minute=10,
        permissions=[APIPermission.CHAT_BASIC],
        monthly_price_usd=Decimal("0.00"),
        yearly_price_usd=Decimal("0.00")
    ),
    SubscriptionTier.DEVELOPER: TierLimits(
        name="Developer",
        monthly_api_calls=25000,
        daily_api_calls=1000,
        video_generations_monthly=50,
        max_concurrent_requests=10,
        max_video_duration=120,
        custom_models=False,
        priority_support=True,
        white_label=False,
        advanced_analytics=True,
        bulk_processing=True,
        sla_uptime=99.5,
        rate_limit_per_minute=60,
        permissions=[
            APIPermission.CHAT_BASIC,
            APIPermission.CHAT_ADVANCED,
            APIPermission.VIDEO_GENERATION,
            APIPermission.BULK_PROCESSING
        ],
        monthly_price_usd=Decimal("49.00"),
        yearly_price_usd=Decimal("490.00")
    ),
    SubscriptionTier.PROFESSIONAL: TierLimits(
        name="Professional",
        monthly_api_calls=100000,
        daily_api_calls=5000,
        video_generations_monthly=200,
        max_concurrent_requests=25,
        max_video_duration=300,
        custom_models=True,
        priority_support=True,
        white_label=True,
        advanced_analytics=True,
        bulk_processing=True,
        sla_uptime=99.9,
        rate_limit_per_minute=120,
        permissions=[
            APIPermission.CHAT_BASIC,
            APIPermission.CHAT_ADVANCED,
            APIPermission.VIDEO_GENERATION,
            APIPermission.BULK_PROCESSING,
            APIPermission.CUSTOM_MODELS,
            APIPermission.WHITE_LABEL,
            APIPermission.ANALYTICS_ADVANCED
        ],
        monthly_price_usd=Decimal("199.00"),
        yearly_price_usd=Decimal("1990.00")
    ),
    SubscriptionTier.ENTERPRISE: TierLimits(
        name="Enterprise",
        monthly_api_calls=1000000,
        daily_api_calls=50000,
        video_generations_monthly=1000,
        max_concurrent_requests=100,
        max_video_duration=600,
        custom_models=True,
        priority_support=True,
        white_label=True,
        advanced_analytics=True,
        bulk_processing=True,
        sla_uptime=99.95,
        rate_limit_per_minute=300,
        permissions=[perm for perm in APIPermission],
        monthly_price_usd=Decimal("999.00"),
        yearly_price_usd=Decimal("9990.00")
    )
}

# Database Models
Base = declarative_base()

class Organization(Base):
    """Organization/Company using Islamic AI"""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    website = Column(String(200))
    industry = Column(String(100))
    country = Column(String(100))
    
    # Subscription details
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    billing_cycle = Column(SQLEnum(BillingCycle), default=BillingCycle.MONTHLY)
    subscription_started = Column(DateTime, default=func.now())
    subscription_expires = Column(DateTime)
    
    # Billing information
    stripe_customer_id = Column(String(100))
    stripe_subscription_id = Column(String(100))
    billing_email = Column(String(200))
    
    # Usage tracking
    current_month_api_calls = Column(Integer, default=0)
    current_month_video_generations = Column(Integer, default=0)
    total_api_calls = Column(Integer, default=0)
    total_video_generations = Column(Integer, default=0)
    
    # Settings
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    usage_logs = relationship("UsageLog", back_populates="organization")

class User(Base):
    """User within an organization"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Basic info
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default="user")  # admin, user, viewer
    
    # Preferences
    preferred_language = Column(String(10), default="en")
    preferred_madhab = Column(String(50), default="general")
    timezone = Column(String(50), default="UTC")
    
    # Status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")

class APIKey(Base):
    """API keys for accessing Islamic AI services"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Key details
    key_name = Column(String(200), nullable=False)
    key_hash = Column(String(200), nullable=False, unique=True)
    key_prefix = Column(String(20), nullable=False)  # First few chars for identification
    
    # Permissions and limits
    permissions = Column(JSON, default=list)  # List of APIPermission values
    rate_limit_override = Column(Integer)  # Custom rate limit if different from tier
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")

class UsageLog(Base):
    """Detailed usage logging for billing and analytics"""
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"))
    
    # Request details
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    
    # Processing details
    processing_time_ms = Column(Float)
    tokens_used = Column(Integer)
    model_used = Column(String(100))
    
    # Islamic AI specific
    authenticity_score = Column(Float)
    citations_provided = Column(Integer)
    language_detected = Column(String(10))
    
    # Billing
    cost_usd = Column(Float)
    billable = Column(Boolean, default=True)
    
    # Status
    status_code = Column(Integer)
    error_message = Column(String(1000))
    
    # Metadata
    timestamp = Column(DateTime, default=func.now())
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_logs")

class BillingInvoice(Base):
    """Billing invoices"""
    __tablename__ = "billing_invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    stripe_invoice_id = Column(String(100))
    
    # Billing period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Amounts
    subtotal_usd = Column(Float, nullable=False)
    tax_usd = Column(Float, default=0.0)
    total_usd = Column(Float, nullable=False)
    
    # Usage details
    api_calls_count = Column(Integer, default=0)
    video_generations_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="pending")  # pending, paid, failed, cancelled
    paid_at = Column(DateTime)
    due_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())

class IslamicAISaaSPlatform:
    """
    Comprehensive Islamic AI SaaS platform management
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.redis_client = None
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Initialize Stripe
        stripe.api_key = settings.stripe_secret_key
        
        # Setup metrics
        self.setup_metrics()
        
    def setup_metrics(self):
        """Setup business metrics"""
        self.api_requests_counter = Counter('islamic_ai_api_requests_total', 'Total API requests', ['tier', 'endpoint'])
        self.revenue_gauge = Gauge('islamic_ai_revenue_usd', 'Current revenue in USD')
        self.active_subscriptions_gauge = Gauge('islamic_ai_active_subscriptions', 'Active subscriptions', ['tier'])
        self.usage_quota_gauge = Gauge('islamic_ai_usage_quota_percentage', 'Usage quota percentage', ['organization'])
        
    async def initialize(self):
        """Initialize SaaS platform"""
        self.logger.info("Initializing Islamic AI SaaS Platform")
        
        # Setup Redis for caching and rate limiting
        self.redis_client = redis.from_url(settings.redis_url)
        
        # Initialize Stripe webhooks
        await self._setup_stripe_webhooks()
        
        self.logger.info("Islamic AI SaaS Platform initialized")
    
    # Authentication and Authorization
    async def authenticate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Authenticate API key and return organization info"""
        try:
            # Hash the provided key
            key_hash = self._hash_api_key(api_key)
            
            # Check cache first
            cached_auth = await self.redis_client.get(f"auth:{key_hash}")
            if cached_auth:
                auth_data = json.loads(cached_auth)
                
                # Update last used timestamp
                await self._update_api_key_usage(auth_data["api_key_id"])
                
                return auth_data
            
            # Query database
            # This would use actual database query in production
            auth_data = await self._query_api_key_auth(key_hash)
            
            if auth_data:
                # Cache for 5 minutes
                await self.redis_client.setex(
                    f"auth:{key_hash}",
                    300,
                    json.dumps(auth_data)
                )
                
                # Update usage
                await self._update_api_key_usage(auth_data["api_key_id"])
                
                return auth_data
            
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    async def check_rate_limit(self, organization_id: str, endpoint: str) -> bool:
        """Check if organization has exceeded rate limits"""
        try:
            # Get organization tier
            tier_info = await self._get_organization_tier(organization_id)
            tier_limits = SUBSCRIPTION_TIERS[tier_info["tier"]]
            
            # Check minute-based rate limit
            minute_key = f"rate_limit:{organization_id}:{endpoint}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            current_minute_requests = await self.redis_client.get(minute_key)
            current_minute_requests = int(current_minute_requests) if current_minute_requests else 0
            
            if current_minute_requests >= tier_limits.rate_limit_per_minute:
                return False
            
            # Check daily limit
            daily_key = f"daily_usage:{organization_id}:{datetime.utcnow().strftime('%Y%m%d')}"
            daily_requests = await self.redis_client.get(daily_key)
            daily_requests = int(daily_requests) if daily_requests else 0
            
            if daily_requests >= tier_limits.daily_api_calls:
                return False
            
            # Check monthly limit
            monthly_usage = await self._get_monthly_usage(organization_id)
            if monthly_usage >= tier_limits.monthly_api_calls:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check error: {e}")
            return False
    
    async def increment_usage(
        self, 
        organization_id: str, 
        endpoint: str, 
        usage_data: Dict[str, Any]
    ):
        """Increment usage counters"""
        try:
            # Increment minute counter
            minute_key = f"rate_limit:{organization_id}:{endpoint}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            await self.redis_client.incr(minute_key)
            await self.redis_client.expire(minute_key, 60)
            
            # Increment daily counter
            daily_key = f"daily_usage:{organization_id}:{datetime.utcnow().strftime('%Y%m%d')}"
            await self.redis_client.incr(daily_key)
            await self.redis_client.expire(daily_key, 86400)
            
            # Log detailed usage
            await self._log_usage(organization_id, endpoint, usage_data)
            
            # Update metrics
            tier_info = await self._get_organization_tier(organization_id)
            self.api_requests_counter.labels(
                tier=tier_info["tier"].value,
                endpoint=endpoint
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Usage increment error: {e}")
    
    # Subscription Management
    async def create_organization(self, org_data: Dict[str, Any]) -> str:
        """Create new organization with free tier"""
        try:
            # Create Stripe customer
            stripe_customer = stripe.Customer.create(
                email=org_data["billing_email"],
                name=org_data["name"],
                metadata={
                    "industry": org_data.get("industry"),
                    "country": org_data.get("country")
                }
            )
            
            # Create organization in database
            org_id = str(uuid.uuid4())
            
            # This would use actual database operations
            organization_data = {
                "id": org_id,
                "name": org_data["name"],
                "description": org_data.get("description"),
                "website": org_data.get("website"),
                "industry": org_data.get("industry"),
                "country": org_data.get("country"),
                "subscription_tier": SubscriptionTier.FREE,
                "billing_cycle": BillingCycle.MONTHLY,
                "stripe_customer_id": stripe_customer.id,
                "billing_email": org_data["billing_email"],
                "created_at": datetime.utcnow()
            }
            
            # Save to database (placeholder)
            await self._save_organization(organization_data)
            
            # Generate initial API key
            api_key = await self.generate_api_key(org_id, "Default API Key")
            
            self.logger.info(f"Created organization: {org_id}")
            
            return {
                "organization_id": org_id,
                "api_key": api_key,
                "stripe_customer_id": stripe_customer.id
            }
            
        except Exception as e:
            self.logger.error(f"Organization creation error: {e}")
            raise
    
    async def upgrade_subscription(
        self, 
        organization_id: str, 
        new_tier: SubscriptionTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ) -> Dict[str, Any]:
        """Upgrade organization subscription"""
        try:
            # Get organization data
            org_data = await self._get_organization(organization_id)
            tier_limits = SUBSCRIPTION_TIERS[new_tier]
            
            # Calculate price
            price = tier_limits.yearly_price_usd if billing_cycle == BillingCycle.YEARLY else tier_limits.monthly_price_usd
            
            # Create Stripe subscription
            stripe_subscription = stripe.Subscription.create(
                customer=org_data["stripe_customer_id"],
                items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Islamic AI {tier_limits.name}",
                            "description": f"Islamic AI API access - {tier_limits.name} tier"
                        },
                        "unit_amount": int(price * 100),  # Convert to cents
                        "recurring": {
                            "interval": "month" if billing_cycle == BillingCycle.MONTHLY else "year"
                        }
                    }
                }],
                metadata={
                    "organization_id": organization_id,
                    "tier": new_tier.value
                }
            )
            
            # Update organization
            await self._update_organization_subscription(
                organization_id,
                new_tier,
                billing_cycle,
                stripe_subscription.id
            )
            
            # Update metrics
            self.active_subscriptions_gauge.labels(tier=new_tier.value).inc()
            if org_data["subscription_tier"] != SubscriptionTier.FREE:
                self.active_subscriptions_gauge.labels(tier=org_data["subscription_tier"]).dec()
            
            self.logger.info(f"Upgraded subscription: {organization_id} to {new_tier.value}")
            
            return {
                "subscription_id": stripe_subscription.id,
                "tier": new_tier.value,
                "monthly_price": float(price),
                "next_billing_date": stripe_subscription.current_period_end
            }
            
        except Exception as e:
            self.logger.error(f"Subscription upgrade error: {e}")
            raise
    
    # API Key Management
    async def generate_api_key(self, organization_id: str, key_name: str) -> str:
        """Generate new API key for organization"""
        try:
            # Generate secure API key
            api_key = self._generate_secure_api_key()
            key_hash = self._hash_api_key(api_key)
            key_prefix = api_key[:8]
            
            # Save to database
            api_key_data = {
                "id": str(uuid.uuid4()),
                "organization_id": organization_id,
                "key_name": key_name,
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "permissions": [],  # Will inherit from organization tier
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            
            await self._save_api_key(api_key_data)
            
            self.logger.info(f"Generated API key for organization: {organization_id}")
            
            return api_key
            
        except Exception as e:
            self.logger.error(f"API key generation error: {e}")
            raise
    
    async def revoke_api_key(self, organization_id: str, api_key_id: str):
        """Revoke API key"""
        try:
            await self._deactivate_api_key(api_key_id)
            
            # Clear from cache
            await self.redis_client.delete(f"auth:*")  # Clear all auth cache
            
            self.logger.info(f"Revoked API key: {api_key_id}")
            
        except Exception as e:
            self.logger.error(f"API key revocation error: {e}")
            raise
    
    # Analytics and Reporting
    async def get_organization_analytics(
        self, 
        organization_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for organization"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get usage data
            usage_data = await self._get_usage_analytics(organization_id, start_date, end_date)
            
            # Get tier information
            tier_info = await self._get_organization_tier(organization_id)
            tier_limits = SUBSCRIPTION_TIERS[tier_info["tier"]]
            
            # Calculate quota usage
            current_month_usage = await self._get_monthly_usage(organization_id)
            quota_percentage = (current_month_usage / tier_limits.monthly_api_calls) * 100
            
            return {
                "period_days": days,
                "total_api_calls": usage_data["total_calls"],
                "total_video_generations": usage_data["video_generations"],
                "average_response_time_ms": usage_data["avg_response_time"],
                "error_rate_percentage": usage_data["error_rate"],
                "current_month_quota_used": quota_percentage,
                "tier_limits": {
                    "monthly_api_calls": tier_limits.monthly_api_calls,
                    "daily_api_calls": tier_limits.daily_api_calls,
                    "video_generations_monthly": tier_limits.video_generations_monthly,
                    "rate_limit_per_minute": tier_limits.rate_limit_per_minute
                },
                "usage_by_endpoint": usage_data["endpoint_breakdown"],
                "daily_usage": usage_data["daily_breakdown"]
            }
            
        except Exception as e:
            self.logger.error(f"Analytics error: {e}")
            raise
    
    # Billing and Invoicing
    async def generate_invoice(self, organization_id: str, period_start: datetime, period_end: datetime):
        """Generate invoice for billing period"""
        try:
            # Get usage data for period
            usage_data = await self._get_usage_for_period(organization_id, period_start, period_end)
            
            # Get organization and tier info
            org_data = await self._get_organization(organization_id)
            tier_limits = SUBSCRIPTION_TIERS[org_data["subscription_tier"]]
            
            # Calculate costs
            base_cost = float(tier_limits.monthly_price_usd)
            overage_cost = 0.0
            
            # Calculate overage charges
            if usage_data["api_calls"] > tier_limits.monthly_api_calls:
                overage_calls = usage_data["api_calls"] - tier_limits.monthly_api_calls
                overage_cost += overage_calls * 0.001  # $0.001 per overage call
            
            if usage_data["video_generations"] > tier_limits.video_generations_monthly:
                overage_videos = usage_data["video_generations"] - tier_limits.video_generations_monthly
                overage_cost += overage_videos * 0.50  # $0.50 per overage video
            
            subtotal = base_cost + overage_cost
            tax = subtotal * 0.08 if org_data.get("country") == "US" else 0.0  # Simplified tax calculation
            total = subtotal + tax
            
            # Create invoice
            invoice_data = {
                "id": str(uuid.uuid4()),
                "organization_id": organization_id,
                "invoice_number": self._generate_invoice_number(),
                "period_start": period_start,
                "period_end": period_end,
                "subtotal_usd": subtotal,
                "tax_usd": tax,
                "total_usd": total,
                "api_calls_count": usage_data["api_calls"],
                "video_generations_count": usage_data["video_generations"],
                "status": "pending",
                "due_date": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow()
            }
            
            await self._save_invoice(invoice_data)
            
            # Create Stripe invoice
            stripe_invoice = stripe.Invoice.create(
                customer=org_data["stripe_customer_id"],
                collection_method="charge_automatically",
                metadata={
                    "organization_id": organization_id,
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat()
                }
            )
            
            # Add line items
            stripe.InvoiceItem.create(
                customer=org_data["stripe_customer_id"],
                invoice=stripe_invoice.id,
                amount=int(base_cost * 100),
                currency="usd",
                description=f"Islamic AI {tier_limits.name} - {period_start.strftime('%B %Y')}"
            )
            
            if overage_cost > 0:
                stripe.InvoiceItem.create(
                    customer=org_data["stripe_customer_id"],
                    invoice=stripe_invoice.id,
                    amount=int(overage_cost * 100),
                    currency="usd",
                    description="Usage overage charges"
                )
            
            # Finalize and send invoice
            stripe_invoice.finalize_invoice()
            
            return invoice_data
            
        except Exception as e:
            self.logger.error(f"Invoice generation error: {e}")
            raise
    
    # Utility methods
    def _generate_secure_api_key(self) -> str:
        """Generate cryptographically secure API key"""
        return f"budul_{''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))}"
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        return f"INV-{datetime.utcnow().strftime('%Y%m')}-{secrets.randbelow(999999):06d}"
    
    # Database operations (placeholders for actual implementation)
    async def _query_api_key_auth(self, key_hash: str) -> Optional[Dict]: return None
    async def _get_organization_tier(self, org_id: str) -> Dict: return {"tier": SubscriptionTier.FREE}
    async def _get_monthly_usage(self, org_id: str) -> int: return 0
    async def _log_usage(self, org_id: str, endpoint: str, data: Dict): pass
    async def _update_api_key_usage(self, api_key_id: str): pass
    async def _save_organization(self, data: Dict): pass
    async def _get_organization(self, org_id: str) -> Dict: return {}
    async def _update_organization_subscription(self, org_id: str, tier: SubscriptionTier, cycle: BillingCycle, stripe_id: str): pass
    async def _save_api_key(self, data: Dict): pass
    async def _deactivate_api_key(self, api_key_id: str): pass
    async def _get_usage_analytics(self, org_id: str, start: datetime, end: datetime) -> Dict: return {}
    async def _get_usage_for_period(self, org_id: str, start: datetime, end: datetime) -> Dict: return {}
    async def _save_invoice(self, data: Dict): pass
    async def _setup_stripe_webhooks(self): pass

# Global platform instance
saas_platform = IslamicAISaaSPlatform()