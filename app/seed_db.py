"""
Database seeding script with sample venue data
"""

from app.database import SessionLocal, init_db
from app.models.venue import (
    Venue, VenuePhoto, VenueAmenity, VenueHours, VenuePricing,
    SportType, VenueStatus, User
)
from slugify import slugify
import hashlib

def hash_password(password: str) -> str:
    """Simple password hashing for development"""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_database():
    """Seed database with sample data"""
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Venue).count() > 0:
            print("⚠️  Database already contains data. Skipping seed.")
            return
        
        print("🌱 Seeding database...")
        
        # Create admin user
        admin = User(
            email="admin@skaters.com",
            username="admin",
            hashed_password=hash_password("admin"),
            full_name="Admin User",
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        
        # Create test user
        test_user = User(
            email="user@example.com",
            username="testuser",
            hashed_password=hash_password("test"),
            full_name="Test User",
            is_active=True,
            is_admin=False
        )
        db.add(test_user)
        
        # Venue 1: Venice Beach Skatepark
        venice = Venue(
            name="Venice Beach Skatepark",
            slug="venice-beach-skatepark",
            sport_type=SportType.SKATEBOARDING,
            discipline="street",
            venue_type="skatepark",
            address="1800 Ocean Front Walk",
            city="Los Angeles",
            state="CA",
            zip_code="90291",
            country="US",
            latitude=33.985,
            longitude=-118.4695,
            phone="(310) 396-8735",
            website="https://lacity.org",
            description="World-famous skatepark located right on Venice Beach. Features street obstacles, bowls, and a vibrant skate scene. This iconic spot has been featured in countless skate videos and hosts professional competitions throughout the year.",
            year_opened=2009,
            verified=True,
            status=VenueStatus.ACTIVE,
            rating=4.7,
            review_count=234,
            meta_title="Venice Beach Skatepark | Los Angeles, CA | Skaters.com",
            meta_description="World-famous skatepark on Venice Beach with street obstacles and bowls.",
            seo_keywords="skateboarding, skatepark, venice beach, los angeles, california"
        )
        db.add(venice)
        db.flush()
        
        # Venice amenities
        venice_amenities = [
            VenueAmenity(venue_id=venice.id, amenity_type="facilities", amenity_name="Restrooms", available=True),
            VenueAmenity(venue_id=venice.id, amenity_type="facilities", amenity_name="Parking", available=True),
            VenueAmenity(venue_id=venice.id, amenity_type="features", amenity_name="Lighting", available=True),
            VenueAmenity(venue_id=venice.id, amenity_type="features", amenity_name="Street Course", available=True),
            VenueAmenity(venue_id=venice.id, amenity_type="features", amenity_name="Bowls", available=True),
        ]
        db.add_all(venice_amenities)
        
        # Venice hours
        venice_hours = VenueHours(
            venue_id=venice.id,
            monday="6:00 AM - 10:00 PM",
            tuesday="6:00 AM - 10:00 PM",
            wednesday="6:00 AM - 10:00 PM",
            thursday="6:00 AM - 10:00 PM",
            friday="6:00 AM - 10:00 PM",
            saturday="6:00 AM - 10:00 PM",
            sunday="6:00 AM - 10:00 PM"
        )
        db.add(venice_hours)
        
        # Venice pricing
        venice_pricing = VenuePricing(
            venue_id=venice.id,
            admission="Free",
            notes="Free admission, bring your own equipment"
        )
        db.add(venice_pricing)
        
        # Venice photos
        venice_photos = [
            VenuePhoto(venue_id=venice.id, url="https://picsum.photos/seed/venice-beach/800/600", caption="Main view of Venice Beach Skatepark", is_primary=True, approved=True),
            VenuePhoto(venue_id=venice.id, url="https://picsum.photos/seed/venice-bowl/800/600", caption="Concrete bowl section", is_primary=False, approved=True),
            VenuePhoto(venue_id=venice.id, url="https://picsum.photos/seed/venice-street/800/600", caption="Street obstacles and rails", is_primary=False, approved=True),
        ]
        db.add_all(venice_photos)
        
        # Venue 2: Rockefeller Center Ice Rink
        rockefeller = Venue(
            name="Rockefeller Center Ice Rink",
            slug="rockefeller-center-ice-rink",
            sport_type=SportType.ICE_SKATING,
            discipline="figure skating",
            venue_type="ice_rink",
            address="45 Rockefeller Plaza",
            city="New York",
            state="NY",
            zip_code="10020",
            country="US",
            latitude=40.7587,
            longitude=-73.9785,
            phone="(212) 332-7654",
            website="https://www.rockefellercenter.com",
            description="Iconic outdoor ice rink in the heart of Manhattan. Perfect for tourists and locals alike with stunning city views. The rink has been a New York landmark since 1936 and offers skating lessons, birthday parties, and special events throughout the winter season.",
            year_opened=1936,
            verified=True,
            status=VenueStatus.ACTIVE,
            rating=4.6,
            review_count=512,
            meta_title="Rockefeller Center Ice Rink | New York, NY | Skaters.com",
            meta_description="Iconic outdoor ice rink in Manhattan with city views and skating lessons.",
            seo_keywords="ice skating, ice rink, rockefeller center, new york, manhattan"
        )
        db.add(rockefeller)
        db.flush()
        
        # Rockefeller amenities
        rock_amenities = [
            VenueAmenity(venue_id=rockefeller.id, amenity_type="services", amenity_name="Skate Rentals", available=True),
            VenueAmenity(venue_id=rockefeller.id, amenity_type="services", amenity_name="Lessons", available=True),
            VenueAmenity(venue_id=rockefeller.id, amenity_type="features", amenity_name="City Views", available=True),
            VenueAmenity(venue_id=rockefeller.id, amenity_type="facilities", amenity_name="Heated Rest Areas", available=True),
            VenueAmenity(venue_id=rockefeller.id, amenity_type="services", amenity_name="Birthday Parties", available=True),
        ]
        db.add_all(rock_amenities)
        
        # Rockefeller hours
        rock_hours = VenueHours(
            venue_id=rockefeller.id,
            monday="9:00 AM - 12:00 AM",
            tuesday="9:00 AM - 12:00 AM",
            wednesday="9:00 AM - 12:00 AM",
            thursday="9:00 AM - 12:00 AM",
            friday="9:00 AM - 1:00 AM",
            saturday="9:00 AM - 1:00 AM",
            sunday="9:00 AM - 12:00 AM"
        )
        db.add(rock_hours)
        
        # Rockefeller pricing
        rock_pricing = VenuePricing(
            venue_id=rockefeller.id,
            admission="$25-$35",
            rental="$15",
            notes="Prices vary by time and season"
        )
        db.add(rock_pricing)
        
        # Rockefeller photos
        rock_photos = [
            VenuePhoto(venue_id=rockefeller.id, url="https://picsum.photos/seed/rockefeller/800/600", caption="Rockefeller Center Ice Rink with city views", is_primary=True, approved=True),
            VenuePhoto(venue_id=rockefeller.id, url="https://picsum.photos/seed/rockefeller-night/800/600", caption="Evening skating with Christmas tree", is_primary=False, approved=True),
        ]
        db.add_all(rock_photos)
        
        # Venue 3: Moonlight Rollerway
        moonlight = Venue(
            name="Moonlight Rollerway",
            slug="moonlight-rollerway",
            sport_type=SportType.ROLLER_SKATING,
            discipline="recreational",
            venue_type="roller_rink",
            address="5100 San Fernando Rd",
            city="Glendale",
            state="CA",
            zip_code="91204",
            country="US",
            latitude=34.1423,
            longitude=-118.2612,
            phone="(818) 242-1336",
            website="https://www.moonlightrollerway.com",
            description="Classic roller rink with wooden floors, disco lighting, and regular themed nights. Great for families and birthday parties. This historic rink has been operating since 1956 and maintains its vintage charm while offering modern amenities and entertainment.",
            year_opened=1956,
            verified=True,
            status=VenueStatus.ACTIVE,
            rating=4.4,
            review_count=167,
            meta_title="Moonlight Rollerway | Glendale, CA | Skaters.com",
            meta_description="Classic roller rink with wooden floors and disco lighting in Glendale.",
            seo_keywords="roller skating, roller rink, glendale, california, disco"
        )
        db.add(moonlight)
        db.flush()
        
        # Moonlight amenities
        moon_amenities = [
            VenueAmenity(venue_id=moonlight.id, amenity_type="services", amenity_name="Skate Rentals", available=True),
            VenueAmenity(venue_id=moonlight.id, amenity_type="services", amenity_name="Birthday Parties", available=True),
            VenueAmenity(venue_id=moonlight.id, amenity_type="features", amenity_name="Disco Lighting", available=True),
            VenueAmenity(venue_id=moonlight.id, amenity_type="features", amenity_name="Wooden Floor", available=True),
            VenueAmenity(venue_id=moonlight.id, amenity_type="services", amenity_name="Snack Bar", available=True),
        ]
        db.add_all(moon_amenities)
        
        # Moonlight hours
        moon_hours = VenueHours(
            venue_id=moonlight.id,
            wednesday="7:00 PM - 10:00 PM",
            friday="7:30 PM - 11:00 PM",
            saturday="2:00 PM - 5:00 PM, 7:30 PM - 11:00 PM",
            sunday="2:00 PM - 5:00 PM, 7:00 PM - 10:00 PM"
        )
        db.add(moon_hours)
        
        # Moonlight pricing
        moon_pricing = VenuePricing(
            venue_id=moonlight.id,
            admission="$12-$15",
            rental="$5",
            notes="Admission varies by session"
        )
        db.add(moon_pricing)
        
        # Moonlight photos
        moon_photos = [
            VenuePhoto(venue_id=moonlight.id, url="https://picsum.photos/seed/moonlight/800/600", caption="Moonlight Rollerway interior with disco lighting", is_primary=True, approved=True),
            VenuePhoto(venue_id=moonlight.id, url="https://picsum.photos/seed/moonlight-floor/800/600", caption="Classic wooden skating floor", is_primary=False, approved=True),
        ]
        db.add_all(moon_photos)
        
        # Commit all changes
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - Created 2 users (admin@skaters.com / admin)")
        print(f"   - Created 3 venues with full details")
        print(f"   - Added amenities, hours, pricing, and photos")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
