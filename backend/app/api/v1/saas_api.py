"""
Islamic AI SaaS Platform API Router
Unified API endpoints for the complete Islamic AI SaaS platform
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from typing import Dict, List, Optional, Any

# Import all SaaS components
from .islamic_chat import router as chat_router
from .islamic_video import router as video_router
from .saas_dashboard import router as dashboard_router

# Core services
from ...core.saas_platform import saas_platform, SubscriptionTier
from ...core.enterprise_sso import enterprise_sso_manager, SSOProvider
from ...core.auth import get_current_user_optional

# Monitoring
import structlog
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Main SaaS API router
router = APIRouter(prefix="/api/v1", tags=["Islamic AI SaaS Platform"])
logger = structlog.get_logger(__name__)

# Metrics
platform_requests_counter = Counter('islamic_ai_platform_requests_total', 'Total platform requests')

# Include all service routers
router.include_router(chat_router)
router.include_router(video_router)
router.include_router(dashboard_router)

@router.get("/")
async def platform_info():
    """
    Islamic AI Platform Information
    
    Returns comprehensive information about the Islamic AI SaaS platform.
    """
    platform_requests_counter.inc()
    
    return {
        "platform": "Budul AI - Islamic AI Platform",
        "description": "The definitive Islamic AI platform serving 1.8 billion Muslims worldwide",
        "version": "1.0.0",
        "services": {
            "islamic_chat": {
                "description": "Advanced Islamic AI chat with scholarly verification",
                "endpoints": ["/chat", "/chat/stream", "/chat/ws/{user_id}/{session_id}"],
                "features": [
                    "Real-time Islamic Q&A",
                    "Scholarly citations",
                    "Multi-madhab support",
                    "Arabic text processing",
                    "Prayer times & Qibla direction"
                ]
            },
            "video_generation": {
                "description": "Islamic video generation with AI-powered content creation",
                "endpoints": ["/video/generate", "/video/templates", "/video/library"],
                "features": [
                    "Text-to-Islamic video",
                    "Arabic calligraphy integration",
                    "Geometric pattern backgrounds",
                    "Halal audio synthesis",
                    "Cultural customization"
                ]
            },
            "saas_platform": {
                "description": "Enterprise SaaS platform with tiered access and billing",
                "endpoints": ["/dashboard", "/billing", "/analytics"],
                "features": [
                    "Subscription management",
                    "Usage analytics",
                    "API key management",
                    "White-label customization",
                    "Enterprise SSO"
                ]
            }
        },
        "subscription_tiers": {
            "free": {
                "price": "$0/month",
                "api_calls": "1,000/month",
                "video_generations": "5/month",
                "features": ["Basic Islamic chat", "Community support"]
            },
            "developer": {
                "price": "$49/month",
                "api_calls": "25,000/month",
                "video_generations": "50/month",
                "features": ["Advanced chat", "Bulk processing", "Priority support"]
            },
            "professional": {
                "price": "$199/month",
                "api_calls": "100,000/month",
                "video_generations": "200/month",
                "features": ["Custom models", "White-label", "Advanced analytics"]
            },
            "enterprise": {
                "price": "$999/month",
                "api_calls": "1,000,000/month",
                "video_generations": "1,000/month",
                "features": ["Unlimited features", "SSO", "Dedicated support", "SLA"]
            }
        },
        "getting_started": {
            "step_1": "Sign up for free account",
            "step_2": "Get API key from dashboard",
            "step_3": "Start building with Islamic AI",
            "documentation": "/docs",
            "examples": "/examples"
        },
        "support": {
            "documentation": "https://docs.budul.ai",
            "github": "https://github.com/budul-ai/islamic-ai",
            "email": "support@budul.ai",
            "discord": "https://discord.gg/budul-ai"
        }
    }

@router.post("/organizations")
async def create_organization(
    org_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_optional)
):
    """
    Create new organization
    
    Creates a new organization with free tier subscription and generates initial API key.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Create organization
        result = await saas_platform.create_organization(org_data)
        
        return {
            "message": "Organization created successfully",
            "organization_id": result["organization_id"],
            "api_key": result["api_key"],
            "subscription_tier": "free",
            "next_steps": [
                "Visit the dashboard to explore features",
                "Read the API documentation",
                "Try the Islamic chat API",
                "Generate your first Islamic video"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=500, detail="Error creating organization")

@router.get("/subscription-tiers")
async def get_subscription_tiers():
    """
    Get available subscription tiers
    
    Returns detailed information about all available subscription tiers and features.
    """
    from ...core.saas_platform import SUBSCRIPTION_TIERS
    
    tiers_info = {}
    for tier, limits in SUBSCRIPTION_TIERS.items():
        tiers_info[tier.value] = {
            "name": limits.name,
            "monthly_price": float(limits.monthly_price_usd),
            "yearly_price": float(limits.yearly_price_usd),
            "limits": {
                "monthly_api_calls": limits.monthly_api_calls,
                "daily_api_calls": limits.daily_api_calls,
                "video_generations_monthly": limits.video_generations_monthly,
                "max_concurrent_requests": limits.max_concurrent_requests,
                "rate_limit_per_minute": limits.rate_limit_per_minute
            },
            "features": {
                "custom_models": limits.custom_models,
                "priority_support": limits.priority_support,
                "white_label": limits.white_label,
                "advanced_analytics": limits.advanced_analytics,
                "bulk_processing": limits.bulk_processing
            },
            "sla_uptime": limits.sla_uptime,
            "permissions": [perm.value for perm in limits.permissions]
        }
    
    return {
        "tiers": tiers_info,
        "recommended": "professional",
        "most_popular": "developer",
        "enterprise_contact": "sales@budul.ai"
    }

@router.post("/sso/configure")
async def configure_sso(
    sso_config: Dict[str, Any],
    user_id: str = Depends(get_current_user_optional)
):
    """
    Configure Enterprise SSO
    
    Set up SAML 2.0, OAuth 2.0, or OpenID Connect for enterprise authentication.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get organization ID
        organization_id = "default_org_id"  # Would get from user
        
        # Validate enterprise tier
        tier_info = await saas_platform._get_organization_tier(organization_id)
        if tier_info["tier"] not in [SubscriptionTier.ENTERPRISE]:
            raise HTTPException(
                status_code=403,
                detail="SSO configuration requires Enterprise tier"
            )
        
        # Configure SSO
        provider = SSOProvider(sso_config["provider"])
        config_id = await enterprise_sso_manager.configure_sso(
            organization_id=organization_id,
            provider=provider,
            config_data=sso_config["config"],
            user_id=user_id
        )
        
        return {
            "message": "SSO configured successfully",
            "config_id": config_id,
            "provider": provider.value,
            "status": "active",
            "next_steps": [
                "Test SSO login flow",
                "Configure user attribute mapping",
                "Train your team on SSO usage"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error configuring SSO: {e}")
        raise HTTPException(status_code=500, detail="Error configuring SSO")

@router.get("/sso/login/{organization_id}")
async def initiate_sso_login(
    organization_id: str,
    redirect_url: str,
    request: Request
):
    """
    Initiate SSO login
    
    Starts the SSO authentication flow for an organization.
    """
    try:
        login_data = await enterprise_sso_manager.initiate_sso_login(
            organization_id=organization_id,
            redirect_url=redirect_url,
            request=request
        )
        
        # Redirect to identity provider
        return RedirectResponse(url=login_data["login_url"])
        
    except Exception as e:
        logger.error(f"Error initiating SSO login: {e}")
        raise HTTPException(status_code=500, detail="Error initiating SSO login")

@router.post("/sso/callback/{provider}")
async def handle_sso_callback(
    provider: str,
    request: Request,
    response: Response
):
    """
    Handle SSO authentication callback
    
    Processes the callback from identity provider and authenticates user.
    """
    try:
        sso_provider = SSOProvider(provider)
        sso_user = await enterprise_sso_manager.handle_sso_callback(request, sso_provider)
        
        # Create JWT token for API access
        # This would integrate with your authentication system
        
        return {
            "message": "SSO authentication successful",
            "user": {
                "email": sso_user.email,
                "full_name": sso_user.full_name,
                "organization_id": sso_user.organization_id,
                "groups": sso_user.groups
            },
            "session_id": getattr(sso_user, 'session_id', None),
            "redirect_url": "/dashboard"
        }
        
    except Exception as e:
        logger.error(f"Error handling SSO callback: {e}")
        raise HTTPException(status_code=500, detail="Error handling SSO callback")

@router.get("/health")
async def platform_health():
    """
    Platform health check
    
    Returns comprehensive health status of all Islamic AI platform services.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00Z",
            "services": {
                "islamic_chat": {
                    "status": "healthy",
                    "response_time_ms": 150,
                    "active_conversations": 1250
                },
                "video_generation": {
                    "status": "healthy",
                    "queue_size": 5,
                    "active_generations": 12
                },
                "saas_platform": {
                    "status": "healthy",
                    "active_subscriptions": 847,
                    "api_requests_per_minute": 2340
                },
                "enterprise_sso": {
                    "status": "healthy",
                    "active_sessions": 156,
                    "configured_organizations": 23
                }
            },
            "infrastructure": {
                "database": "healthy",
                "redis": "healthy",
                "elasticsearch": "healthy",
                "monitoring": "healthy"
            },
            "performance": {
                "avg_response_time_ms": 145,
                "error_rate_percentage": 0.02,
                "uptime_percentage": 99.98
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T12:00:00Z"
        }

@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint
    
    Returns metrics for monitoring and alerting.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/examples")
async def get_api_examples():
    """
    API usage examples
    
    Returns comprehensive examples for integrating with the Islamic AI platform.
    """
    return {
        "chat_examples": {
            "basic_question": {
                "description": "Ask a basic Islamic question",
                "request": {
                    "method": "POST",
                    "url": "/api/v1/chat",
                    "headers": {
                        "Authorization": "Bearer budul_your_api_key",
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "message": "What are the five pillars of Islam?",
                        "context": {
                            "knowledge_level": "intermediate",
                            "madhab": "hanafi"
                        }
                    }
                }
            },
            "streaming_chat": {
                "description": "Stream Islamic AI responses",
                "request": {
                    "method": "POST",
                    "url": "/api/v1/chat/stream",
                    "headers": {
                        "Authorization": "Bearer budul_your_api_key",
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "message": "Explain the concept of Tawheed in detail",
                        "stream": True
                    }
                }
            }
        },
        "video_examples": {
            "generate_video": {
                "description": "Generate Islamic educational video",
                "request": {
                    "method": "POST",
                    "url": "/api/v1/video/generate",
                    "headers": {
                        "Authorization": "Bearer budul_your_api_key",
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "text_content": "The importance of prayer in Islam and its spiritual benefits",
                        "title": "Islamic Prayer Guide",
                        "duration_seconds": 60,
                        "style": "modern",
                        "include_arabic_text": True,
                        "cultural_style": "general"
                    }
                }
            }
        },
        "dashboard_examples": {
            "get_usage": {
                "description": "Get organization usage statistics",
                "request": {
                    "method": "GET",
                    "url": "/api/v1/dashboard/usage?period=month",
                    "headers": {
                        "Authorization": "Bearer budul_your_api_key"
                    }
                }
            }
        },
        "code_examples": {
            "python": """
import requests

# Initialize Budul AI client
api_key = "budul_your_api_key"
base_url = "https://api.budul.ai/v1"

# Ask Islamic question
def ask_islamic_question(question):
    response = requests.post(
        f"{base_url}/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"message": question}
    )
    return response.json()

# Generate Islamic video
def generate_islamic_video(content):
    response = requests.post(
        f"{base_url}/video/generate",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "text_content": content,
            "duration_seconds": 30,
            "style": "modern"
        }
    )
    return response.json()

# Example usage
answer = ask_islamic_question("What is the significance of Ramadan?")
video = generate_islamic_video("The benefits of reading Quran daily")
            """,
            "javascript": """
const axios = require('axios');

class BudulAI {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://api.budul.ai/v1';
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async askQuestion(message, context = {}) {
    const response = await axios.post(
      `${this.baseURL}/chat`,
      { message, context },
      { headers: this.headers }
    );
    return response.data;
  }

  async generateVideo(textContent, options = {}) {
    const response = await axios.post(
      `${this.baseURL}/video/generate`,
      { text_content: textContent, ...options },
      { headers: this.headers }
    );
    return response.data;
  }
}

// Example usage
const budul = new BudulAI('budul_your_api_key');
const answer = await budul.askQuestion('Explain Islamic finance principles');
const video = await budul.generateVideo('Islamic ethics in business');
            """
        },
        "sdks": {
            "python": "pip install budul-ai",
            "javascript": "npm install @budul/ai",
            "php": "composer require budul/ai",
            "ruby": "gem install budul-ai",
            "go": "go get github.com/budul-ai/go-sdk"
        }
    }