"""
Test script to verify homepage queries work correctly
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.venue import Venue

# Create database connection (same as app uses)
engine = create_engine('sqlite:///./skaters.db')
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 60)
print("TESTING HOMEPAGE QUERIES")
print("=" * 60)

# Test 1: Count all active venues
print("\n1. Testing: Count all active venues")
total = db.query(Venue).filter(Venue.status == "active").count()
print(f"   Result: {total} venues")

# Test 2: Count by state
print("\n2. Testing: Count venues by state (top 5)")
us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA']
states = db.query(
    Venue.state,
    func.count(Venue.id).label('venue_count')
).filter(
    Venue.status == "active",
    Venue.state.in_(us_states)
).group_by(
    Venue.state
).order_by(
    func.count(Venue.id).desc()
).limit(5).all()

for state, count in states:
    print(f"   {state}: {count} venues")

# Test 3: Get popular cities
print("\n3. Testing: Popular cities (top 5)")
cities = db.query(
    Venue.city,
    Venue.state,
    func.count(Venue.id).label('venue_count')
).filter(
    Venue.status == "active"
).group_by(
    Venue.city,
    Venue.state
).order_by(
    func.count(Venue.id).desc()
).limit(5).all()

for city, state, count in cities:
    print(f"   {city}, {state}: {count} venues")

# Test 4: Get featured venues
print("\n4. Testing: Featured venues (top 5)")
venues = db.query(Venue).filter(
    Venue.status == "active"
).order_by(
    Venue.rating.desc()
).limit(5).all()

for v in venues:
    print(f"   {v.name} ({v.city}, {v.state}) - Rating: {v.rating}")

# Test 5: Calculate stats
print("\n5. Testing: Statistics")
us_states_full = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
                  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
                  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
                  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']

total_venues = db.query(Venue).filter(Venue.status == "active", Venue.state.in_(us_states_full)).count()
total_cities = db.query(func.count(func.distinct(Venue.city + Venue.state))).filter(Venue.status == "active", Venue.state.in_(us_states_full)).scalar()
total_states = db.query(func.count(func.distinct(Venue.state))).filter(Venue.status == "active", Venue.state.in_(us_states_full)).scalar()
total_reviews = db.query(func.sum(Venue.review_count)).filter(Venue.status == "active", Venue.state.in_(us_states_full)).scalar() or 0

print(f"   Total Venues: {total_venues}")
print(f"   Total Cities: {total_cities}")
print(f"   Total States: {total_states}")
print(f"   Total Reviews: {int(total_reviews)}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)

db.close()
