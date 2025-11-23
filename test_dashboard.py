"""
Test script to add sample reviews and saved venues for dashboard testing
"""

from app.database import SessionLocal
from app.models.venue import Review, SavedVenue, User, Venue
from datetime import datetime

db = SessionLocal()

# Get test user
user = db.query(User).filter(User.username == "testuser").first()
if not user:
    print("❌ Test user not found!")
    exit(1)

print(f"✅ Found user: {user.username} (ID: {user.id})")

# Get venues
venues = db.query(Venue).all()
print(f"✅ Found {len(venues)} venues")

# Add sample reviews
print("\n📝 Adding sample reviews...")

# Check if reviews already exist
existing_reviews = db.query(Review).filter(Review.user_id == user.id).count()
if existing_reviews == 0:
    # Add review for Venice Beach
    venice = db.query(Venue).filter(Venue.slug == "venice-beach-skatepark").first()
    if venice:
        review1 = Review(
            venue_id=venice.id,
            user_id=user.id,
            rating=5,
            title="Amazing skatepark!",
            comment="This is hands down the best skatepark I've ever been to. The bowls are perfectly maintained and the street section has everything you need. Great atmosphere and always friendly people. Highly recommend visiting if you're in LA!",
            approved=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(review1)
        print(f"  ✅ Added review for {venice.name}")
    
    # Add review for Rockefeller
    rockefeller = db.query(Venue).filter(Venue.slug == "rockefeller-center-ice-rink").first()
    if rockefeller:
        review2 = Review(
            venue_id=rockefeller.id,
            user_id=user.id,
            rating=4,
            title="Iconic NYC experience",
            comment="Skating at Rockefeller Center is a must-do in NYC. The atmosphere is magical, especially during the holidays. It can get crowded, but the experience is worth it. The ice quality is excellent and the views are stunning.",
            approved=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(review2)
        print(f"  ✅ Added review for {rockefeller.name}")
    
    # Add pending review for Moonlight
    moonlight = db.query(Venue).filter(Venue.slug == "moonlight-rollerway").first()
    if moonlight:
        review3 = Review(
            venue_id=moonlight.id,
            user_id=user.id,
            rating=5,
            title="Retro vibes and great fun!",
            comment="Love the vintage atmosphere here! The wooden floor is smooth and the disco lights make it feel like you're back in the 70s. Great for families and the staff is super friendly. The snack bar has good options too.",
            approved=False,  # Pending moderation
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(review3)
        print(f"  ✅ Added pending review for {moonlight.name}")
    
    db.commit()
else:
    print(f"  ℹ️  User already has {existing_reviews} reviews")

# Add saved venues
print("\n💾 Adding saved venues...")

existing_saved = db.query(SavedVenue).filter(SavedVenue.user_id == user.id).count()
if existing_saved == 0:
    for venue in venues[:3]:  # Save first 3 venues
        saved = SavedVenue(
            user_id=user.id,
            venue_id=venue.id,
            created_at=datetime.utcnow()
        )
        db.add(saved)
        print(f"  ✅ Saved {venue.name}")
    
    db.commit()
else:
    print(f"  ℹ️  User already has {existing_saved} saved venues")

# Verify data
print("\n📊 Final Stats:")
review_count = db.query(Review).filter(Review.user_id == user.id).count()
saved_count = db.query(SavedVenue).filter(SavedVenue.user_id == user.id).count()
print(f"  Reviews: {review_count}")
print(f"  Saved Venues: {saved_count}")

print("\n✅ Dashboard data ready! Visit http://localhost:8000/dashboard")

db.close()
