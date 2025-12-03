import json
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from mcp.server.fastmcp import FastMCP

# Directory to store geocoded results
GEOCODE_DIR = "geocoded_locations"

# Initialize FastMCP server
mcp = FastMCP("geocoder")

def get_geolocator():
    """Initialize and return a geolocator with rate limiting."""
    # Generate a unique email identifier using UUID
    email_identifier = f"{uuid.uuid4()}.com"
    geolocator = Nominatim(user_agent=email_identifier)
    # Rate limiter automatically handles the 1-second delay
    return RateLimiter(geolocator.geocode, min_delay_seconds=1), RateLimiter(geolocator.reverse, min_delay_seconds=1)

@mcp.tool()
def geocode_location(
    location: str,
    exactly_one: bool = True,
    timeout: int = 10,
    language: str = "en",
    addressdetails: bool = True,
    country_codes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert a location name/address to latitude and longitude coordinates.
    
    Args:
        location: The location to geocode (e.g., "Ashburn, Virginia", "Paris, France")
        exactly_one: Return only one result if True, otherwise return multiple matches
        timeout: Timeout in seconds for the geocoding request
        language: Language for the result (default: "en")
        addressdetails: Include detailed address components in response
        country_codes: Limit search to specific countries (e.g., "us,ca")
        
    Returns:
        Dict containing geocoding results and metadata
    """
    
    try:
        geocode, _ = get_geolocator()
        
        # Build geocoding parameters
        params = {
            'exactly_one': exactly_one,
            'timeout': timeout,
            'language': language,
            'addressdetails': addressdetails
        }
        
        if country_codes:
            params['country_codes'] = country_codes
        
        # Perform geocoding
        result = geocode(location, **params)
        
        if not result:
            return {
                "success": False,
                "error": f"No coordinates found for location: {location}",
                "query": location
            }
        
        # Handle multiple results
        if not exactly_one and isinstance(result, list):
            locations_data = []
            for loc in result:
                locations_data.append({
                    "latitude": float(loc.latitude),
                    "longitude": float(loc.longitude),
                    "display_name": loc.address,
                    "raw_data": loc.raw
                })
            
            response = {
                "success": True,
                "query": location,
                "multiple_results": True,
                "count": len(locations_data),
                "locations": locations_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Single result
            location_data = {
                "latitude": float(result.latitude),
                "longitude": float(result.longitude),
                "display_name": result.address,
                "raw_data": result.raw
            }
            
            response = {
                "success": True,
                "query": location,
                "multiple_results": False,
                "location_data": location_data,
                "timestamp": datetime.now().isoformat()
            }
        
        # Save to file for resource access
        location_id = f"{location.replace(' ', '_').replace(',', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(GEOCODE_DIR, exist_ok=True)
        
        file_path = os.path.join(GEOCODE_DIR, f"{location_id}.json")
        with open(file_path, "w") as f:
            json.dump(response, f, indent=2)
        
        response["location_id"] = location_id
        print(f"Geocoding results saved to: {file_path}")
        
        return response
        
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        return {
            "success": False,
            "error": f"Geocoding service error: {str(e)}",
            "query": location
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "query": location
        }

@mcp.tool()
def reverse_geocode(
    latitude: float,
    longitude: float,
    exactly_one: bool = True,
    timeout: int = 10,
    language: str = "en",
    zoom: int = 18
) -> Dict[str, Any]:
    """
    Convert latitude and longitude coordinates to a location name/address.
    
    Args:
        latitude: Latitude coordinate (e.g., 39.0458)
        longitude: Longitude coordinate (e.g., -77.5011)
        exactly_one: Return only one result if True
        timeout: Timeout in seconds for the request
        language: Language for the result (default: "en")
        zoom: Level of detail (1-18, higher = more detailed)
        
    Returns:
        Dict containing reverse geocoding results
    """
    
    try:
        _, reverse_geocode_func = get_geolocator()
        
        # Perform reverse geocoding
        result = reverse_geocode_func(
            (latitude, longitude),
            exactly_one=exactly_one,
            timeout=timeout,
            language=language,
            zoom=zoom
        )
        
        if not result:
            return {
                "success": False,
                "error": f"No address found for coordinates: {latitude}, {longitude}",
                "coordinates": {"latitude": latitude, "longitude": longitude}
            }
        
        response = {
            "success": True,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "address": result.address,
            "raw_data": result.raw,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        coord_id = f"reverse_{str(latitude).replace('.', '_')}_{str(longitude).replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(GEOCODE_DIR, exist_ok=True)
        
        file_path = os.path.join(GEOCODE_DIR, f"{coord_id}.json")
        with open(file_path, "w") as f:
            json.dump(response, f, indent=2)
        
        response["location_id"] = coord_id
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Reverse geocoding error: {str(e)}",
            "coordinates": {"latitude": latitude, "longitude": longitude}
        }

@mcp.tool()
def batch_geocode(locations: List[str]) -> Dict[str, Any]:
    """
    Geocode multiple locations in a single request.
    
    Args:
        locations: List of location names to geocode
        
    Returns:
        Dict containing results for all locations
    """
    
    results = {
        "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_locations": len(locations),
        "successful": 0,
        "failed": 0,
        "results": []
    }
    
    for location in locations:
        result = geocode_location(location)
        results["results"].append(result)
        
        if result.get("success"):
            results["successful"] += 1
        else:
            results["failed"] += 1
    
    # Save batch results
    os.makedirs(GEOCODE_DIR, exist_ok=True)
    file_path = os.path.join(GEOCODE_DIR, f"{results['batch_id']}.json")
    with open(file_path, "w") as f:
        json.dump(results, f, indent=2)
    
    return results

@mcp.tool()
def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    unit: str = "km"
) -> Dict[str, Any]:
    """
    Calculate the distance between two geographic coordinates.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        unit: Unit for distance ("km", "miles", "nm" for nautical miles)
        
    Returns:
        Dict containing distance calculation results
    """
    
    try:
        from geopy.distance import geodesic
        
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        
        distance = geodesic(point1, point2)
        
        if unit.lower() == "miles":
            result_distance = distance.miles
        elif unit.lower() == "nm":
            result_distance = distance.nautical
        else:  # Default to kilometers
            result_distance = distance.kilometers
        
        return {
            "success": True,
            "distance": round(result_distance, 2),
            "unit": unit,
            "point1": {"latitude": lat1, "longitude": lon1},
            "point2": {"latitude": lat2, "longitude": lon2},
            "calculation_method": "geodesic"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Distance calculation error: {str(e)}"
        }

@mcp.tool()
def search_locations(query: str, max_results: int = 10) -> str:
    """
    Search through previously geocoded locations.
    
    Args:
        query: Search term to find in saved locations
        max_results: Maximum number of results to return
        
    Returns:
        JSON string with matching locations
    """
    
    if not os.path.exists(GEOCODE_DIR):
        return json.dumps({"message": "No geocoded locations found."})
    
    matches = []
    
    for filename in os.listdir(GEOCODE_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(GEOCODE_DIR, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Search in query and display_name
                if query.lower() in data.get('query', '').lower():
                    matches.append(data)
                    continue
                    
                # Search in location data
                if data.get('location_data'):
                    if query.lower() in data['location_data'].get('display_name', '').lower():
                        matches.append(data)
                elif data.get('locations'):  # Multiple results
                    for loc in data['locations']:
                        if query.lower() in loc.get('display_name', '').lower():
                            matches.append(data)
                            break
                            
            except (json.JSONDecodeError, KeyError):
                continue
    
    return json.dumps({
        "query": query,
        "matches_found": len(matches),
        "results": matches[:max_results]
    }, indent=2)

@mcp.resource("geocoder://locations")
def get_geocoded_locations() -> str:
    """
    List all previously geocoded locations.
    
    This resource provides a summary of all saved geocoding results.
    """
    locations = []
    
    if os.path.exists(GEOCODE_DIR):
        for filename in os.listdir(GEOCODE_DIR):
            if filename.endswith('.json'):
                location_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(GEOCODE_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                        summary = {
                            'location_id': location_id,
                            'query': data.get('query', 'N/A'),
                            'success': data.get('success', False),
                            'timestamp': data.get('timestamp', 'N/A')
                        }
                        
                        if data.get('success'):
                            if data.get('location_data'):
                                # Single result
                                loc_data = data['location_data']
                                summary['coordinates'] = f"{loc_data['latitude']}, {loc_data['longitude']}"
                                summary['address'] = loc_data.get('display_name', 'N/A')
                            elif data.get('locations'):
                                # Multiple results
                                summary['multiple_results'] = len(data['locations'])
                                first_loc = data['locations'][0]
                                summary['coordinates'] = f"{first_loc['latitude']}, {first_loc['longitude']}"
                                summary['address'] = first_loc.get('display_name', 'N/A')
                        
                        locations.append(summary)
                        
                except (json.JSONDecodeError, KeyError):
                    continue
    
    content = "# Geocoded Locations\n\n"
    
    if locations:
        content += f"Total geocoded locations: {len(locations)}\n\n"
        
        # Sort by timestamp (newest first)
        locations.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        for loc in locations:
            content += f"## {loc['location_id']}\n"
            content += f"- **Query**: {loc['query']}\n"
            content += f"- **Status**: {'✅ Success' if loc['success'] else '❌ Failed'}\n"
            
            if loc['success']:
                content += f"- **Coordinates**: {loc.get('coordinates', 'N/A')}\n"
                content += f"- **Address**: {loc.get('address', 'N/A')}\n"
                if loc.get('multiple_results'):
                    content += f"- **Multiple Results**: {loc['multiple_results']} locations found\n"
            
            content += f"- **Timestamp**: {loc['timestamp']}\n\n"
            content += "---\n\n"
    else:
        content += "No geocoded locations found.\n\n"
        content += "Use the geocode_location tool to convert addresses to coordinates.\n"
    
    return content

@mcp.resource("geocoder://{location_id}")
def get_location_details(location_id: str) -> str:
    """
    Get detailed information about a specific geocoded location.
    
    Args:
        location_id: The location ID to retrieve details for
    """
    file_path = os.path.join(GEOCODE_DIR, f"{location_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Location Not Found: {location_id}\n\nNo geocoded location found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        content = f"# Geocoded Location: {location_id}\n\n"
        content += f"## Query Information\n"
        content += f"- **Original Query**: {data.get('query', 'N/A')}\n"
        content += f"- **Status**: {'✅ Success' if data.get('success') else '❌ Failed'}\n"
        content += f"- **Timestamp**: {data.get('timestamp', 'N/A')}\n\n"
        
        if not data.get('success'):
            content += f"## Error Details\n"
            content += f"- **Error**: {data.get('error', 'Unknown error')}\n"
            return content
        
        if data.get('multiple_results'):
            content += f"## Multiple Results Found ({data.get('count', 0)})\n\n"
            for i, location in enumerate(data.get('locations', []), 1):
                content += f"### Result {i}\n"
                content += f"- **Coordinates**: {location['latitude']}, {location['longitude']}\n"
                content += f"- **Address**: {location['display_name']}\n"
                
                # Add detailed address components if available
                raw_data = location.get('raw_data', {})
                if raw_data.get('address'):
                    addr = raw_data['address']
                    content += f"- **Country**: {addr.get('country', 'N/A')}\n"
                    content += f"- **State/Region**: {addr.get('state', addr.get('region', 'N/A'))}\n"
                    content += f"- **City**: {addr.get('city', addr.get('town', addr.get('village', 'N/A')))}\n"
                    if addr.get('postcode'):
                        content += f"- **Postal Code**: {addr['postcode']}\n"
                
                content += "\n"
        else:
            # Single result
            location_data = data.get('location_data', {})
            content += f"## Location Details\n"
            content += f"- **Coordinates**: {location_data.get('latitude', 'N/A')}, {location_data.get('longitude', 'N/A')}\n"
            content += f"- **Full Address**: {location_data.get('display_name', 'N/A')}\n\n"
            
            # Add detailed address components
            raw_data = location_data.get('raw_data', {})
            if raw_data.get('address'):
                content += f"## Address Components\n"
                addr = raw_data['address']
                
                # Common address fields
                address_fields = [
                    ('house_number', 'House Number'),
                    ('road', 'Street'),
                    ('neighbourhood', 'Neighbourhood'),
                    ('suburb', 'Suburb'),
                    ('city', 'City'),
                    ('town', 'Town'),
                    ('village', 'Village'),
                    ('county', 'County'),
                    ('state', 'State'),
                    ('region', 'Region'),
                    ('postcode', 'Postal Code'),
                    ('country', 'Country'),
                    ('country_code', 'Country Code')
                ]
                
                for field, label in address_fields:
                    if addr.get(field):
                        content += f"- **{label}**: {addr[field]}\n"
                
                content += "\n"
            
            # Bounding box if available
            if raw_data.get('boundingbox'):
                bbox = raw_data['boundingbox']
                content += f"## Bounding Box\n"
                content += f"- **South**: {bbox[0]}\n"
                content += f"- **North**: {bbox[1]}\n"
                content += f"- **West**: {bbox[2]}\n"
                content += f"- **East**: {bbox[3]}\n\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted location data for ID: {location_id}"

@mcp.prompt()
def location_analysis_prompt(
    location: str,
    include_nearby: bool = True,
    analysis_type: str = "general"
) -> str:
    """Generate a comprehensive location analysis prompt for Claude."""
    
    prompt = f"""Analyze the location "{location}" and provide comprehensive geographical and contextual information.

Please perform the following analysis:

1. **Geocoding**: Use the geocode_location tool to get precise coordinates for "{location}"

2. **Location Details**: Based on the geocoding results, provide:
   - Exact coordinates (latitude, longitude)
   - Full formatted address
   - Administrative divisions (country, state/region, city)
   - Postal/zip code if available

3. **Geographical Context**:"""
    
    if analysis_type == "travel":
        prompt += """
   - Climate and weather patterns
   - Time zone information
   - Elevation and terrain characteristics
   - Transportation accessibility (airports, railways, highways)
   - Tourist attractions and points of interest"""
    elif analysis_type == "business":
        prompt += """
   - Economic indicators and business environment
   - Demographics and population data
   - Infrastructure and connectivity
   - Regulatory environment
   - Market opportunities and challenges"""
    else:  # general
        prompt += """
   - Physical geography and topography
   - Climate characteristics
   - Population and demographics
   - Historical significance
   - Cultural and economic importance"""
    
    if include_nearby:
        prompt += f"""

4. **Nearby Locations**: 
   - Major cities within 100km
   - Notable landmarks or features
   - Regional context and connections"""
    
    prompt += f"""

5. **Practical Information**:
   - Best times to visit (if applicable)
   - Transportation options
   - Language(s) spoken
   - Currency (if different from common currencies)

Please start by geocoding the location to get accurate coordinates, then provide the comprehensive analysis based on the geocoding results."""

    return prompt

@mcp.prompt()
def distance_calculation_prompt(
    location1: str,
    location2: str,
    include_route_info: bool = True
) -> str:
    """Generate a prompt for calculating and analyzing distance between two locations."""
    
    return f"""Calculate the distance between "{location1}" and "{location2}" and provide detailed travel analysis.

Please perform the following steps:

1. **Geocode Both Locations**:
   - Use geocode_location for "{location1}"
   - Use geocode_location for "{location2}"
   - Verify both locations were found successfully

2. **Distance Calculation**:
   - Use calculate_distance with the obtained coordinates
   - Provide distance in kilometers, miles, and nautical miles
   - Calculate approximate travel times for different transportation methods

3. **Location Comparison**:
   - Compare the two locations' geographical features
   - Time zone differences
   - Climate variations
   - Cultural or economic differences

{'4. **Travel Route Analysis**:' if include_route_info else ''}
{'''   - Suggest optimal travel routes
   - Transportation options (air, road, rail)
   - Approximate travel costs and duration
   - Best travel seasons or times''' if include_route_info else ''}

5. **Practical Considerations**:
   - Border crossings or visa requirements (if applicable)
   - Language barriers
   - Currency differences
   - Communication/connectivity options

Start with geocoding both locations to ensure accurate coordinate-based calculations."""

@mcp.prompt()
def batch_location_prompt(locations: List[str], analysis_focus: str = "coordinates") -> str:
    """Generate a prompt for batch processing multiple locations."""
    
    locations_str = '", "'.join(locations)
    
    return f"""Process and analyze the following locations in batch: "{locations_str}"

Please perform the following batch analysis:

1. **Batch Geocoding**: Use batch_geocode with the list of locations: {locations}

2. **Results Summary**:
   - Success/failure rate for geocoding
   - Successfully geocoded locations with coordinates
   - Failed locations and potential reasons

3. **Comparative Analysis**:"""
    
    if analysis_focus == "distances":
        return prompt + """
   - Calculate distances between all location pairs
   - Identify the closest and furthest locations
   - Create a distance matrix summary"""
    elif analysis_focus == "regions":
        return prompt + """
   - Group locations by country/region
   - Identify geographical clusters
   - Compare regional characteristics"""
    else:  # coordinates
        return prompt + """
   - Display all coordinates in a organized table
   - Identify geographical spread (bounding box)
   - Sort locations by latitude/longitude
   - Highlight any geographical patterns"""
    
    prompt += """

4. **Visualization Suggestions**:
   - Recommend map plotting approaches
   - Suggest grouping strategies
   - Identify outliers or notable patterns

5. **Data Export**:
   - Format results for easy export/use
   - Provide coordinates in different formats (decimal degrees, DMS)
   - Include all relevant metadata

The analysis should help understand the geographical distribution and relationships between all the specified locations."""

    return prompt

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')