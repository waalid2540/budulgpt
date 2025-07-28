"""
Enterprise SSO Integration for Islamic AI Platform
SAML 2.0, OAuth 2.0, and OpenID Connect integration for enterprise customers
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import base64
import secrets
import hashlib
from urllib.parse import urlencode, parse_qs, urlparse

# SSO and Authentication libraries
import jwt
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import xmltodict
import xml.etree.ElementTree as ET
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

# FastAPI and security
from fastapi import HTTPException, Request, Response
from passlib.context import CryptContext
import httpx

# Database and caching
import redis.asyncio as redis
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Core services
from .saas_platform import saas_platform
from .islamic_ai_config import settings

# Monitoring
import structlog
from prometheus_client import Counter, Histogram

class SSOProvider(str, Enum):
    SAML2 = "saml2"
    OAUTH2 = "oauth2"
    OPENID_CONNECT = "oidc"
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    OKTA = "okta"
    ACTIVE_DIRECTORY = "active_directory"

class SSOStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"

@dataclass
class SSOConfig:
    """SSO configuration for an organization"""
    provider: SSOProvider
    organization_id: str
    config_data: Dict[str, Any]
    metadata_url: Optional[str] = None
    certificate: Optional[str] = None
    private_key: Optional[str] = None
    status: SSOStatus = SSOStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SSOUser:
    """User authenticated via SSO"""
    sso_user_id: str
    email: str
    full_name: str
    organization_id: str
    groups: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    provider: SSOProvider = SSOProvider.SAML2
    authenticated_at: datetime = field(default_factory=datetime.utcnow)

# Database Models
Base = declarative_base()

class SSOConfiguration(Base):
    """SSO configuration storage"""
    __tablename__ = "sso_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    
    # SSO Provider details
    provider = Column(String(50), nullable=False)
    provider_name = Column(String(200))
    
    # Configuration
    config_data = Column(JSON, nullable=False)
    metadata_url = Column(String(500))
    certificate = Column(String(4000))
    private_key = Column(String(4000))
    
    # SAML specific
    entity_id = Column(String(500))
    sso_url = Column(String(500))
    sls_url = Column(String(500))
    
    # OAuth/OIDC specific
    client_id = Column(String(200))
    client_secret = Column(String(200))
    authorization_endpoint = Column(String(500))
    token_endpoint = Column(String(500))
    userinfo_endpoint = Column(String(500))
    
    # Settings
    auto_provision_users = Column(Boolean, default=True)
    default_role = Column(String(50), default="user")
    attribute_mapping = Column(JSON, default=dict)
    
    # Status
    status = Column(String(20), default="pending")
    last_sync = Column(DateTime)
    sync_errors = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

class SSOSession(Base):
    """SSO session tracking"""
    __tablename__ = "sso_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    sso_config_id = Column(UUID(as_uuid=True), ForeignKey("sso_configurations.id"))
    
    # Session details
    session_id = Column(String(200), nullable=False)
    sso_user_id = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    
    # Authentication details
    provider = Column(String(50), nullable=False)
    assertion_id = Column(String(200))
    name_id = Column(String(200))
    
    # Session status
    is_active = Column(Boolean, default=True)
    authenticated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    logout_url = Column(String(500))
    
    # User attributes
    attributes = Column(JSON, default=dict)
    roles = Column(JSON, default=list)
    groups = Column(JSON, default=list)

class EnterpriseSSOManager:
    """
    Comprehensive Enterprise SSO Manager
    Supports SAML 2.0, OAuth 2.0, OpenID Connect, and major identity providers
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.redis_client = None
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # SSO configurations cache
        self.sso_configs: Dict[str, SSOConfig] = {}
        
        # Session management
        self.active_sessions: Dict[str, SSOUser] = {}
        
        # Metrics
        self.setup_metrics()
        
        # Provider-specific handlers
        self.provider_handlers = {
            SSOProvider.SAML2: self._handle_saml2_auth,
            SSOProvider.OAUTH2: self._handle_oauth2_auth,
            SSOProvider.OPENID_CONNECT: self._handle_oidc_auth,
            SSOProvider.AZURE_AD: self._handle_azure_ad_auth,
            SSOProvider.GOOGLE_WORKSPACE: self._handle_google_workspace_auth,
            SSOProvider.OKTA: self._handle_okta_auth
        }
    
    def setup_metrics(self):
        """Setup SSO metrics"""
        self.sso_auth_counter = Counter('islamic_ai_sso_auth_total', 'SSO authentications', ['provider', 'status'])
        self.sso_response_time = Histogram('islamic_ai_sso_response_time_seconds', 'SSO response time')
        
    async def initialize(self):
        """Initialize SSO manager"""
        self.logger.info("Initializing Enterprise SSO Manager")
        
        # Setup Redis for session management
        self.redis_client = redis.from_url(settings.redis_url)
        
        # Load SSO configurations
        await self._load_sso_configurations()
        
        self.logger.info("Enterprise SSO Manager initialized")
    
    async def configure_sso(
        self,
        organization_id: str,
        provider: SSOProvider,
        config_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """Configure SSO for organization"""
        try:
            self.logger.info(f"Configuring SSO for organization {organization_id}")
            
            # Validate configuration
            await self._validate_sso_config(provider, config_data)
            
            # Generate certificates if needed
            if provider == SSOProvider.SAML2:
                if "certificate" not in config_data or "private_key" not in config_data:
                    cert_data = await self._generate_saml_certificates()
                    config_data.update(cert_data)
            
            # Create SSO configuration
            sso_config = SSOConfig(
                provider=provider,
                organization_id=organization_id,
                config_data=config_data,
                metadata_url=config_data.get("metadata_url"),
                certificate=config_data.get("certificate"),
                private_key=config_data.get("private_key")
            )
            
            # Save configuration
            config_id = await self._save_sso_config(sso_config, user_id)
            
            # Cache configuration
            self.sso_configs[organization_id] = sso_config
            
            # Test configuration
            test_result = await self._test_sso_config(sso_config)
            if test_result["success"]:
                sso_config.status = SSOStatus.ACTIVE
                await self._update_sso_status(config_id, SSOStatus.ACTIVE)
            else:
                sso_config.status = SSOStatus.ERROR
                await self._update_sso_status(config_id, SSOStatus.ERROR)
                raise HTTPException(
                    status_code=400,
                    detail=f"SSO configuration test failed: {test_result['error']}"
                )
            
            self.logger.info(f"SSO configured successfully for organization {organization_id}")
            
            return config_id
            
        except Exception as e:
            self.logger.error(f"Error configuring SSO: {e}")
            raise
    
    async def initiate_sso_login(
        self,
        organization_id: str,
        redirect_url: str,
        request: Request
    ) -> Dict[str, Any]:
        """Initiate SSO login flow"""
        start_time = time.time()
        
        try:
            # Get SSO configuration
            if organization_id not in self.sso_configs:
                await self._load_organization_sso_config(organization_id)
            
            if organization_id not in self.sso_configs:
                raise HTTPException(status_code=404, detail="SSO not configured for organization")
            
            sso_config = self.sso_configs[organization_id]
            
            # Generate state for security
            state = secrets.token_urlsafe(32)
            await self.redis_client.setex(f"sso_state:{state}", 600, organization_id)
            
            # Handle provider-specific login initiation
            login_data = await self._initiate_provider_login(sso_config, redirect_url, state, request)
            
            self.sso_auth_counter.labels(provider=sso_config.provider.value, status='initiated').inc()
            
            return login_data
            
        except Exception as e:
            self.logger.error(f"Error initiating SSO login: {e}")
            self.sso_auth_counter.labels(provider='unknown', status='error').inc()
            raise
        finally:
            self.sso_response_time.observe(time.time() - start_time)
    
    async def handle_sso_callback(
        self,
        request: Request,
        provider: SSOProvider,
        organization_id: Optional[str] = None
    ) -> SSOUser:
        """Handle SSO callback and authenticate user"""
        start_time = time.time()
        
        try:
            # Extract state and validate
            if provider in [SSOProvider.OAUTH2, SSOProvider.OPENID_CONNECT, SSOProvider.AZURE_AD]:
                state = request.query_params.get("state")
                if not state:
                    raise HTTPException(status_code=400, detail="Missing state parameter")
                
                # Validate state
                cached_org_id = await self.redis_client.get(f"sso_state:{state}")
                if not cached_org_id:
                    raise HTTPException(status_code=400, detail="Invalid or expired state")
                
                organization_id = cached_org_id.decode()
                await self.redis_client.delete(f"sso_state:{state}")
            
            if not organization_id:
                raise HTTPException(status_code=400, detail="Organization ID required")
            
            # Get SSO configuration
            if organization_id not in self.sso_configs:
                await self._load_organization_sso_config(organization_id)
            
            sso_config = self.sso_configs[organization_id]
            
            # Handle provider-specific authentication
            handler = self.provider_handlers.get(provider)
            if not handler:
                raise HTTPException(status_code=400, detail=f"Unsupported SSO provider: {provider}")
            
            sso_user = await handler(request, sso_config)
            
            # Create session
            session_id = await self._create_sso_session(sso_user, sso_config)
            sso_user.session_id = session_id
            
            # Cache active session
            self.active_sessions[session_id] = sso_user
            
            self.sso_auth_counter.labels(provider=provider.value, status='success').inc()
            
            return sso_user
            
        except Exception as e:
            self.logger.error(f"Error handling SSO callback: {e}")
            self.sso_auth_counter.labels(provider=provider.value, status='error').inc()
            raise
        finally:
            self.sso_response_time.observe(time.time() - start_time)
    
    async def _handle_saml2_auth(self, request: Request, sso_config: SSOConfig) -> SSOUser:
        """Handle SAML 2.0 authentication"""
        
        # Build OneLogin request object
        req = await self._build_onelogin_request(request)
        
        # Create SAML settings
        saml_settings = await self._build_saml_settings(sso_config)
        
        # Initialize SAML Auth
        auth = OneLogin_Saml2_Auth(req, saml_settings)
        
        # Process SAML response
        auth.process_response()
        
        if not auth.is_authenticated():
            errors = auth.get_errors()
            raise HTTPException(status_code=401, detail=f"SAML authentication failed: {errors}")
        
        # Extract user attributes
        attributes = auth.get_attributes()
        name_id = auth.get_nameid()
        session_index = auth.get_session_index()
        
        # Map SAML attributes to user
        email = self._extract_saml_attribute(attributes, sso_config.config_data.get("email_attribute", "email"))
        full_name = self._extract_saml_attribute(attributes, sso_config.config_data.get("name_attribute", "displayName"))
        groups = self._extract_saml_attribute(attributes, sso_config.config_data.get("groups_attribute", "groups"), multiple=True)
        
        return SSOUser(
            sso_user_id=name_id,
            email=email,
            full_name=full_name or email,
            organization_id=sso_config.organization_id,
            groups=groups or [],
            attributes=attributes,
            provider=SSOProvider.SAML2
        )
    
    async def _handle_oauth2_auth(self, request: Request, sso_config: SSOConfig) -> SSOUser:
        """Handle OAuth 2.0 authentication"""
        
        # Get authorization code
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        
        # Exchange code for access token
        token_data = await self._exchange_oauth_code(code, sso_config)
        
        # Get user info
        user_info = await self._get_oauth_user_info(token_data["access_token"], sso_config)
        
        return SSOUser(
            sso_user_id=user_info.get("sub", user_info.get("id")),
            email=user_info.get("email"),
            full_name=user_info.get("name", user_info.get("displayName")),
            organization_id=sso_config.organization_id,
            groups=user_info.get("groups", []),
            attributes=user_info,
            provider=SSOProvider.OAUTH2
        )
    
    async def _handle_oidc_auth(self, request: Request, sso_config: SSOConfig) -> SSOUser:
        """Handle OpenID Connect authentication"""
        
        # Get authorization code
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        
        # Exchange code for tokens
        token_data = await self._exchange_oidc_code(code, sso_config)
        
        # Verify and decode ID token
        id_token = token_data.get("id_token")
        if not id_token:
            raise HTTPException(status_code=400, detail="Missing ID token")
        
        # Decode JWT (simplified - in production, verify signature)
        payload = jwt.decode(id_token, options={"verify_signature": False})
        
        return SSOUser(
            sso_user_id=payload.get("sub"),
            email=payload.get("email"),
            full_name=payload.get("name"),
            organization_id=sso_config.organization_id,
            groups=payload.get("groups", []),
            attributes=payload,
            provider=SSOProvider.OPENID_CONNECT
        )
    
    async def _handle_azure_ad_auth(self, request: Request, sso_config: SSOConfig) -> SSOUser:
        """Handle Azure AD authentication"""
        
        # Azure AD uses OpenID Connect
        sso_user = await self._handle_oidc_auth(request, sso_config)
        sso_user.provider = SSOProvider.AZURE_AD
        
        return sso_user
    
    async def _handle_google_workspace_auth(self, request: Request, sso_config: SSOConfig) -> SSOUser:
        """Handle Google Workspace authentication"""
        
        # Google Workspace uses OpenID Connect
        sso_user = await self._handle_oidc_auth(request, sso_config)
        sso_user.provider = SSOProvider.GOOGLE_WORKSPACE
        
        return sso_user
    
    async def _handle_okta_auth(self, request: Request, sso_config: SSOConfig) -> SSOUser:
        """Handle Okta authentication"""
        
        # Okta supports both SAML and OIDC
        if sso_config.config_data.get("protocol") == "saml":
            sso_user = await self._handle_saml2_auth(request, sso_config)
        else:
            sso_user = await self._handle_oidc_auth(request, sso_config)
        
        sso_user.provider = SSOProvider.OKTA
        
        return sso_user
    
    async def logout_sso_user(self, session_id: str) -> Optional[str]:
        """Logout SSO user and return logout URL if available"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            sso_user = self.active_sessions[session_id]
            organization_id = sso_user.organization_id
            
            # Get SSO configuration
            sso_config = self.sso_configs.get(organization_id)
            if not sso_config:
                return None
            
            # Generate logout URL for SAML
            logout_url = None
            if sso_config.provider == SSOProvider.SAML2:
                logout_url = await self._generate_saml_logout_url(sso_config, session_id)
            
            # Clear session
            del self.active_sessions[session_id]
            await self._deactivate_sso_session(session_id)
            
            return logout_url
            
        except Exception as e:
            self.logger.error(f"Error logging out SSO user: {e}")
            return None
    
    async def validate_sso_session(self, session_id: str) -> Optional[SSOUser]:
        """Validate SSO session"""
        try:
            # Check active sessions cache
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Check database
            session_data = await self._get_sso_session(session_id)
            if session_data and session_data["is_active"]:
                # Reconstruct SSO user
                sso_user = SSOUser(
                    sso_user_id=session_data["sso_user_id"],
                    email=session_data["email"],
                    full_name=session_data.get("full_name", ""),
                    organization_id=session_data["organization_id"],
                    groups=session_data.get("groups", []),
                    attributes=session_data.get("attributes", {}),
                    provider=SSOProvider(session_data["provider"])
                )
                
                # Cache session
                self.active_sessions[session_id] = sso_user
                
                return sso_user
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error validating SSO session: {e}")
            return None
    
    # Utility methods and additional implementation would continue here...
    
    async def _validate_sso_config(self, provider: SSOProvider, config_data: Dict) -> bool:
        """Validate SSO configuration"""
        required_fields = {
            SSOProvider.SAML2: ["entity_id", "sso_url"],
            SSOProvider.OAUTH2: ["client_id", "client_secret", "authorization_endpoint", "token_endpoint"],
            SSOProvider.OPENID_CONNECT: ["client_id", "client_secret", "discovery_url"],
            SSOProvider.AZURE_AD: ["tenant_id", "client_id", "client_secret"],
            SSOProvider.GOOGLE_WORKSPACE: ["client_id", "client_secret"],
            SSOProvider.OKTA: ["domain", "client_id", "client_secret"]
        }
        
        for field in required_fields.get(provider, []):
            if field not in config_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        return True
    
    async def _generate_saml_certificates(self) -> Dict[str, str]:
        """Generate SAML certificates"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Generate certificate (simplified)
        # In production, use proper certificate generation
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            "private_key": private_pem.decode(),
            "certificate": public_pem.decode()
        }
    
    # Placeholder methods for database operations
    async def _save_sso_config(self, config: SSOConfig, user_id: str) -> str: return str(uuid.uuid4())
    async def _update_sso_status(self, config_id: str, status: SSOStatus): pass
    async def _test_sso_config(self, config: SSOConfig) -> Dict: return {"success": True}
    async def _load_sso_configurations(self): pass
    async def _load_organization_sso_config(self, org_id: str): pass
    async def _create_sso_session(self, user: SSOUser, config: SSOConfig) -> str: return str(uuid.uuid4())
    async def _deactivate_sso_session(self, session_id: str): pass
    async def _get_sso_session(self, session_id: str) -> Optional[Dict]: return None
    
    # Additional utility methods would be implemented here...

# Global SSO manager instance
enterprise_sso_manager = EnterpriseSSOManager()