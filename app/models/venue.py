"""
Database models for venues
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class SportType(str, enum.Enum):
    SKATEBOARDING = "skateboarding"
    ICE_SKATING = "ice_skating"
    ROLLER_SKATING = "roller_skating"
    INLINE_SKATING = "inline_skating"


class VenueStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    
    # Sport information
    sport_type = Column(Enum(SportType), nullable=False, index=True)
    discipline = Column(String(100))
    venue_type = Column(String(100))
    
    # Location
    address = Column(String(300))
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    zip_code = Column(String(10))
    country = Column(String(2), default="US")
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Contact
    phone = Column(String(20))
    email = Column(String(150))
    website = Column(String(300))
    
    # Description
    description = Column(Text, nullable=False)
    year_opened = Column(Integer)
    
    # Status
    verified = Column(Boolean, default=False)
    status = Column(Enum(VenueStatus), default=VenueStatus.PENDING)
    
    # Ratings
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    google_place_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # SEO
    meta_title = Column(String(200))
    meta_description = Column(Text)
    seo_keywords = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    photos = relationship("VenuePhoto", back_populates="venue", cascade="all, delete-orphan")
    amenities = relationship("VenueAmenity", back_populates="venue", cascade="all, delete-orphan")
    hours = relationship("VenueHours", back_populates="venue", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="venue", cascade="all, delete-orphan")
    pricing = relationship("VenuePricing", back_populates="venue", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Venue {self.name} ({self.city}, {self.state})>"


class VenuePhoto(Base):
    __tablename__ = "venue_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    url = Column(String(500), nullable=False)
    caption = Column(String(300))
    is_primary = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    venue = relationship("Venue", back_populates="photos")


class VenueAmenity(Base):
    __tablename__ = "venue_amenities"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    amenity_type = Column(String(50))  # facilities, services, features
    amenity_name = Column(String(100), nullable=False)
    available = Column(Boolean, default=True)
    
    venue = relationship("Venue", back_populates="amenities")


class VenueHours(Base):
    __tablename__ = "venue_hours"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, unique=True)
    monday = Column(String(100))
    tuesday = Column(String(100))
    wednesday = Column(String(100))
    thursday = Column(String(100))
    friday = Column(String(100))
    saturday = Column(String(100))
    sunday = Column(String(100))
    
    venue = relationship("Venue", back_populates="hours")


class VenuePricing(Base):
    __tablename__ = "venue_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, unique=True)
    admission = Column(String(100))
    rental = Column(String(100))
    lessons = Column(String(100))
    notes = Column(Text)
    
    venue = relationship("Venue", back_populates="pricing")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(200))
    comment = Column(Text)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    venue = relationship("Venue", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(150))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reviews = relationship("Review", back_populates="user")
    saved_venues = relationship("SavedVenue", back_populates="user")


class SavedVenue(Base):
    __tablename__ = "saved_venues"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="saved_venues")
    venue = relationship("Venue")
