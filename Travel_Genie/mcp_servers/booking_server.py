"""
Booking MCP Server - Handles reservations and bookings for travel
Uses FastMCP with stdio transport for efficient process management
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Initialize FastMCP server for booking services
mcp = FastMCP("travel-booking")


@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    class_type: str = "economy"
) -> Dict[str, Any]:
    """
    Search for available flights.
    
    Args:
        origin: Departure airport/city
        destination: Arrival airport/city
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Optional return date for round trips
        passengers: Number of passengers
        class_type: Flight class ('economy', 'business', 'first')
    
    Returns:
        Available flight options
    """
    # Mock flight data - in production, would use real flight API
    airlines = ["SkyWings", "AeroFly", "CloudJet", "SwiftAir"]
    
    flights = []
    for i in range(5):  # Generate 5 flight options
        base_price = random.randint(200, 1500)
        flight = {
            "flight_id": f"FL{random.randint(1000, 9999)}",
            "airline": random.choice(airlines),
            "origin": origin,
            "destination": destination,
            "departure": {
                "date": departure_date,
                "time": f"{random.randint(6, 22):02d}:{random.choice(['00', '30'])}"
            },
            "arrival": {
                "time": f"{random.randint(8, 23):02d}:{random.choice(['00', '30'])}"
            },
            "duration": f"{random.randint(2, 15)}h {random.randint(0, 59)}m",
            "stops": random.choice([0, 1, 2]),
            "price": {
                "economy": base_price,
                "business": base_price * 2.5,
                "first": base_price * 4
            },
            "available_seats": random.randint(5, 50)
        }
        flights.append(flight)
    
    result = {
        "success": True,
        "search_params": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers,
            "class": class_type
        },
        "flights_found": len(flights),
        "outbound_flights": flights
    }
    
    # Add return flights if round trip
    if return_date:
        return_flights = []
        for i in range(5):
            base_price = random.randint(200, 1500)
            flight = {
                "flight_id": f"FL{random.randint(1000, 9999)}",
                "airline": random.choice(airlines),
                "origin": destination,
                "destination": origin,
                "departure": {
                    "date": return_date,
                    "time": f"{random.randint(6, 22):02d}:{random.choice(['00', '30'])}"
                },
                "arrival": {
                    "time": f"{random.randint(8, 23):02d}:{random.choice(['00', '30'])}"
                },
                "duration": f"{random.randint(2, 15)}h {random.randint(0, 59)}m",
                "stops": random.choice([0, 1, 2]),
                "price": {
                    "economy": base_price,
                    "business": base_price * 2.5,
                    "first": base_price * 4
                },
                "available_seats": random.randint(5, 50)
            }
            return_flights.append(flight)
        result["return_flights"] = return_flights
    
    return result


@mcp.tool()
async def search_hotels(
    location: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1,
    amenities: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for available hotels.
    
    Args:
        location: Hotel location/city
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        rooms: Number of rooms
        amenities: Desired amenities list
    
    Returns:
        Available hotel options
    """
    # Mock hotel data - in production, would use real hotel API
    hotel_names = [
        "Grand Plaza Hotel",
        "City Center Inn",
        "Luxury Suites",
        "Budget Lodge",
        "Boutique Hotel",
        "Resort & Spa",
        "Business Hotel",
        "Historic Inn"
    ]
    
    hotels = []
    for i, name in enumerate(hotel_names[:6]):
        hotel = {
            "hotel_id": f"HTL{random.randint(1000, 9999)}",
            "name": name,
            "location": location,
            "rating": round(random.uniform(3.5, 5.0), 1),
            "stars": random.randint(2, 5),
            "price_per_night": random.randint(50, 500),
            "total_price": 0,  # Will calculate
            "available_rooms": random.randint(1, 20),
            "amenities": random.sample([
                "WiFi", "Pool", "Gym", "Spa", "Restaurant",
                "Bar", "Parking", "Pet-friendly", "Business Center",
                "Airport Shuttle", "Room Service", "Breakfast"
            ], k=random.randint(4, 8)),
            "distance_from_center": f"{round(random.uniform(0.5, 10.0), 1)} km",
            "cancellation": random.choice(["Free cancellation", "Non-refundable", "Cancel before 24h"]),
            "reviews": {
                "count": random.randint(50, 2000),
                "score": round(random.uniform(7.5, 9.8), 1)
            }
        }
        
        # Calculate nights and total price
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        hotel["total_price"] = hotel["price_per_night"] * nights * rooms
        hotel["nights"] = nights
        
        hotels.append(hotel)
    
    # Filter by amenities if provided
    if amenities:
        hotels = [h for h in hotels if any(a in h["amenities"] for a in amenities)]
    
    # Sort by rating
    hotels.sort(key=lambda x: x["rating"], reverse=True)
    
    return {
        "success": True,
        "search_params": {
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "rooms": rooms,
            "nights": nights
        },
        "hotels_found": len(hotels),
        "hotels": hotels
    }


@mcp.tool()
async def book_flight(
    flight_id: str,
    passengers: List[Dict[str, str]],
    class_type: str = "economy",
    add_insurance: bool = False
) -> Dict[str, Any]:
    """
    Book a flight reservation.
    
    Args:
        flight_id: ID of the flight to book
        passengers: List of passenger details [{"first_name": "", "last_name": "", "passport": ""}]
        class_type: Flight class
        add_insurance: Add travel insurance
    
    Returns:
        Booking confirmation details
    """
    # Mock booking - in production, would process real booking
    booking_ref = f"BK{random.randint(100000, 999999)}"
    base_price = random.randint(200, 1500)
    
    # Calculate pricing
    class_multiplier = {"economy": 1, "business": 2.5, "first": 4}
    ticket_price = base_price * class_multiplier.get(class_type, 1)
    insurance_price = 50 if add_insurance else 0
    total_price = (ticket_price * len(passengers)) + insurance_price
    
    confirmation = {
        "success": True,
        "booking_reference": booking_ref,
        "flight_id": flight_id,
        "status": "confirmed",
        "passengers": passengers,
        "class": class_type,
        "pricing": {
            "ticket_price": ticket_price,
            "num_passengers": len(passengers),
            "insurance": insurance_price,
            "total": total_price,
            "currency": "USD"
        },
        "booking_date": datetime.now().isoformat(),
        "payment_status": "pending",
        "confirmation_email": "sent"
    }
    
    return confirmation


@mcp.tool()
async def book_hotel(
    hotel_id: str,
    check_in: str,
    check_out: str,
    guest_name: str,
    rooms: int = 1,
    special_requests: Optional[str] = None
) -> Dict[str, Any]:
    """
    Book a hotel reservation.
    
    Args:
        hotel_id: ID of the hotel to book
        check_in: Check-in date
        check_out: Check-out date
        guest_name: Primary guest name
        rooms: Number of rooms
        special_requests: Any special requests
    
    Returns:
        Hotel booking confirmation
    """
    # Mock booking - in production, would process real booking
    booking_ref = f"HTL{random.randint(100000, 999999)}"
    
    # Calculate nights
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
    nights = (check_out_date - check_in_date).days
    
    price_per_night = random.randint(50, 500)
    total_price = price_per_night * nights * rooms
    
    confirmation = {
        "success": True,
        "booking_reference": booking_ref,
        "hotel_id": hotel_id,
        "status": "confirmed",
        "guest_name": guest_name,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "rooms": rooms,
        "pricing": {
            "price_per_night": price_per_night,
            "total_nights": nights,
            "num_rooms": rooms,
            "total": total_price,
            "currency": "USD"
        },
        "special_requests": special_requests,
        "booking_date": datetime.now().isoformat(),
        "cancellation_policy": "Free cancellation until 24h before check-in",
        "confirmation_email": "sent"
    }
    
    return confirmation


@mcp.tool()
async def search_car_rentals(
    location: str,
    pickup_date: str,
    return_date: str,
    car_type: str = "economy"
) -> Dict[str, Any]:
    """
    Search for car rental options.
    
    Args:
        location: Pickup location
        pickup_date: Pickup date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        car_type: Type of car ('economy', 'compact', 'midsize', 'suv', 'luxury')
    
    Returns:
        Available car rental options
    """
    # Mock car rental data
    companies = ["RentACar", "DriveEasy", "AutoRent", "QuickCar"]
    car_models = {
        "economy": ["Toyota Yaris", "Nissan Versa", "Hyundai Accent"],
        "compact": ["Honda Civic", "Toyota Corolla", "Mazda3"],
        "midsize": ["Toyota Camry", "Honda Accord", "Nissan Altima"],
        "suv": ["Toyota RAV4", "Honda CR-V", "Ford Explorer"],
        "luxury": ["BMW 3 Series", "Mercedes C-Class", "Audi A4"]
    }
    
    # Calculate rental days
    pickup = datetime.strptime(pickup_date, "%Y-%m-%d")
    return_dt = datetime.strptime(return_date, "%Y-%m-%d")
    rental_days = (return_dt - pickup).days
    
    rentals = []
    for company in companies:
        models = car_models.get(car_type, car_models["economy"])
        rental = {
            "rental_id": f"CAR{random.randint(1000, 9999)}",
            "company": company,
            "car_model": random.choice(models),
            "car_type": car_type,
            "price_per_day": random.randint(30, 150),
            "total_price": 0,  # Will calculate
            "features": random.sample([
                "Automatic", "Manual", "GPS", "Bluetooth",
                "USB Port", "Backup Camera", "Cruise Control"
            ], k=random.randint(3, 5)),
            "mileage": random.choice(["Unlimited", "200 km/day", "500 km/day"]),
            "insurance_included": random.choice([True, False]),
            "fuel_policy": "Full to Full",
            "pickup_location": location
        }
        rental["total_price"] = rental["price_per_day"] * rental_days
        rental["rental_days"] = rental_days
        rentals.append(rental)
    
    return {
        "success": True,
        "search_params": {
            "location": location,
            "pickup_date": pickup_date,
            "return_date": return_date,
            "car_type": car_type,
            "rental_days": rental_days
        },
        "rentals_found": len(rentals),
        "rentals": rentals
    }


@mcp.tool()
async def get_booking_status(
    booking_reference: str
) -> Dict[str, Any]:
    """
    Check the status of an existing booking.
    
    Args:
        booking_reference: Booking reference number
    
    Returns:
        Current booking status and details
    """
    # Mock booking status - in production, would query real database
    statuses = ["confirmed", "pending", "processing", "completed"]
    
    booking_info = {
        "success": True,
        "booking_reference": booking_reference,
        "status": random.choice(statuses),
        "type": random.choice(["flight", "hotel", "car"]),
        "created_date": "2025-11-01T10:30:00Z",
        "last_updated": datetime.now().isoformat(),
        "payment_status": random.choice(["paid", "pending", "partial"]),
        "details": {
            "traveler": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123"
        },
        "actions_available": ["modify", "cancel", "print"]
    }
    
    return booking_info


@mcp.tool()
async def cancel_booking(
    booking_reference: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancel an existing booking.
    
    Args:
        booking_reference: Booking reference to cancel
        reason: Optional cancellation reason
    
    Returns:
        Cancellation confirmation
    """
    # Mock cancellation - in production, would process real cancellation
    refund_amount = random.randint(100, 1000)
    
    return {
        "success": True,
        "booking_reference": booking_reference,
        "status": "cancelled",
        "cancellation_date": datetime.now().isoformat(),
        "reason": reason or "Customer requested",
        "refund": {
            "amount": refund_amount,
            "currency": "USD",
            "method": "Original payment method",
            "estimated_days": "5-7 business days"
        },
        "confirmation_number": f"CXL{random.randint(100000, 999999)}"
    }


@mcp.resource("bookings://active")
async def get_active_bookings() -> str:
    """
    Get all active bookings.
    
    Returns:
        JSON string of active bookings
    """
    # Mock active bookings
    bookings = [
        {
            "reference": "BK123456",
            "type": "flight",
            "destination": "Paris",
            "date": "2025-12-15",
            "status": "confirmed"
        },
        {
            "reference": "HTL789012",
            "type": "hotel",
            "location": "Paris",
            "check_in": "2025-12-15",
            "status": "confirmed"
        }
    ]
    return json.dumps(bookings, indent=2)


# Main entry point
if __name__ == "__main__":
    import os
    
    # Get transport type from environment or default to stdio
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    if transport in ["sse", "http"]:
        # Get host and port from environment
        host = os.getenv("MCP_HOST", "localhost")
        port = int(os.getenv("MCP_PORT", 8002))
        
        # Run with SSE transport on specified port
        mcp.run(transport="sse", host=host, port=port)
        print(f"Starting MCP server on {host}:{port} with {transport} transport")
    else:
        # Run with stdio transport (default, backward compatible)
        mcp.run(transport="stdio")
        port = os.getenv("MCP_PORT", "N/A")
        print(f"Starting MCP server with stdio transport (configured port: {port})")
