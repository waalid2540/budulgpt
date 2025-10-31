"""
Database schema for Umrah Deal Finder and Alert System
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    phone = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    searches = relationship("SavedSearch", back_populates="user")
    alerts = relationship("Alert", back_populates="user")


class SavedSearch(Base):
    """Saved Umrah deal searches"""
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Search criteria
    destination = Column(String, nullable=False)  # Makkah, Madinah, Both
    budget_min = Column(Float)
    budget_max = Column(Float, nullable=False)
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    duration_nights = Column(Integer)
    hotel_rating = Column(Integer)  # 3, 4, 5 stars
    distance_from_haram = Column(Float)  # in km

    # Alert preferences
    alert_enabled = Column(Boolean, default=True)
    alert_email = Column(Boolean, default=True)
    alert_whatsapp = Column(Boolean, default=False)
    alert_sms = Column(Boolean, default=False)

    # Metadata
    name = Column(String)  # User-given name for this search
    last_checked = Column(DateTime, default=datetime.utcnow)
    best_price_found = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="searches")
    alerts = relationship("Alert", back_populates="search")
    deals = relationship("UmrahDeal", back_populates="search")


class UmrahDeal(Base):
    """Umrah deals found by searches"""
    __tablename__ = "umrah_deals"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("saved_searches.id"))

    # Deal information
    hotel_name = Column(String, nullable=False)
    hotel_rating = Column(Float)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    location = Column(String)
    distance_from_haram = Column(Float)

    # Additional details
    amenities = Column(JSON)  # List of amenities
    room_type = Column(String)
    booking_url = Column(Text)
    provider = Column(String)  # Booking.com, Expedia, etc.

    # Availability
    available_from = Column(DateTime)
    available_to = Column(DateTime)

    # Metadata
    found_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    search = relationship("SavedSearch", back_populates="deals")


class Alert(Base):
    """Alert notifications sent to users"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_id = Column(Integer, ForeignKey("saved_searches.id"))

    # Alert details
    alert_type = Column(String, nullable=False)  # price_drop, new_deal, availability
    message = Column(Text, nullable=False)

    # Notification channels
    sent_email = Column(Boolean, default=False)
    sent_whatsapp = Column(Boolean, default=False)
    sent_sms = Column(Boolean, default=False)

    # Deal information
    deal_data = Column(JSON)  # Snapshot of deal info

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    is_read = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
    search = relationship("SavedSearch", back_populates="alerts")


class SearchLog(Base):
    """Log of all searches performed (for analytics)"""
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Search params
    search_params = Column(JSON, nullable=False)

    # Results
    results_count = Column(Integer)
    results_data = Column(JSON)  # Cache of results

    # Performance
    search_duration_ms = Column(Integer)
    api_used = Column(String)  # perplexity, cached, etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)


# Create all tables
def init_db(engine):
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
