"""
Location Service Module.
Handles different location input methods: place names, coordinates, and boundaries.
"""
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import numpy as np
from typing import Dict, List, Tuple, Optional

class LocationService:
    """Handles location resolution and validation."""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="nasa_weather_dashboard")
    
    def geocode_place_name(self, place_name: str) -> Dict:
        """
        Convert place name to coordinates.
        
        Args:
            place_name: Name of location (e.g., "Washington DC", "New York", "Tokyo")
        
        Returns:
            Dictionary with latitude, longitude, and formatted address
        """
        try:
            location = self.geocoder.geocode(place_name)
            
            if location is None:
                return {
                    'success': False,
                    'error': f"Could not find location: {place_name}"
                }
            
            return {
                'success': True,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address,
                'raw': {
                    'display_name': location.address,
                    'type': location.raw.get('type', 'unknown')
                }
            }
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            return {
                'success': False,
                'error': f"Geocoding service error: {str(e)}"
            }
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """
        Get place name from coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            Dictionary with address information
        """
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}")
            
            if location is None:
                return {
                    'success': False,
                    'error': "Could not reverse geocode coordinates"
                }
            
            address = location.raw.get('address', {})
            
            return {
                'success': True,
                'address': location.address,
                'city': address.get('city') or address.get('town') or address.get('village'),
                'state': address.get('state'),
                'country': address.get('country'),
                'country_code': address.get('country_code')
            }
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            return {
                'success': False,
                'error': f"Reverse geocoding error: {str(e)}"
            }
    
    def validate_coordinates(self, latitude: float, longitude: float) -> Dict:
        """
        Validate that coordinates are within valid ranges.
        
        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
        
        Returns:
            Dictionary with validation result
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return {
                'valid': False,
                'error': "Coordinates must be numeric values"
            }
        
        if not -90 <= latitude <= 90:
            return {
                'valid': False,
                'error': f"Latitude must be between -90 and 90 (got {latitude})"
            }
        
        if not -180 <= longitude <= 180:
            return {
                'valid': False,
                'error': f"Longitude must be between -180 and 180 (got {longitude})"
            }
        
        return {
            'valid': True,
            'latitude': latitude,
            'longitude': longitude
        }
    
    def get_boundary_grid(
        self, 
        north: float, 
        south: float, 
        east: float, 
        west: float,
        grid_size: int = 5
    ) -> List[Dict]:
        """
        Generate a grid of points within a boundary for area analysis.
        
        Args:
            north: Northern boundary latitude
            south: Southern boundary latitude
            east: Eastern boundary longitude
            west: Western boundary longitude
            grid_size: Number of points per dimension (default: 5x5 grid)
        
        Returns:
            List of coordinate dictionaries
        """
        # Validate boundaries
        if not (south < north and west < east):
            raise ValueError("Invalid boundary: south must be < north and west must be < east")
        
        # Generate grid
        lats = np.linspace(south, north, grid_size)
        lons = np.linspace(west, east, grid_size)
        
        grid_points = []
        for lat in lats:
            for lon in lons:
                grid_points.append({
                    'latitude': float(lat),
                    'longitude': float(lon)
                })
        
        return grid_points
    
    def calculate_boundary_center(
        self,
        north: float,
        south: float,
        east: float,
        west: float
    ) -> Dict:
        """
        Calculate the center point of a boundary.
        
        Args:
            north: Northern boundary latitude
            south: Southern boundary latitude
            east: Eastern boundary longitude
            west: Western boundary longitude
        
        Returns:
            Dictionary with center coordinates
        """
        center_lat = (north + south) / 2
        center_lon = (east + west) / 2
        
        return {
            'latitude': center_lat,
            'longitude': center_lon
        }
    
    def get_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: int = 50
    ) -> List[Dict]:
        """
        Get nearby cities for context (simplified implementation).
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
        
        Returns:
            List of nearby locations
        """
        # Note: This is a simplified implementation
        # In production, you'd use a proper geocoding database
        
        try:
            # Get location info for center point
            location_info = self.reverse_geocode(latitude, longitude)
            
            if location_info['success']:
                return [{
                    'name': location_info.get('city', 'Unknown'),
                    'state': location_info.get('state'),
                    'country': location_info.get('country'),
                    'distance_km': 0,
                    'latitude': latitude,
                    'longitude': longitude
                }]
            
            return []
        
        except Exception as e:
            print(f"Error getting nearby cities: {e}")
            return []


def parse_location_input(data: Dict) -> Dict:
    """
    Parse different types of location input and normalize to coordinates.
    
    Supports:
    1. Direct coordinates: {"latitude": X, "longitude": Y}
    2. Place name: {"place_name": "City, State"}
    3. Boundary: {"boundary": {"north": N, "south": S, "east": E, "west": W}}
    
    Args:
        data: Input dictionary with location information
    
    Returns:
        Normalized location dictionary with coordinates
    """
    service = LocationService()
    
    # Case 1: Direct coordinates
    if 'latitude' in data and 'longitude' in data:
        validation = service.validate_coordinates(data['latitude'], data['longitude'])
        if not validation['valid']:
            return {'error': validation['error']}
        
        # Try to get place name
        reverse = service.reverse_geocode(data['latitude'], data['longitude'])
        
        return {
            'type': 'point',
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'address': reverse.get('address', 'Unknown location') if reverse['success'] else None
        }
    
    # Case 2: Place name
    elif 'place_name' in data:
        result = service.geocode_place_name(data['place_name'])
        if not result['success']:
            return {'error': result['error']}
        
        return {
            'type': 'point',
            'latitude': result['latitude'],
            'longitude': result['longitude'],
            'address': result['address'],
            'place_name': data['place_name']
        }
    
    # Case 3: Boundary
    elif 'boundary' in data:
        boundary = data['boundary']
        required = ['north', 'south', 'east', 'west']
        
        if not all(key in boundary for key in required):
            return {'error': f"Boundary must include: {', '.join(required)}"}
        
        try:
            # Get center point
            center = service.calculate_boundary_center(
                boundary['north'],
                boundary['south'],
                boundary['east'],
                boundary['west']
            )
            
            # Generate grid for area analysis
            grid = service.get_boundary_grid(
                boundary['north'],
                boundary['south'],
                boundary['east'],
                boundary['west'],
                grid_size=data.get('grid_size', 5)
            )
            
            return {
                'type': 'boundary',
                'center': center,
                'boundary': boundary,
                'grid_points': grid
            }
        
        except Exception as e:
            return {'error': f"Invalid boundary: {str(e)}"}
    
    else:
        return {'error': "Invalid location input. Must provide 'latitude'+'longitude', 'place_name', or 'boundary'"}


if __name__ == '__main__':
    # Test the location service
    service = LocationService()
    
    print("Testing Location Service\n")
    
    # Test 1: Geocoding place name
    print("1. Geocoding 'Washington DC':")
    result = service.geocode_place_name("Washington DC")
    if result['success']:
        print(f"   Coordinates: ({result['latitude']}, {result['longitude']})")
        print(f"   Address: {result['address']}")
    
    # Test 2: Reverse geocoding
    print("\n2. Reverse geocoding (40.7128, -74.0060):")
    result = service.reverse_geocode(40.7128, -74.0060)
    if result['success']:
        print(f"   Address: {result['address']}")
    
    # Test 3: Boundary grid
    print("\n3. Generating grid for boundary:")
    grid = service.get_boundary_grid(41, 40, -73, -74, grid_size=3)
    print(f"   Generated {len(grid)} points")
    print(f"   First point: {grid[0]}")
    
    # Test 4: Parse different input types
    print("\n4. Testing input parsing:")
    
    test_inputs = [
        {"latitude": 38.9072, "longitude": -77.0369},
        {"place_name": "Tokyo, Japan"},
        {"boundary": {"north": 41, "south": 40, "east": -73, "west": -74}}
    ]
    
    for i, inp in enumerate(test_inputs):
        print(f"\n   Test {i+1}: {list(inp.keys())[0]}")
        result = parse_location_input(inp)
        if 'error' not in result:
            print(f"   Type: {result['type']}")
            if result['type'] == 'point':
                print(f"   Location: ({result['latitude']}, {result['longitude']})")
            elif result['type'] == 'boundary':
                print(f"   Center: ({result['center']['latitude']}, {result['center']['longitude']})")
                print(f"   Grid points: {len(result['grid_points'])}")
        else:
            print(f"   Error: {result['error']}")

