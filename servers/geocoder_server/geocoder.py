from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Generate a unique email identifer using a combination of GUIDs and adding '.com' to it
import uuid

email_identifier = f"{uuid.uuid4()}.com"

geolocator = Nominatim(user_agent=email_identifier)
# Rate limiter automatically handles the 1-second delay
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

location = geocode("Ashburn, Virginia")
if location:
    print(f"Latitude: {location.latitude}, Longitude: {location.longitude}")