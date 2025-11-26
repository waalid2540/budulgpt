# Global Waqaf Tech - Architecture & Implementation Plan

## 📋 Executive Summary

This document outlines the complete transformation of **Madina GPT** into **Global Waqaf Tech** - a multi-tenant SaaS platform serving masajid and Islamic organizations worldwide.

**Current State:**
- Single-user Islamic AI platform (MadinaGPT)
- 4 features: Islamic Chat, Du'a Generator, Kids Stories, Umrah Deal Finder
- Python FastAPI backend + Next.js frontend
- No multi-tenancy, no organization management

**Target State:**
- Multi-tenant platform with organizations as first-class citizens
- Role-based access control (Super Admin, Org Admin, Org User)
- 7+ features including existing + new modules
- Unified dashboard with plan-based access control
- Revenue-generating platform for masajid

---

## 🏗️ System Architecture

### Technology Stack (Unchanged)
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **AI/LLM:** OpenAI GPT (existing integration)
- **Auth:** JWT-based authentication

### New Architectural Patterns
1. **Multi-tenancy:** Organization-scoped data isolation
2. **Role-Based Access Control (RBAC):** 3-tier permission system
3. **Feature Flagging:** Plan-based feature access
4. **Modular Services:** Each feature is a self-contained service module

---

## 📊 Database Schema Design

### Core Multi-Tenant Models

#### 1. Organization Model
```python
class Organization(Base):
    __tablename__ = "organizations"

    # Primary
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)

    # Organization Type
    type = Column(String(50), nullable=False)  # masjid, organization, school, business, other

    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color

    # Location
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    address = Column(Text)

    # Contact & Social
    website_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    social_links = Column(JSON)  # {facebook, instagram, twitter, youtube, tiktok}

    # About
    description = Column(Text)
    mission_statement = Column(Text)

    # Subscription & Billing
    plan = Column(String(20), nullable=False, default="basic")  # basic, pro, enterprise
    subscription_status = Column(String(20), default="active")  # active, suspended, cancelled
    subscription_started = Column(DateTime, default=datetime.utcnow)
    subscription_expires = Column(DateTime)

    # Settings
    settings = Column(JSON, default={})  # Organization-specific settings

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    dua_generations = relationship("DuaGeneration", back_populates="organization")
    story_generations = relationship("StoryGeneration", back_populates="organization")
    saved_grants = relationship("SavedGrant", back_populates="organization")
    marketplace_listings = relationship("MarketplaceListing", back_populates="organization")
    social_posts = relationship("SocialPost", back_populates="organization")
```

#### 2. User Model (Updated)
```python
class User(Base):
    __tablename__ = "users"

    # Primary
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100))
    full_name = Column(String(255))

    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Multi-tenant & Roles
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=True)
    role = Column(String(20), nullable=False)  # super_admin, org_admin, org_user

    # Profile
    avatar_url = Column(String(500))
    phone = Column(String(50))

    # Preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")

    # Activity
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
```

### Feature-Specific Models

#### 3. Du'a & Dhikr Studio
```python
class DuaGeneration(Base):
    __tablename__ = "dua_generations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Request params
    topic = Column(String(255))
    situation = Column(String(500))
    language = Column(String(10), default="en")
    level = Column(String(20))  # kids, adults

    # Generated content
    arabic_text = Column(Text)
    transliteration = Column(Text)
    translation = Column(Text)
    explanation = Column(Text)
    source_reference = Column(String(500))

    # Metadata
    is_saved = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="dua_generations")
```

#### 4. Kids Story Studio
```python
class StoryGeneration(Base):
    __tablename__ = "story_generations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Request params
    age_range = Column(String(20))  # 3-5, 6-8, 9-12
    theme = Column(String(100))  # kindness, salah, honesty, etc.
    style = Column(String(20))  # short, medium
    language = Column(String(10), default="en")

    # Generated content
    title = Column(String(500))
    content = Column(Text)
    moral_lesson = Column(Text)
    discussion_questions = Column(JSON)
    related_verses = Column(JSON)

    # Metadata
    is_saved = Column(Boolean, default=False)
    read_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="story_generations")
```

#### 5. Grant Finder Module
```python
class Grant(Base):
    __tablename__ = "grants"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # Basic Info
    title = Column(String(500), nullable=False)
    funder_name = Column(String(255), nullable=False)

    # Location
    country = Column(String(100))
    region = Column(String(100))  # US, EU, global, etc.

    # Categorization
    type = Column(String(50))  # masjid, nonprofit, education, youth, immigrant, general
    categories = Column(ARRAY(String))  # Multiple categories

    # Amounts
    amount_min = Column(Integer)
    amount_max = Column(Integer)
    currency = Column(String(3), default="USD")

    # Dates
    deadline = Column(DateTime)
    opens_at = Column(DateTime)

    # Content
    link_url = Column(String(500))
    summary = Column(Text)
    requirements = Column(Text)
    eligibility = Column(Text)

    # Metadata
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedGrant(Base):
    __tablename__ = "saved_grants"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    grant_id = Column(UUID, ForeignKey("grants.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Tracking
    status = Column(String(20), default="interested")
    # interested, researching, drafting, submitted, awarded, rejected

    notes = Column(Text)
    ai_summary = Column(Text)  # AI-generated summary
    ai_draft_response = Column(Text)  # AI-generated draft

    # Dates
    submitted_date = Column(Date)
    decision_date = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="saved_grants")
    grant = relationship("Grant")
```

#### 6. Marketplace Module
```python
class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)

    # Basic Info
    title = Column(String(500), nullable=False)
    category = Column(String(50))  # business, service, course, event, product, tool

    # Content
    short_description = Column(String(500))
    long_description = Column(Text)

    # Media
    images = Column(JSON)  # Array of image URLs
    video_url = Column(String(500))

    # Links
    website_url = Column(String(500))
    contact_email = Column(String(255))
    phone = Column(String(50))

    # Pricing (optional)
    price_min = Column(Float)
    price_max = Column(Float)
    pricing_note = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Moderation
    rejection_reason = Column(Text)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID, ForeignKey("users.id"))

    # Stats
    view_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="marketplace_listings")
```

#### 7. Learning Hub Module
```python
class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # Basic Info
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True)

    # Categorization
    category = Column(String(50))  # Quran, Seerah, Fiqh, Kids, Parents, New Muslims
    level = Column(String(20))  # beginner, intermediate, advanced
    language = Column(String(10), default="en")

    # Content
    short_description = Column(String(500))
    long_description = Column(Text)
    learning_objectives = Column(JSON)  # Array of objectives

    # Media
    thumbnail_url = Column(String(500))
    preview_video_url = Column(String(500))

    # Authorship
    created_by_org_id = Column(UUID, ForeignKey("organizations.id"))
    instructor_name = Column(String(255))
    instructor_bio = Column(Text)

    # Metadata
    duration_minutes = Column(Integer)
    lesson_count = Column(Integer, default=0)

    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lessons = relationship("Lesson", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False)

    # Basic Info
    title = Column(String(500), nullable=False)
    order_index = Column(Integer, nullable=False)

    # Content
    content_type = Column(String(20))  # text, video, audio
    content_text = Column(Text)
    content_url = Column(String(500))

    # Metadata
    duration_minutes = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Progress
    completed_lessons = Column(JSON, default=[])  # Array of lesson IDs
    progress_percentage = Column(Integer, default=0)

    # Status
    status = Column(String(20), default="in_progress")  # in_progress, completed, dropped

    # Dates
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime)

    # Relationships
    course = relationship("Course", back_populates="enrollments")
```

#### 8. Social Media Studio Module
```python
class SocialProfile(Base):
    __tablename__ = "social_profiles"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)

    # Audience
    main_audience = Column(String(100))  # local community, youth, parents, converts

    # Platforms
    platforms = Column(JSON)  # {facebook: true, instagram: true, tiktok: false, ...}

    # Preferences
    preferred_languages = Column(ARRAY(String))
    tone = Column(String(20))  # formal, warm, youthful, simple

    # Guidelines
    custom_hashtags = Column(ARRAY(String))
    topics_to_avoid = Column(ARRAY(String))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Template & Input
    template_type = Column(String(50))
    # event_reminder, jumuah_reminder, daily_dua, hadith_reflection, quran_reflection,
    # fundraising, volunteer_call, announcement

    input_description = Column(Text)

    # Generated Content
    caption_short = Column(Text)
    caption_long = Column(Text)
    hashtags = Column(ARRAY(String))
    image_prompt = Column(Text)  # For future image AI integration

    # Metadata
    is_saved = Column(Boolean, default=False)
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="social_posts")
```

#### 9. Usage Tracking (Enhanced)
```python
class FeatureUsage(Base):
    __tablename__ = "feature_usage"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Feature tracking
    feature_name = Column(String(50))  # dua_studio, story_studio, grant_finder, etc.
    action = Column(String(50))  # generate, save, search, etc.

    # Metadata
    request_data = Column(JSON)
    response_summary = Column(JSON)

    # AI costs (optional)
    tokens_used = Column(Integer)
    estimated_cost = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔐 Authentication & Authorization

### Authentication Flow
1. User logs in with email/password
2. Backend validates credentials
3. JWT token generated with: `user_id`, `organization_id`, `role`
4. Frontend stores token in httpOnly cookie
5. All API requests include JWT in Authorization header

### Authorization Levels

#### Super Admin (`super_admin`)
- Can create, edit, deactivate organizations
- Can view all organizations and their data
- Can assign/change plans
- Can view global analytics
- Can approve marketplace listings
- Can create/manage courses (global)
- **organization_id:** `null`

#### Organization Admin (`org_admin`)
- Full access to their organization's data
- Can invite/manage staff users
- Can edit organization profile
- Can use all tools available in their plan
- Can view org-specific analytics
- **organization_id:** Set to their organization

#### Organization User (`org_user`)
- Can use tools available in their plan
- Cannot manage organization settings
- Cannot invite users
- Limited to viewing own generated content
- **organization_id:** Set to their organization

### Middleware & Decorators

```python
# Dependency for getting current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode JWT, verify, return user object
    pass

# Dependency for requiring specific role
def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Dependency for getting current organization
async def get_current_organization(current_user: User = Depends(get_current_user)):
    if current_user.role == "super_admin":
        # Super admin needs to specify org_id in request
        pass
    else:
        return current_user.organization
```

### Data Isolation

All queries must be scoped to organization:

```python
# Example: Get all dua generations for current org
@router.get("/duas")
async def get_duas(
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization)
):
    duas = db.query(DuaGeneration).filter(
        DuaGeneration.organization_id == current_org.id
    ).all()
    return duas
```

---

## 📦 Plan-Based Feature Access

### Plan Tiers

#### Basic Plan
**Price:** Free or $9/month
**Features:**
- Du'a & Dhikr Studio (10 generations/month)
- Kids Story Studio (5 stories/month)
- Grant Finder (view only, no AI helpers)
- Learning Hub (view free courses)

#### Pro Plan
**Price:** $29/month
**Features:**
- Du'a & Dhikr Studio (100 generations/month)
- Kids Story Studio (50 stories/month)
- Umrah & Hajj Alerts (full access)
- Grant Finder (unlimited, AI summary & draft)
- Social Media Studio (50 posts/month)
- Learning Hub (all courses)
- Marketplace (1 listing)

#### Enterprise Plan
**Price:** $99/month
**Features:**
- All Pro features
- Unlimited generations across all tools
- Priority support
- Custom branding
- Advanced analytics
- API access
- Marketplace (unlimited listings)
- Featured marketplace placement

### Implementation

```python
# Helper function
def can_use_feature(organization: Organization, feature: str) -> bool:
    """Check if organization's plan allows feature"""

    PLAN_FEATURES = {
        "basic": {
            "dua_studio": {"enabled": True, "limit": 10},
            "story_studio": {"enabled": True, "limit": 5},
            "grant_finder": {"enabled": True, "ai_helpers": False},
            "social_studio": {"enabled": False},
            "marketplace": {"enabled": False},
        },
        "pro": {
            "dua_studio": {"enabled": True, "limit": 100},
            "story_studio": {"enabled": True, "limit": 50},
            "grant_finder": {"enabled": True, "ai_helpers": True},
            "social_studio": {"enabled": True, "limit": 50},
            "marketplace": {"enabled": True, "limit": 1},
            "learning_hub": {"enabled": True, "all_courses": True},
        },
        "enterprise": {
            # All features unlimited
            "dua_studio": {"enabled": True, "limit": -1},  # -1 = unlimited
            "story_studio": {"enabled": True, "limit": -1},
            "grant_finder": {"enabled": True, "ai_helpers": True},
            "social_studio": {"enabled": True, "limit": -1},
            "marketplace": {"enabled": True, "limit": -1, "featured": True},
            "learning_hub": {"enabled": True, "all_courses": True},
        }
    }

    plan_config = PLAN_FEATURES.get(organization.plan, PLAN_FEATURES["basic"])
    feature_config = plan_config.get(feature, {"enabled": False})

    return feature_config.get("enabled", False)


# Usage in endpoints
@router.post("/duas/generate")
async def generate_dua(
    request: DuaRequest,
    current_org: Organization = Depends(get_current_organization)
):
    # Check feature access
    if not can_use_feature(current_org, "dua_studio"):
        raise HTTPException(
            status_code=403,
            detail="Upgrade to access Du'a Studio"
        )

    # Check usage limits
    # ... implement limit checking logic

    # Proceed with generation
    ...
```

---

## 🎨 Frontend Architecture

### Layout Structure

```
/dashboard (Protected, requires auth)
├── /dashboard (Overview - org stats, recent activity)
├── /dashboard/dua-studio
├── /dashboard/story-studio
├── /dashboard/umrah-alerts
├── /dashboard/grant-finder
│   ├── /dashboard/grant-finder/search
│   ├── /dashboard/grant-finder/saved
│   └── /dashboard/grant-finder/[grantId]
├── /dashboard/marketplace
│   ├── /dashboard/marketplace/browse
│   ├── /dashboard/marketplace/my-listings
│   └── /dashboard/marketplace/new
├── /dashboard/learning-hub
│   ├── /dashboard/learning-hub/courses
│   ├── /dashboard/learning-hub/my-courses
│   └── /dashboard/learning-hub/[courseId]
├── /dashboard/social-studio
│   ├── /dashboard/social-studio/generate
│   └── /dashboard/social-studio/library
└── /dashboard/settings
    ├── /dashboard/settings/organization
    ├── /dashboard/settings/team
    ├── /dashboard/settings/billing
    └── /dashboard/settings/profile

/admin (Super admin only)
├── /admin/organizations
├── /admin/organizations/[orgId]
├── /admin/analytics
├── /admin/grants (Manage grants)
├── /admin/marketplace (Approve listings)
└── /admin/courses (Manage courses)

/ (Public)
├── / (Landing page)
├── /login
├── /register
├── /pricing
├── /about
└── /contact
```

### Navigation Component

```tsx
// components/DashboardLayout.tsx
const navigation = [
  { name: 'Dashboard', icon: HomeIcon, href: '/dashboard' },
  { name: 'Du'a Studio', icon: HeartIcon, href: '/dashboard/dua-studio' },
  { name: 'Story Studio', icon: BookOpenIcon, href: '/dashboard/story-studio' },
  { name: 'Umrah Alerts', icon: MapPinIcon, href: '/dashboard/umrah-alerts' },
  { name: 'Grant Finder', icon: CurrencyDollarIcon, href: '/dashboard/grant-finder' },
  { name: 'Marketplace', icon: ShoppingBagIcon, href: '/dashboard/marketplace' },
  { name: 'Learning Hub', icon: AcademicCapIcon, href: '/dashboard/learning-hub' },
  { name: 'Social Studio', icon: ShareIcon, href: '/dashboard/social-studio' },
]
```

### Context Providers

```tsx
// providers/AuthProvider.tsx
interface AuthContext {
  user: User | null
  organization: Organization | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  canUseFeature: (feature: string) => boolean
}

// providers/OrganizationProvider.tsx
interface OrganizationContext {
  organization: Organization
  updateOrganization: (data: Partial<Organization>) => Promise<void>
  members: User[]
  inviteMember: (email: string, role: string) => Promise<void>
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Rename branding: MadinaGPT → Global Waqaf Tech
- [ ] Create new database models (Organization, updated User)
- [ ] Implement JWT auth with role support
- [ ] Build organization management endpoints
- [ ] Create user management endpoints (invite, roles)
- [ ] Build basic dashboard layout

### Phase 2: Refactor Existing Features (Week 2)
- [ ] Add organization_id to Du'a API
- [ ] Add organization_id to Story API
- [ ] Add organization_id to Umrah API
- [ ] Store generations in database (not just in-memory)
- [ ] Add usage tracking for all existing features
- [ ] Update frontend to use authenticated APIs

### Phase 3: Grant Finder (Week 3)
- [ ] Create Grant & SavedGrant models
- [ ] Build Grant CRUD endpoints (admin)
- [ ] Build Grant search/filter endpoints
- [ ] Build SavedGrant tracker endpoints
- [ ] Implement AI summary & draft generation
- [ ] Build Grant Finder UI

### Phase 4: Marketplace (Week 4)
- [ ] Create MarketplaceListing model
- [ ] Build listing CRUD endpoints
- [ ] Build approval workflow (admin)
- [ ] Build browse/search/filter endpoints
- [ ] Build Marketplace UI (browse + manage)
- [ ] Build admin approval interface

### Phase 5: Learning Hub (Week 5)
- [ ] Create Course, Lesson, Enrollment models
- [ ] Build course CRUD endpoints (admin)
- [ ] Build enrollment endpoints
- [ ] Build progress tracking
- [ ] Build Learning Hub UI
- [ ] Build course player

### Phase 6: Social Media Studio (Week 6)
- [ ] Create SocialProfile & SocialPost models
- [ ] Build profile settings endpoints
- [ ] Build AI post generation logic
- [ ] Build content library endpoints
- [ ] Build Social Studio UI
- [ ] Add templates and customization

### Phase 7: Admin Panel (Week 7)
- [ ] Build organization management UI
- [ ] Build user management UI
- [ ] Build analytics dashboards
- [ ] Build grant management UI
- [ ] Build marketplace approval UI
- [ ] Build course management UI

### Phase 8: Polish & Launch (Week 8)
- [ ] Plan enforcement & upgrade flows
- [ ] Usage limit tracking & notifications
- [ ] Email notifications
- [ ] Documentation
- [ ] Testing
- [ ] Deployment

---

## 📁 File Structure

```
madinagpt/  →  global-waqaf-tech/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── auth.py (NEW)
│   │   │       ├── organizations.py (NEW)
│   │   │       ├── users.py (NEW)
│   │   │       ├── duas.py (UPDATED - multi-tenant)
│   │   │       ├── stories.py (UPDATED - multi-tenant)
│   │   │       ├── umrah_deals.py (UPDATED - multi-tenant)
│   │   │       ├── grants.py (NEW)
│   │   │       ├── marketplace.py (NEW)
│   │   │       ├── courses.py (NEW)
│   │   │       ├── social_studio.py (NEW)
│   │   │       └── admin.py (NEW)
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py (NEW - JWT, password hashing)
│   │   │   └── permissions.py (NEW - RBAC helpers)
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py (MAJOR UPDATE)
│   │   │   └── seed_data.py (NEW - initial grants, courses)
│   │   ├── services/
│   │   │   ├── dua_service.py (UPDATED)
│   │   │   ├── story_service.py (UPDATED)
│   │   │   ├── umrah_service.py
│   │   │   ├── grant_service.py (NEW)
│   │   │   ├── marketplace_service.py (NEW)
│   │   │   ├── course_service.py (NEW)
│   │   │   ├── social_service.py (NEW)
│   │   │   └── ai_service.py (NEW - centralized AI calls)
│   │   └── main.py (UPDATE branding)
│   └── requirements.txt (ADD: python-jose, passlib)
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (public)/
│   │   │   │   ├── page.tsx (REBRAND)
│   │   │   │   ├── login/
│   │   │   │   ├── register/
│   │   │   │   ├── pricing/
│   │   │   │   └── about/
│   │   │   ├── dashboard/
│   │   │   │   ├── layout.tsx (NEW - dashboard layout)
│   │   │   │   ├── page.tsx (NEW - org overview)
│   │   │   │   ├── dua-studio/
│   │   │   │   ├── story-studio/
│   │   │   │   ├── umrah-alerts/
│   │   │   │   ├── grant-finder/
│   │   │   │   ├── marketplace/
│   │   │   │   ├── learning-hub/
│   │   │   │   ├── social-studio/
│   │   │   │   └── settings/
│   │   │   └── admin/
│   │   │       ├── organizations/
│   │   │       ├── grants/
│   │   │       ├── marketplace/
│   │   │       └── courses/
│   │   ├── components/
│   │   │   ├── auth/ (NEW)
│   │   │   ├── dashboard/ (NEW)
│   │   │   ├── grants/ (NEW)
│   │   │   ├── marketplace/ (NEW)
│   │   │   ├── learning/ (NEW)
│   │   │   └── social/ (NEW)
│   │   ├── hooks/
│   │   │   ├── useAuth.ts (NEW)
│   │   │   ├── useOrganization.ts (NEW)
│   │   │   └── useFeatureAccess.ts (NEW)
│   │   ├── providers/
│   │   │   ├── AuthProvider.tsx (NEW)
│   │   │   └── OrganizationProvider.tsx (NEW)
│   │   └── services/
│   │       ├── api.ts (UPDATE base URL, auth headers)
│   │       ├── authAPI.ts (NEW)
│   │       ├── organizationAPI.ts (NEW)
│   │       ├── grantAPI.ts (NEW)
│   │       ├── marketplaceAPI.ts (NEW)
│   │       ├── courseAPI.ts (NEW)
│   │       └── socialAPI.ts (NEW)
│   ├── package.json (UPDATE name, description)
│   └── tailwind.config.js (UPDATE colors - madina → waqaf)
│
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   └── USER_GUIDE.md
│
└── GLOBAL_WAQAF_TECH_ARCHITECTURE_PLAN.md (THIS FILE)
```

---

## 🎯 Success Criteria

### Technical
- [ ] Multi-tenancy working correctly (data isolation)
- [ ] All 3 user roles implemented and tested
- [ ] All 7+ features functional
- [ ] Plan-based access control enforced
- [ ] Database migrations successful
- [ ] Frontend rebrandedfrom MadinaGPT to Global Waqaf Tech
- [ ] Authentication & authorization working

### Business
- [ ] Super admin can create and manage organizations
- [ ] Organizations can invite team members
- [ ] Organizations can use all tools in their plan
- [ ] Usage tracking implemented
- [ ] Clear upgrade paths for plans

### User Experience
- [ ] Intuitive dashboard navigation
- [ ] Responsive on mobile/tablet/desktop
- [ ] Fast page loads (<2s)
- [ ] Clear error messages
- [ ] Help documentation available

---

## 📝 Notes for Implementation

1. **Start with database migrations** - Get the schema right first
2. **Build authentication early** - Everything depends on it
3. **Test multi-tenancy thoroughly** - Ensure no data leakage
4. **Implement one feature module at a time** - Don't try to do everything at once
5. **Keep existing features working** - Don't break what already works
6. **Add comprehensive logging** - Track all organization actions
7. **Consider rate limiting** - Prevent abuse
8. **Plan for scaling** - Use caching (Redis) for frequently accessed data

---

## 🔮 Future Enhancements (Post-Launch)

- Payment integration (Stripe/PayPal)
- Automated email campaigns
- Mobile app (React Native)
- Affiliate program management
- Revenue sharing automation
- WhatsApp/SMS notifications for alerts
- Calendar integration
- Advanced analytics & reporting
- Public API for developers
- Webhooks for integrations

---

**End of Architecture Plan**

*This document serves as the blueprint for transforming Madina GPT into Global Waqaf Tech. It should be reviewed and updated as implementation progresses.*
