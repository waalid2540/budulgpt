"""
Learning Hub API Endpoints - Multi-tenant Islamic Learning Platform
Educational platform for Islamic courses, lessons, and progress tracking.

Plan-based access:
- Basic: Access to free courses only
- Pro: Access to all courses (free + paid)
- Enterprise: All courses + create own courses

Routes:
- GET /api/v1/learning - Browse course catalog
- GET /api/v1/learning/search - Search courses
- GET /api/v1/learning/{course_id} - Get course details
- GET /api/v1/learning/{course_id}/lessons - Get course lessons
- GET /api/v1/learning/{course_id}/lessons/{lesson_id} - Get lesson content
- POST /api/v1/learning/{course_id}/enroll - Enroll in course
- DELETE /api/v1/learning/{course_id}/unenroll - Unenroll from course
- GET /api/v1/learning/my-enrollments - My enrolled courses
- POST /api/v1/learning/lessons/{lesson_id}/complete - Mark lesson complete
- GET /api/v1/learning/my-progress/{course_id} - Get my progress

Course Creation (Enterprise only):
- POST /api/v1/learning/courses - Create course
- PATCH /api/v1/learning/courses/{course_id} - Update course
- DELETE /api/v1/learning/courses/{course_id} - Delete course
- POST /api/v1/learning/courses/{course_id}/lessons - Add lesson
- PATCH /api/v1/learning/courses/{course_id}/lessons/{lesson_id} - Update lesson
- DELETE /api/v1/learning/courses/{course_id}/lessons/{lesson_id} - Delete lesson
- GET /api/v1/learning/courses/my-courses - My created courses
- GET /api/v1/learning/courses/{course_id}/analytics - Course analytics

Admin Routes:
- GET /api/v1/learning/admin/courses - List all courses (super admin)
- PATCH /api/v1/learning/admin/courses/{course_id}/feature - Feature course (super admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models_multitenant import (
    Course,
    Lesson,
    Enrollment,
    Organization,
    User,
    FeatureUsage
)
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_current_organization,
    require_roles,
    require_feature
)
from app.core.permissions import UserRole
from pydantic import BaseModel, Field, validator

router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class CourseCreateRequest(BaseModel):
    """Request body for creating a course"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    instructor_name: str = Field(..., max_length=100)
    category: str = Field(..., description="aqeedah, fiqh, seerah, quran, hadith, arabic, general")
    level: str = Field(..., description="beginner, intermediate, advanced")

    # Pricing
    is_free: bool = Field(default=True)
    price: Optional[float] = Field(None, ge=0)

    # Media
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    preview_video_url: Optional[str] = Field(None, max_length=500)

    # Additional
    duration_hours: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = Field(default_factory=list)

    @validator('category')
    def validate_category(cls, v):
        allowed = ['aqeedah', 'fiqh', 'seerah', 'quran', 'hadith', 'arabic', 'general']
        if v.lower() not in allowed:
            raise ValueError(f'Category must be one of: {", ".join(allowed)}')
        return v.lower()

    @validator('level')
    def validate_level(cls, v):
        allowed = ['beginner', 'intermediate', 'advanced']
        if v.lower() not in allowed:
            raise ValueError(f'Level must be one of: {", ".join(allowed)}')
        return v.lower()


class CourseUpdateRequest(BaseModel):
    """Request body for updating a course"""
    title: Optional[str] = None
    description: Optional[str] = None
    instructor_name: Optional[str] = None
    is_free: Optional[bool] = None
    price: Optional[float] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    duration_hours: Optional[float] = None
    tags: Optional[List[str]] = None


class LessonCreateRequest(BaseModel):
    """Request body for creating a lesson"""
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10, description="Lesson content in markdown")
    video_url: Optional[str] = Field(None, max_length=500)
    order_number: int = Field(..., ge=1, description="Order in course (1, 2, 3...)")
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_free_preview: bool = Field(default=False, description="Can be viewed without enrollment")


class LessonUpdateRequest(BaseModel):
    """Request body for updating a lesson"""
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    order_number: Optional[int] = None
    duration_minutes: Optional[int] = None
    is_free_preview: Optional[bool] = None


class CourseResponse(BaseModel):
    """Response model for course"""
    id: uuid.UUID
    title: str
    description: str
    instructor_name: str
    category: str
    level: str

    is_free: bool
    price: Optional[float]

    thumbnail_url: Optional[str]
    preview_video_url: Optional[str]
    duration_hours: Optional[float]
    tags: List[str]

    # Creator info
    created_by_organization_id: Optional[uuid.UUID]
    created_by_organization_name: Optional[str]

    # Stats
    total_lessons: int
    total_enrollments: int
    is_featured: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    """Response model for lesson"""
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    content: str
    video_url: Optional[str]
    order_number: int
    duration_minutes: Optional[int]
    is_free_preview: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentResponse(BaseModel):
    """Response model for enrollment"""
    id: uuid.UUID
    course_id: uuid.UUID
    course_title: str
    course_instructor: str
    course_thumbnail: Optional[str]

    progress_percentage: float
    completed_lessons: int
    total_lessons: int
    is_completed: bool

    enrolled_at: datetime
    last_accessed_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class CourseAnalyticsResponse(BaseModel):
    """Analytics for course creator"""
    total_enrollments: int
    active_students: int
    completed_students: int
    average_progress: float
    total_lesson_completions: int
    enrollments_by_month: dict


# ============================================================================
# PUBLIC ROUTES (Browse Catalog)
# ============================================================================

@router.get("/", response_model=List[CourseResponse])
async def browse_courses(
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    free_only: bool = Query(False, description="Show only free courses"),
    featured_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Browse all available courses.
    Featured courses appear first.
    """
    query = db.query(
        Course,
        Organization.name.label("org_name")
    ).outerjoin(
        Organization,
        Course.created_by_organization_id == Organization.id
    )

    # Apply filters
    if category:
        query = query.filter(Course.category == category.lower())
    if level:
        query = query.filter(Course.level == level.lower())
    if free_only:
        query = query.filter(Course.is_free == True)
    if featured_only:
        query = query.filter(Course.is_featured == True)

    # Order: Featured first, then newest
    query = query.order_by(
        Course.is_featured.desc(),
        Course.created_at.desc()
    )

    results = query.offset(skip).limit(limit).all()

    return [
        CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            instructor_name=course.instructor_name,
            category=course.category,
            level=course.level,
            is_free=course.is_free,
            price=course.price,
            thumbnail_url=course.thumbnail_url,
            preview_video_url=course.preview_video_url,
            duration_hours=course.duration_hours,
            tags=course.tags or [],
            created_by_organization_id=course.created_by_organization_id,
            created_by_organization_name=org_name if org_name else None,
            total_lessons=course.total_lessons,
            total_enrollments=course.total_enrollments,
            is_featured=course.is_featured,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        for course, org_name in results
    ]


@router.get("/search", response_model=List[CourseResponse])
async def search_courses(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search courses by keyword.
    Searches in title, description, instructor name, and tags.
    """
    search_term = f"%{q}%"

    query = db.query(
        Course,
        Organization.name.label("org_name")
    ).outerjoin(
        Organization,
        Course.created_by_organization_id == Organization.id
    ).filter(
        or_(
            Course.title.ilike(search_term),
            Course.description.ilike(search_term),
            Course.instructor_name.ilike(search_term),
            Course.tags.contains([q])
        )
    )

    results = query.offset(skip).limit(limit).all()

    return [
        CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            instructor_name=course.instructor_name,
            category=course.category,
            level=course.level,
            is_free=course.is_free,
            price=course.price,
            thumbnail_url=course.thumbnail_url,
            preview_video_url=course.preview_video_url,
            duration_hours=course.duration_hours,
            tags=course.tags or [],
            created_by_organization_id=course.created_by_organization_id,
            created_by_organization_name=org_name if org_name else None,
            total_lessons=course.total_lessons,
            total_enrollments=course.total_enrollments,
            is_featured=course.is_featured,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        for course, org_name in results
    ]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_details(
    course_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific course.
    """
    result = db.query(
        Course,
        Organization.name.label("org_name")
    ).outerjoin(
        Organization,
        Course.created_by_organization_id == Organization.id
    ).filter(
        Course.id == course_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Course not found")

    course, org_name = result

    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        instructor_name=course.instructor_name,
        category=course.category,
        level=course.level,
        is_free=course.is_free,
        price=course.price,
        thumbnail_url=course.thumbnail_url,
        preview_video_url=course.preview_video_url,
        duration_hours=course.duration_hours,
        tags=course.tags or [],
        created_by_organization_id=course.created_by_organization_id,
        created_by_organization_name=org_name if org_name else None,
        total_lessons=course.total_lessons,
        total_enrollments=course.total_enrollments,
        is_featured=course.is_featured,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
async def get_course_lessons(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all lessons for a course.
    Returns full content only for enrolled users or free preview lessons.
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is enrolled
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.user_id == current_user.id
        )
    ).first()

    # Get lessons
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id
    ).order_by(Lesson.order_number).all()

    # If not enrolled, only show free preview lessons
    if not enrollment:
        lessons = [l for l in lessons if l.is_free_preview]

    return [
        LessonResponse(
            id=lesson.id,
            course_id=lesson.course_id,
            title=lesson.title,
            content=lesson.content if enrollment or lesson.is_free_preview else "Enroll to access this lesson",
            video_url=lesson.video_url if enrollment or lesson.is_free_preview else None,
            order_number=lesson.order_number,
            duration_minutes=lesson.duration_minutes,
            is_free_preview=lesson.is_free_preview,
            created_at=lesson.created_at
        )
        for lesson in lessons
    ]


@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson_content(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get full lesson content.
    Requires enrollment unless it's a free preview lesson.
    """
    lesson = db.query(Lesson).filter(
        and_(
            Lesson.id == lesson_id,
            Lesson.course_id == course_id
        )
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check enrollment
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.user_id == current_user.id
        )
    ).first()

    if not enrollment and not lesson.is_free_preview:
        raise HTTPException(
            status_code=403,
            detail="You must be enrolled in this course to access this lesson"
        )

    # Update last accessed
    if enrollment:
        enrollment.last_accessed_at = datetime.utcnow()
        db.commit()

    return LessonResponse(
        id=lesson.id,
        course_id=lesson.course_id,
        title=lesson.title,
        content=lesson.content,
        video_url=lesson.video_url,
        order_number=lesson.order_number,
        duration_minutes=lesson.duration_minutes,
        is_free_preview=lesson.is_free_preview,
        created_at=lesson.created_at
    )


# ============================================================================
# ENROLLMENT & PROGRESS ROUTES
# ============================================================================

@router.post("/{course_id}/enroll", response_model=EnrollmentResponse, status_code=201)
async def enroll_in_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("learning_hub")),
    db: Session = Depends(get_db)
):
    """
    Enroll in a course.

    Plan access:
    - Basic: Free courses only
    - Pro/Enterprise: All courses
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.user_id == current_user.id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")

    # Check plan access for paid courses
    if not course.is_free and organization.plan == "basic":
        raise HTTPException(
            status_code=403,
            detail="Basic plan only allows free courses. Upgrade to Pro or Enterprise for paid courses."
        )

    # Create enrollment
    enrollment = Enrollment(
        id=uuid.uuid4(),
        user_id=current_user.id,
        course_id=course_id,
        organization_id=organization.id,
        progress_percentage=0.0,
        completed_lessons=0,
        is_completed=False
    )

    db.add(enrollment)

    # Update course enrollment count
    course.total_enrollments += 1

    db.commit()
    db.refresh(enrollment)

    # Track usage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="learning_hub",
        usage_type="course_enrolled",
        metadata={"course_id": str(course_id), "course_title": course.title}
    )
    db.add(usage)
    db.commit()

    return EnrollmentResponse(
        id=enrollment.id,
        course_id=course.id,
        course_title=course.title,
        course_instructor=course.instructor_name,
        course_thumbnail=course.thumbnail_url,
        progress_percentage=enrollment.progress_percentage,
        completed_lessons=enrollment.completed_lessons,
        total_lessons=course.total_lessons,
        is_completed=enrollment.is_completed,
        enrolled_at=enrollment.enrolled_at,
        last_accessed_at=enrollment.last_accessed_at,
        completed_at=enrollment.completed_at
    )


@router.delete("/{course_id}/unenroll", status_code=204)
async def unenroll_from_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Unenroll from a course.
    """
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.user_id == current_user.id
        )
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")

    # Update course enrollment count
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        course.total_enrollments = max(0, course.total_enrollments - 1)

    db.delete(enrollment)
    db.commit()

    return None


@router.get("/my-enrollments", response_model=List[EnrollmentResponse])
async def get_my_enrollments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all courses I'm enrolled in.
    """
    results = db.query(
        Enrollment,
        Course
    ).join(
        Course,
        Enrollment.course_id == Course.id
    ).filter(
        Enrollment.user_id == current_user.id
    ).order_by(
        Enrollment.last_accessed_at.desc().nullsfirst(),
        Enrollment.enrolled_at.desc()
    ).all()

    return [
        EnrollmentResponse(
            id=enrollment.id,
            course_id=course.id,
            course_title=course.title,
            course_instructor=course.instructor_name,
            course_thumbnail=course.thumbnail_url,
            progress_percentage=enrollment.progress_percentage,
            completed_lessons=enrollment.completed_lessons,
            total_lessons=course.total_lessons,
            is_completed=enrollment.is_completed,
            enrolled_at=enrollment.enrolled_at,
            last_accessed_at=enrollment.last_accessed_at,
            completed_at=enrollment.completed_at
        )
        for enrollment, course in results
    ]


@router.post("/lessons/{lesson_id}/complete")
async def mark_lesson_complete(
    lesson_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a lesson as completed.
    Updates progress percentage automatically.
    """
    # Get lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get enrollment
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == lesson.course_id,
            Enrollment.user_id == current_user.id
        )
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    # Get total lessons in course
    total_lessons = db.query(func.count(Lesson.id)).filter(
        Lesson.course_id == lesson.course_id
    ).scalar()

    # Update enrollment
    enrollment.completed_lessons += 1
    enrollment.progress_percentage = (enrollment.completed_lessons / total_lessons) * 100
    enrollment.last_accessed_at = datetime.utcnow()

    # Check if course completed
    if enrollment.completed_lessons >= total_lessons:
        enrollment.is_completed = True
        enrollment.completed_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "progress_percentage": enrollment.progress_percentage,
        "completed_lessons": enrollment.completed_lessons,
        "total_lessons": total_lessons,
        "is_completed": enrollment.is_completed
    }


@router.get("/my-progress/{course_id}")
async def get_my_progress(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress for a specific course.
    """
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.user_id == current_user.id
        )
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")

    course = db.query(Course).filter(Course.id == course_id).first()

    return {
        "course_id": course_id,
        "course_title": course.title if course else None,
        "progress_percentage": enrollment.progress_percentage,
        "completed_lessons": enrollment.completed_lessons,
        "total_lessons": course.total_lessons if course else 0,
        "is_completed": enrollment.is_completed,
        "enrolled_at": enrollment.enrolled_at,
        "last_accessed_at": enrollment.last_accessed_at,
        "completed_at": enrollment.completed_at
    }


# ============================================================================
# COURSE CREATION ROUTES (Enterprise Only)
# ============================================================================

@router.post("/courses", response_model=CourseResponse, status_code=201)
async def create_course(
    request: CourseCreateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(require_feature("learning_hub", "create_courses")),
    db: Session = Depends(get_db)
):
    """
    Create a new course (Enterprise plan only).
    """
    new_course = Course(
        id=uuid.uuid4(),
        title=request.title,
        description=request.description,
        instructor_name=request.instructor_name,
        category=request.category,
        level=request.level,
        is_free=request.is_free,
        price=request.price,
        thumbnail_url=request.thumbnail_url,
        preview_video_url=request.preview_video_url,
        duration_hours=request.duration_hours,
        tags=request.tags,
        created_by_organization_id=organization.id,
        total_lessons=0,
        total_enrollments=0,
        is_featured=False
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # Track usage
    usage = FeatureUsage(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=current_user.id,
        feature_name="learning_hub",
        usage_type="course_created",
        metadata={"course_id": str(new_course.id), "title": new_course.title}
    )
    db.add(usage)
    db.commit()

    return CourseResponse(
        id=new_course.id,
        title=new_course.title,
        description=new_course.description,
        instructor_name=new_course.instructor_name,
        category=new_course.category,
        level=new_course.level,
        is_free=new_course.is_free,
        price=new_course.price,
        thumbnail_url=new_course.thumbnail_url,
        preview_video_url=new_course.preview_video_url,
        duration_hours=new_course.duration_hours,
        tags=new_course.tags or [],
        created_by_organization_id=new_course.created_by_organization_id,
        created_by_organization_name=organization.name,
        total_lessons=new_course.total_lessons,
        total_enrollments=new_course.total_enrollments,
        is_featured=new_course.is_featured,
        created_at=new_course.created_at,
        updated_at=new_course.updated_at
    )


@router.get("/courses/my-courses", response_model=List[CourseResponse])
async def get_my_created_courses(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get all courses created by my organization.
    """
    courses = db.query(Course).filter(
        Course.created_by_organization_id == organization.id
    ).order_by(Course.created_at.desc()).all()

    return [
        CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            instructor_name=course.instructor_name,
            category=course.category,
            level=course.level,
            is_free=course.is_free,
            price=course.price,
            thumbnail_url=course.thumbnail_url,
            preview_video_url=course.preview_video_url,
            duration_hours=course.duration_hours,
            tags=course.tags or [],
            created_by_organization_id=course.created_by_organization_id,
            created_by_organization_name=organization.name,
            total_lessons=course.total_lessons,
            total_enrollments=course.total_enrollments,
            is_featured=course.is_featured,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        for course in courses
    ]


@router.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: uuid.UUID,
    request: CourseUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update my organization's course.
    """
    course = db.query(Course).filter(
        and_(
            Course.id == course_id,
            Course.created_by_organization_id == organization.id
        )
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    course.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(course)

    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        instructor_name=course.instructor_name,
        category=course.category,
        level=course.level,
        is_free=course.is_free,
        price=course.price,
        thumbnail_url=course.thumbnail_url,
        preview_video_url=course.preview_video_url,
        duration_hours=course.duration_hours,
        tags=course.tags or [],
        created_by_organization_id=course.created_by_organization_id,
        created_by_organization_name=organization.name,
        total_lessons=course.total_lessons,
        total_enrollments=course.total_enrollments,
        is_featured=course.is_featured,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.delete("/courses/{course_id}", status_code=204)
async def delete_course(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete my organization's course.
    Also deletes all lessons and enrollments.
    """
    course = db.query(Course).filter(
        and_(
            Course.id == course_id,
            Course.created_by_organization_id == organization.id
        )
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Delete lessons
    db.query(Lesson).filter(Lesson.course_id == course_id).delete()

    # Delete enrollments
    db.query(Enrollment).filter(Enrollment.course_id == course_id).delete()

    # Delete course
    db.delete(course)
    db.commit()

    return None


@router.post("/courses/{course_id}/lessons", response_model=LessonResponse, status_code=201)
async def add_lesson_to_course(
    course_id: uuid.UUID,
    request: LessonCreateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Add a lesson to my organization's course.
    """
    # Verify course ownership
    course = db.query(Course).filter(
        and_(
            Course.id == course_id,
            Course.created_by_organization_id == organization.id
        )
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Create lesson
    new_lesson = Lesson(
        id=uuid.uuid4(),
        course_id=course_id,
        title=request.title,
        content=request.content,
        video_url=request.video_url,
        order_number=request.order_number,
        duration_minutes=request.duration_minutes,
        is_free_preview=request.is_free_preview
    )

    db.add(new_lesson)

    # Update course lesson count
    course.total_lessons += 1

    db.commit()
    db.refresh(new_lesson)

    return LessonResponse(
        id=new_lesson.id,
        course_id=new_lesson.course_id,
        title=new_lesson.title,
        content=new_lesson.content,
        video_url=new_lesson.video_url,
        order_number=new_lesson.order_number,
        duration_minutes=new_lesson.duration_minutes,
        is_free_preview=new_lesson.is_free_preview,
        created_at=new_lesson.created_at
    )


@router.patch("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    request: LessonUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Update a lesson in my organization's course.
    """
    # Verify course ownership
    course = db.query(Course).filter(
        and_(
            Course.id == course_id,
            Course.created_by_organization_id == organization.id
        )
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get lesson
    lesson = db.query(Lesson).filter(
        and_(
            Lesson.id == lesson_id,
            Lesson.course_id == course_id
        )
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)

    return LessonResponse(
        id=lesson.id,
        course_id=lesson.course_id,
        title=lesson.title,
        content=lesson.content,
        video_url=lesson.video_url,
        order_number=lesson.order_number,
        duration_minutes=lesson.duration_minutes,
        is_free_preview=lesson.is_free_preview,
        created_at=lesson.created_at
    )


@router.delete("/courses/{course_id}/lessons/{lesson_id}", status_code=204)
async def delete_lesson(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a lesson from my organization's course.
    """
    # Verify course ownership
    course = db.query(Course).filter(
        and_(
            Course.id == course_id,
            Course.created_by_organization_id == organization.id
        )
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get lesson
    lesson = db.query(Lesson).filter(
        and_(
            Lesson.id == lesson_id,
            Lesson.course_id == course_id
        )
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(lesson)

    # Update course lesson count
    course.total_lessons = max(0, course.total_lessons - 1)

    db.commit()

    return None


@router.get("/courses/{course_id}/analytics", response_model=CourseAnalyticsResponse)
async def get_course_analytics(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Get analytics for my organization's course (Enterprise only).
    """
    # Verify course ownership
    course = db.query(Course).filter(
        and_(
            Course.id == course_id,
            Course.created_by_organization_id == organization.id
        )
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Total enrollments
    total_enrollments = db.query(func.count(Enrollment.id)).filter(
        Enrollment.course_id == course_id
    ).scalar()

    # Active students (accessed in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_students = db.query(func.count(Enrollment.id)).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.last_accessed_at >= thirty_days_ago
        )
    ).scalar()

    # Completed students
    completed_students = db.query(func.count(Enrollment.id)).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.is_completed == True
        )
    ).scalar()

    # Average progress
    avg_progress = db.query(func.avg(Enrollment.progress_percentage)).filter(
        Enrollment.course_id == course_id
    ).scalar() or 0.0

    # Total lesson completions
    total_completions = db.query(func.sum(Enrollment.completed_lessons)).filter(
        Enrollment.course_id == course_id
    ).scalar() or 0

    return CourseAnalyticsResponse(
        total_enrollments=total_enrollments,
        active_students=active_students,
        completed_students=completed_students,
        average_progress=float(avg_progress),
        total_lesson_completions=total_completions,
        enrollments_by_month={}  # TODO: Implement monthly breakdown
    )


# ============================================================================
# SUPER ADMIN ROUTES
# ============================================================================

@router.get("/admin/courses", response_model=List[CourseResponse])
async def get_all_courses_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Get all courses (super admin only).
    """
    results = db.query(
        Course,
        Organization.name.label("org_name")
    ).outerjoin(
        Organization,
        Course.created_by_organization_id == Organization.id
    ).order_by(Course.created_at.desc()).offset(skip).limit(limit).all()

    return [
        CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            instructor_name=course.instructor_name,
            category=course.category,
            level=course.level,
            is_free=course.is_free,
            price=course.price,
            thumbnail_url=course.thumbnail_url,
            preview_video_url=course.preview_video_url,
            duration_hours=course.duration_hours,
            tags=course.tags or [],
            created_by_organization_id=course.created_by_organization_id,
            created_by_organization_name=org_name if org_name else None,
            total_lessons=course.total_lessons,
            total_enrollments=course.total_enrollments,
            is_featured=course.is_featured,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        for course, org_name in results
    ]


@router.patch("/admin/courses/{course_id}/feature", response_model=CourseResponse)
async def toggle_course_featured(
    course_id: uuid.UUID,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Toggle featured status for a course (super admin only).
    """
    result = db.query(
        Course,
        Organization.name.label("org_name")
    ).outerjoin(
        Organization,
        Course.created_by_organization_id == Organization.id
    ).filter(Course.id == course_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Course not found")

    course, org_name = result

    course.is_featured = not course.is_featured
    course.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(course)

    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        instructor_name=course.instructor_name,
        category=course.category,
        level=course.level,
        is_free=course.is_free,
        price=course.price,
        thumbnail_url=course.thumbnail_url,
        preview_video_url=course.preview_video_url,
        duration_hours=course.duration_hours,
        tags=course.tags or [],
        created_by_organization_id=course.created_by_organization_id,
        created_by_organization_name=org_name if org_name else None,
        total_lessons=course.total_lessons,
        total_enrollments=course.total_enrollments,
        is_featured=course.is_featured,
        created_at=course.created_at,
        updated_at=course.updated_at
    )
