"""
API Testing Script
Test all endpoints of the enhanced weather prediction API.
"""
import requests
import json
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health check endpoint."""
    print_section("1. HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_location_resolve():
    """Test location resolution."""
    print_section("2. LOCATION RESOLUTION")
    
    test_cases = [
        {
            "name": "Direct Coordinates",
            "data": {"latitude": 38.9072, "longitude": -77.0369}
        },
        {
            "name": "Place Name",
            "data": {"place_name": "Washington DC"}
        },
        {
            "name": "Boundary",
            "data": {
                "boundary": {
                    "north": 39.0,
                    "south": 38.8,
                    "east": -76.9,
                    "west": -77.1
                }
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n  Test: {test['name']}")
        response = requests.post(
            f"{BASE_URL}/api/location/resolve",
            json=test['data']
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Type: {result.get('type')}")
            if result['type'] == 'point':
                print(f"  Coordinates: ({result['latitude']}, {result['longitude']})")
            elif result['type'] == 'boundary':
                print(f"  Center: ({result['center']['latitude']}, {result['center']['longitude']})")
                print(f"  Grid points: {len(result['grid_points'])}")
        else:
            print(f"  Error: {response.json()}")

def test_current_weather():
    """Test current weather endpoint."""
    print_section("3. CURRENT WEATHER")
    
    data = {
        "latitude": 38.9072,
        "longitude": -77.0369
    }
    
    print("  Location: Washington DC")
    response = requests.post(
        f"{BASE_URL}/api/weather/current",
        json=data
    )
    
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\n  Date: {result.get('date')}")
        print(f"  Temperature: {result.get('temperature')}°C")
        print(f"  Temperature Max: {result.get('temperature_max')}°C")
        print(f"  Temperature Min: {result.get('temperature_min')}°C")
        print(f"  Precipitation: {result.get('precipitation')} mm")
        print(f"  Humidity: {result.get('humidity')}%")
        print(f"  Wind Speed: {result.get('wind_speed')} m/s")
        print(f"  Pressure: {result.get('pressure')} kPa")
    else:
        print(f"  Error: {response.json()}")

def test_weather_statistics():
    """Test weather statistics endpoint."""
    print_section("4. WEATHER STATISTICS")
    
    # Test for July 1st (day 182)
    data = {
        "latitude": 38.9072,
        "longitude": -77.0369,
        "day_of_year": 182,
        "window_days": 15,
        "years_back": 10
    }
    
    print("  Location: Washington DC")
    print("  Day of Year: 182 (approximately July 1)")
    print("  Window: ±15 days")
    print("  Years analyzed: 10")
    
    response = requests.post(
        f"{BASE_URL}/api/weather/statistics",
        json=data
    )
    
    print(f"\n  Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        stats = result.get('statistics', {})
        
        if 'T2M' in stats:
            temp_stats = stats['T2M']
            print(f"\n  Temperature Statistics:")
            print(f"    Mean: {temp_stats['mean']:.1f}°C")
            print(f"    Median: {temp_stats['median']:.1f}°C")
            print(f"    Std Dev: {temp_stats['std']:.1f}°C")
            print(f"    Min: {temp_stats['min']:.1f}°C")
            print(f"    Max: {temp_stats['max']:.1f}°C")
            print(f"    90th Percentile: {temp_stats['percentile_90']:.1f}°C")
        
        if 'PRECTOTCORR' in stats:
            precip_stats = stats['PRECTOTCORR']
            print(f"\n  Precipitation Statistics:")
            print(f"    Mean: {precip_stats['mean']:.1f} mm/day")
            print(f"    Median: {precip_stats['median']:.1f} mm/day")
            print(f"    Max: {precip_stats['max']:.1f} mm/day")
    else:
        print(f"  Error: {response.json()}")

def test_threshold_probability():
    """Test threshold probability calculation."""
    print_section("5. THRESHOLD PROBABILITY")
    
    # Test probability of extreme heat (>32°C / 90°F)
    data = {
        "latitude": 38.9072,
        "longitude": -77.0369,
        "day_of_year": 182,
        "thresholds": {
            "T2M_MAX": 32.0,  # 90°F in Celsius
            "PRECTOTCORR": 10.0  # Heavy rain threshold
        },
        "window_days": 15,
        "years_back": 10
    }
    
    print("  Location: Washington DC")
    print("  Day of Year: 182 (approximately July 1)")
    print("  Thresholds:")
    print("    - Max Temperature > 32°C (90°F)")
    print("    - Precipitation > 10mm/day")
    
    response = requests.post(
        f"{BASE_URL}/api/weather/probability",
        json=data
    )
    
    print(f"\n  Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        probs = result.get('probabilities', {})
        
        for param, prob_data in probs.items():
            print(f"\n  {param}:")
            print(f"    Threshold: {prob_data['threshold']}")
            print(f"    Probability: {prob_data['probability']}%")
            print(f"    Samples: {prob_data['samples']}")
            print(f"    Times exceeded: {prob_data['exceed_count']}")
    else:
        print(f"  Error: {response.json()}")

def test_time_series():
    """Test time series endpoint."""
    print_section("6. TIME SERIES DATA")
    
    data = {
        "latitude": 38.9072,
        "longitude": -77.0369,
        "parameter": "T2M",
        "years": 2
    }
    
    print("  Location: Washington DC")
    print("  Parameter: Temperature (T2M)")
    print("  Time Range: Last 2 years")
    
    response = requests.post(
        f"{BASE_URL}/api/weather/timeseries",
        json=data
    )
    
    print(f"\n  Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        data_points = result.get('data', [])
        print(f"  Data points received: {len(data_points)}")
        if len(data_points) > 0:
            print(f"  First point: {data_points[0]}")
            print(f"  Last point: {data_points[-1]}")
    else:
        print(f"  Error: {response.json()}")

def test_available_parameters():
    """Test available parameters endpoint."""
    print_section("7. AVAILABLE PARAMETERS")
    
    response = requests.get(f"{BASE_URL}/api/parameters")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        params = result.get('parameters', {})
        print(f"\nAvailable parameters ({len(params)}):")
        for code, description in params.items():
            print(f"  - {code}: {description}")
    else:
        print(f"Error: {response.json()}")

def test_location_search():
    """Test location search endpoint."""
    print_section("8. LOCATION SEARCH")
    
    queries = ["Tokyo", "Paris, France", "New York City"]
    
    for query in queries:
        print(f"\n  Searching: {query}")
        response = requests.get(
            f"{BASE_URL}/api/location/search",
            params={"q": query}
        )
        
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Found: {result.get('address')}")
            print(f"  Coordinates: ({result.get('latitude')}, {result.get('longitude')})")
        else:
            print(f"  Error: {response.json()}")

def test_export_data():
    """Test data export endpoint."""
    print_section("9. DATA EXPORT")
    
    # Get last 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = {
        "latitude": 38.9072,
        "longitude": -77.0369,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "format": "csv"
    }
    
    print(f"  Exporting data for Washington DC")
    print(f"  Date range: {data['start_date']} to {data['end_date']}")
    print(f"  Format: CSV")
    
    response = requests.post(
        f"{BASE_URL}/api/weather/export",
        json=data
    )
    
    print(f"\n  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  File size: {len(response.content)} bytes")
        print(f"  Content type: {response.headers.get('Content-Type')}")
        
        # Save to file
        filename = "test_export.csv"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"  ✓ Saved to: {filename}")
    else:
        print(f"  Error: Could not download file")

def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*60)
    print("  NASA WEATHER PREDICTION API - COMPREHENSIVE TEST")
    print("="*60)
    print(f"\n  Testing API at: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Health Check", test_health),
        ("Location Resolution", test_location_resolve),
        ("Current Weather", test_current_weather),
        ("Weather Statistics", test_weather_statistics),
        ("Threshold Probability", test_threshold_probability),
        ("Time Series", test_time_series),
        ("Available Parameters", test_available_parameters),
        ("Location Search", test_location_search),
        ("Data Export", test_export_data)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "✓ PASS"))
        except Exception as e:
            results.append((name, f"✗ FAIL: {str(e)}"))
    
    # Summary
    print_section("TEST SUMMARY")
    for name, result in results:
        print(f"  {result} - {name}")
    
    passed = sum(1 for _, r in results if r.startswith("✓"))
    total = len(results)
    print(f"\n  Total: {passed}/{total} tests passed")
    
    print("\n" + "="*60)
    print("  Testing complete!")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print(f"   Make sure the server is running at {BASE_URL}")
        print(f"   Start the server with: python app_enhanced.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")

