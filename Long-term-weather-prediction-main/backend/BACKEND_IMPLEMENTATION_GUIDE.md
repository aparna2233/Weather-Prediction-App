# Backend Implementation Guide
## NASA Weather Prediction Dashboard

This guide explains how to implement and use the backend for the NASA Earth observation weather prediction application.

---

## Architecture Overview

The backend is structured into modular components:

```
backend/
├── app_enhanced.py          # Main Flask API with all endpoints
├── nasa_data.py             # NASA POWER API integration
├── location_service.py      # Location resolution (geocoding, boundaries)
├── train_model.py           # ML model training
├── generate_data.py         # Synthetic data generation
└── requirements.txt         # Dependencies
```

---

## Key Features Implemented

### 1. **Multiple Location Input Methods**

The backend supports three ways to specify locations:

#### a) Direct Coordinates
```json
{
  "latitude": 38.9072,
  "longitude": -77.0369
}
```

#### b) Place Name
```json
{
  "place_name": "Washington DC"
}
```

#### c) Boundary/Area
```json
{
  "boundary": {
    "north": 41.0,
    "south": 40.0,
    "east": -73.0,
    "west": -74.0
  }
}
```

### 2. **NASA Earth Observation Data Integration**

The `nasa_data.py` module integrates with the **NASA POWER API** to fetch real Earth observation data:

- **Temperature** (current, max, min)
- **Precipitation**
- **Humidity**
- **Wind Speed**
- **Surface Pressure**
- **Solar Radiation**

**Key Methods:**
- `fetch_historical_data()` - Get historical weather data
- `get_climate_statistics()` - Calculate statistical measures
- `calculate_threshold_probabilities()` - Compute probability of exceeding thresholds
- `get_time_series()` - Get data for visualization

### 3. **Statistical Analysis**

The backend provides comprehensive statistical analysis:

- **Mean, Median, Standard Deviation**
- **Min/Max values**
- **Percentiles** (25th, 75th, 90th, 95th)
- **Threshold probabilities** (e.g., "60% chance of temperature > 90°F")

Example response:
```json
{
  "statistics": {
    "T2M": {
      "mean": 25.3,
      "median": 25.1,
      "std": 3.2,
      "min": 18.5,
      "max": 32.1,
      "percentile_90": 29.5,
      "percentile_95": 30.8
    }
  }
}
```

### 4. **Probability Calculations**

Calculate the probability of specific weather conditions occurring:

```json
// Request
{
  "latitude": 38.9072,
  "longitude": -77.0369,
  "day_of_year": 180,
  "thresholds": {
    "T2M_MAX": 32.0,  // 90°F in Celsius
    "PRECTOTCORR": 25.0  // Heavy rain threshold
  }
}

// Response
{
  "probabilities": {
    "T2M_MAX": {
      "threshold": 32.0,
      "probability": 65.3,
      "samples": 150,
      "exceed_count": 98
    }
  }
}
```

### 5. **Data Export**

Users can download data in CSV or JSON format:

```bash
POST /api/weather/export
{
  "latitude": 38.9072,
  "longitude": -77.0369,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "format": "csv"  // or "json"
}
```

Returns a downloadable file containing all relevant weather data.

---

## API Endpoints

### Core Weather Endpoints

#### 1. Get Current Weather
```
POST /api/weather/current
```
Get latest weather data for a location.

**Request:**
```json
{
  "latitude": 38.9072,
  "longitude": -77.0369
}
```

**Response:**
```json
{
  "location": {
    "latitude": 38.9072,
    "longitude": -77.0369,
    "address": "Washington, DC, USA"
  },
  "date": "2024-10-03",
  "temperature": 22.5,
  "temperature_max": 27.3,
  "temperature_min": 18.1,
  "precipitation": 2.3,
  "humidity": 65.2,
  "wind_speed": 4.5,
  "pressure": 101.3
}
```

#### 2. Get Weather Statistics
```
POST /api/weather/statistics
```
Get statistical analysis for a specific day of year.

**Request:**
```json
{
  "latitude": 38.9072,
  "longitude": -77.0369,
  "day_of_year": 180,
  "window_days": 15,
  "years_back": 10
}
```

**Response:**
```json
{
  "day_of_year": 180,
  "years_analyzed": 10,
  "statistics": {
    "T2M": {
      "mean": 25.3,
      "median": 25.1,
      "std": 3.2,
      ...
    }
  }
}
```

#### 3. Calculate Threshold Probabilities
```
POST /api/weather/probability
```
Calculate probability of exceeding thresholds.

**Request:**
```json
{
  "latitude": 38.9072,
  "longitude": -77.0369,
  "day_of_year": 180,
  "thresholds": {
    "T2M_MAX": 32.0,
    "PRECTOTCORR": 10.0
  }
}
```

#### 4. Get Time Series Data
```
POST /api/weather/timeseries
```
Get historical time series for visualization.

**Request:**
```json
{
  "latitude": 38.9072,
  "longitude": -77.0369,
  "parameter": "T2M",
  "years": 5
}
```

**Response:**
```json
{
  "parameter": "T2M",
  "parameter_name": "Temperature at 2 Meters (°C)",
  "data": [
    {"date": "2019-01-01", "value": 15.3},
    {"date": "2019-01-02", "value": 16.1},
    ...
  ]
}
```

#### 5. Export Weather Data
```
POST /api/weather/export
```
Download weather data as CSV or JSON.

**Request:**
```json
{
  "latitude": 38.9072,
  "longitude": -77.0369,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "format": "csv"
}
```

Returns downloadable file.

### Location Endpoints

#### 6. Resolve Location
```
POST /api/location/resolve
```
Convert various location inputs to coordinates.

#### 7. Search Location
```
GET /api/location/search?q=Washington%20DC
```
Search for location by name.

#### 8. Reverse Geocode
```
GET /api/location/reverse?lat=38.9072&lon=-77.0369
```
Get place name from coordinates.

### Utility Endpoints

#### 9. Get Available Parameters
```
GET /api/parameters
```
List all available weather parameters.

#### 10. Health Check
```
GET /health
```
Check API status.

---

## Implementation Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Generate Training Data (Optional)

```bash
python generate_data.py
```

This creates `weather_data.csv` with 10,000 synthetic samples.

### Step 3: Train ML Models (Optional)

```bash
python train_model.py
```

This creates:
- `rain_model.pkl`
- `temperature_model.pkl`
- `aqi_model.pkl`
- `scaler.pkl`

### Step 4: Run the Enhanced API

```bash
python app_enhanced.py
```

Or use the original API:
```bash
python app.py
```

The API will run on `http://localhost:5000`

### Step 5: Test the API

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test current weather
curl -X POST http://localhost:5000/api/weather/current \
  -H "Content-Type: application/json" \
  -d '{"latitude": 38.9072, "longitude": -77.0369}'
```

---

## Data Sources

### NASA POWER API

The backend uses the **NASA Prediction Of Worldwide Energy Resources (POWER)** API:

- **Base URL:** `https://power.larc.nasa.gov/api/temporal/daily/point`
- **Coverage:** Global, 1981-present
- **Resolution:** Daily data
- **Parameters:** Temperature, precipitation, humidity, wind, pressure, solar radiation

**Advantages:**
- Free and open access
- High-quality satellite and model data
- Global coverage
- Long historical record

**Limitations:**
- Daily resolution (no hourly data)
- 1-2 day latency for recent data
- Some parameters not available for all locations

### Alternative NASA Data Sources

For production, consider integrating additional NASA APIs:

1. **MODIS (Moderate Resolution Imaging Spectroradiometer)**
   - Real-time satellite imagery
   - Land surface temperature
   - Vegetation indices

2. **AIRS (Atmospheric Infrared Sounder)**
   - Atmospheric temperature and humidity profiles
   - Cloud properties

3. **GPM (Global Precipitation Measurement)**
   - High-resolution precipitation data
   - Near real-time updates

4. **Giovanni (NASA's Earth Data Visualization Tool)**
   - Multiple datasets in one API
   - Advanced visualization options

---

## Scalability Considerations

### 1. Caching

Implement caching for frequently requested data:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_weather_data(lat, lon, start, end):
    return nasa_fetcher.fetch_historical_data(lat, lon, start, end)
```

### 2. Database Storage

For production, store historical data in a database:

```python
# Use PostgreSQL with PostGIS extension
from sqlalchemy import create_engine
import psycopg2

# Store frequently accessed locations
# Cache NASA API responses
# Enable spatial queries
```

### 3. Background Processing

Use Celery for long-running tasks:

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def fetch_large_dataset(lat, lon, years):
    # Process in background
    pass
```

### 4. Rate Limiting

Implement rate limiting to protect the API:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## Frontend Integration

### Example: React/JavaScript

```javascript
// Fetch weather statistics
async function getWeatherStatistics(lat, lon, dayOfYear) {
  const response = await fetch('http://localhost:5000/api/weather/statistics', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      latitude: lat,
      longitude: lon,
      day_of_year: dayOfYear,
      window_days: 15,
      years_back: 10
    })
  });
  
  return await response.json();
}

// Get probability of extreme heat
async function getHeatProbability(lat, lon, dayOfYear) {
  const response = await fetch('http://localhost:5000/api/weather/probability', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      latitude: lat,
      longitude: lon,
      day_of_year: dayOfYear,
      thresholds: {
        T2M_MAX: 32.2  // 90°F in Celsius
      }
    })
  });
  
  return await response.json();
}

// Download data
function downloadWeatherData(lat, lon, startDate, endDate) {
  const url = 'http://localhost:5000/api/weather/export';
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      latitude: lat,
      longitude: lon,
      start_date: startDate,
      end_date: endDate,
      format: 'csv'
    })
  })
  .then(response => response.blob())
  .then(blob => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weather_data_${lat}_${lon}.csv`;
    a.click();
  });
}
```

---

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error message here"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (location/data not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (models not loaded)

---

## Testing

### Unit Tests

```python
# test_api.py
import unittest
from app_enhanced import app

class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
    
    def test_current_weather(self):
        response = self.app.post('/api/weather/current', json={
            'latitude': 38.9072,
            'longitude': -77.0369
        })
        self.assertEqual(response.status_code, 200)
```

### Integration Tests

Test NASA API integration:
```bash
python nasa_data.py
```

Test location service:
```bash
python location_service.py
```

---

## Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app_enhanced:app"]
```

Build and run:
```bash
docker build -t weather-api .
docker run -p 5000:5000 weather-api
```

### Production Considerations

1. **Use a production WSGI server** (Gunicorn, uWSGI)
2. **Enable HTTPS** (SSL/TLS certificates)
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure logging** (structured logs, log aggregation)
5. **Implement authentication** (API keys, OAuth)
6. **Add input validation** (more robust error handling)

---

## Next Steps

1. **Enhance ML Models:** Incorporate actual NASA data into training
2. **Add More Parameters:** Integrate additional NASA datasets
3. **Improve Predictions:** Use deep learning (LSTM, Transformer models)
4. **Add Alerts:** Notify users when thresholds are likely to be exceeded
5. **Create Dashboard:** Build comprehensive frontend visualization
6. **Mobile Support:** Create mobile-friendly responsive design

---

## Resources

- [NASA POWER API Documentation](https://power.larc.nasa.gov/docs/)
- [NASA Earthdata](https://www.earthdata.nasa.gov/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)

---

## Support

For questions or issues:
1. Check the API health endpoint: `/health`
2. Review error messages in responses
3. Check console logs for detailed error information
4. Verify NASA API availability: https://power.larc.nasa.gov/

---

## License

This implementation is for educational and research purposes in response to the NASA challenge.

