# 🛰️ NASA Earth Observation Data Integration

## Overview

This weather prediction app now integrates **real NASA Earth observation data** from the [NASA POWER API](https://power.larc.nasa.gov/) as part of the [NASA Space Apps Challenge 2025 - "Will It Rain On My Parade?"](https://www.spaceappschallenge.org/2025/challenges/will-it-rain-on-my-parade/?tab=resources).

## What is NASA POWER?

**NASA POWER** (Prediction Of Worldwide Energy Resources) provides:
- 40+ years of historical weather data (1981-present)
- Global coverage for any location on Earth
- Daily meteorological and solar data
- Free API access for research and applications

## Data Sources

### Primary: NASA POWER API
When available, the app fetches:
- **Temperature** (T2M, T2M_MAX, T2M_MIN)
- **Precipitation** (PRECTOTCORR)
- **Humidity** (RH2M)
- **Wind Speed** (WS2M)
- **Surface Pressure** (PS)
- **Solar Radiation** (ALLSKY_SFC_SW_DWN)

### Fallback: Seasonal Patterns
If NASA API is unavailable:
- Uses Indian climate seasonal patterns
- Summer (March-May): 30-43°C
- Monsoon (June-October): 25-30°C
- Winter (November-February): 18-25°C

## How It Works

### 1. Historical Climate Analysis
```python
# Fetches 10 years of historical data for the selected location
nasa_stats = nasa_fetcher.get_climate_statistics(
    latitude=latitude,
    longitude=longitude,
    target_day_of_year=day_of_year,
    window_days=7,      # ±7 days window
    years_back=10       # 10 years of data
)
```

### 2. Statistical Predictions
The app calculates:
- **Mean**: Average value over 10 years
- **Median**: Middle value
- **Standard Deviation**: Data variability
- **Min/Max**: Extreme values
- **Percentiles**: 25th, 75th, 90th, 95th

### 3. Rain Probability Calculation
```python
# Based on historical precipitation data
avg_precip = nasa_stats['PRECTOTCORR']['mean']
rain_probability = min(100, (avg_precip / 10) * 100)
```

## Features

### ✅ Real-Time NASA Data
- Fetches actual historical climate data
- 10-year averages for accurate predictions
- Location-specific weather patterns

### ✅ Intelligent Fallback
- Automatically uses seasonal patterns if API is unavailable
- No interruption in service
- Clear indication of data source

### ✅ Seasonal Context
- Maintains Indian climate seasons
- Combines NASA data with local patterns
- Enhanced rain probability for monsoon

### ✅ Visual Indicators
- 🛰️ **NASA POWER API Data** badge (blue, pulsing)
- 📊 **Seasonal Pattern Data** badge (gray)
- Clear data source attribution

## API Response Format

```json
{
  "rain_probability": 65.3,
  "temperature": 28.5,
  "temperature_max": 32.1,
  "temperature_min": 25.8,
  "humidity": 78.2,
  "wind_speed": 8.5,
  "heat_index": 31.2,
  "wind_chill": 28.5,
  "aqi": 95,
  "aqi_category": "Moderate",
  "season": "Monsoon",
  "data_source": "NASA POWER API (10-year historical average)",
  "nasa_data": true,
  "location": {
    "latitude": 28.61,
    "longitude": 77.21
  },
  "date": "2025-07-15"
}
```

## NASA POWER API Parameters

| Parameter | Description | Unit |
|-----------|-------------|------|
| `T2M` | Temperature at 2 Meters | °C |
| `T2M_MAX` | Maximum Temperature | °C |
| `T2M_MIN` | Minimum Temperature | °C |
| `PRECTOTCORR` | Precipitation (Corrected) | mm/day |
| `RH2M` | Relative Humidity at 2 Meters | % |
| `WS2M` | Wind Speed at 2 Meters | m/s |
| `PS` | Surface Pressure | kPa |
| `ALLSKY_SFC_SW_DWN` | Solar Radiation | MJ/m²/day |

## Benefits of NASA Integration

### 1. **Accuracy**
- Real historical data instead of synthetic patterns
- Location-specific climate characteristics
- Validated by NASA's Earth observation satellites

### 2. **Global Coverage**
- Works for any location on Earth
- Not limited to weather station locations
- Consistent data quality worldwide

### 3. **Long-Term Trends**
- 10 years of historical data
- Captures climate variability
- Identifies seasonal patterns

### 4. **Scientific Credibility**
- NASA-validated data sources
- Peer-reviewed methodologies
- Trusted by researchers worldwide

## Testing NASA Integration

### Test 1: Verify NASA Data is Being Used
1. Open browser console (F12)
2. Select any location on the map
3. Choose a date
4. Click "Predict Weather"
5. Look for: "✓ Using NASA POWER API data for prediction" in backend logs
6. See the 🛰️ NASA badge in results

### Test 2: Compare Different Locations
```
Location 1: New Delhi (28.61°N, 77.21°E)
- Expect: Hot summers, monsoon rains

Location 2: London (51.51°N, -0.13°W)
- Expect: Cooler temps, moderate rain year-round

Location 3: Sydney (-33.87°S, 151.21°E)
- Expect: Opposite seasons (Southern Hemisphere)
```

### Test 3: Seasonal Variations
```
Date: April 15 (Summer)
- High temperatures
- Low rain probability

Date: August 15 (Monsoon)
- Moderate temperatures
- High rain probability

Date: January 15 (Winter)
- Cool temperatures
- Low rain probability
```

## Implementation Details

### Backend Files

**`nasa_data.py`**:
- `NASADataFetcher` class
- API communication
- Data processing
- Statistical calculations

**`app.py`**:
- NASA integration logic
- Fallback handling
- Response formatting

### Frontend Files

**`App.js`**:
- NASA badge display
- Data source indication

**`App.css`**:
- NASA badge styling
- Pulsing animation

## NASA Space Apps Challenge Compliance

This implementation addresses the challenge requirements:

### ✅ Location Input
- Click anywhere on map
- Global coverage via NASA data

### ✅ Weather Variables
- Temperature, precipitation, humidity, wind
- Multiple parameters from NASA POWER

### ✅ Statistical Analysis
- Mean, median, percentiles
- 10-year historical averages

### ✅ Threshold Probabilities
- Rain probability calculations
- Extreme weather detection

### ✅ User-Friendly Output
- Visual indicators
- Clear data attribution
- Seasonal context

### ✅ Data Download
- JSON format responses
- Complete weather data

## API Rate Limits

NASA POWER API:
- **No authentication required**
- **No rate limits** for reasonable use
- **Free for research and applications**
- **Global coverage**

## Error Handling

```python
try:
    # Fetch NASA data
    nasa_stats = get_nasa_climate_data(...)
    data_source = "NASA POWER API"
except Exception as e:
    # Fallback to seasonal patterns
    print(f"NASA API error: {e}")
    data_source = "Seasonal patterns"
```

## Future Enhancements

Potential improvements:
- [ ] Cache NASA data for faster responses
- [ ] Add more NASA parameters (UV index, cloud cover)
- [ ] Historical trend visualization
- [ ] Multi-day forecasts using NASA data
- [ ] Anomaly detection (unusual weather patterns)
- [ ] Climate change indicators

## Resources

- [NASA POWER API Documentation](https://power.larc.nasa.gov/docs/)
- [NASA Space Apps Challenge](https://www.spaceappschallenge.org/2025/challenges/will-it-rain-on-my-parade/?tab=resources)
- [NASA Earth Observation Data](https://earthdata.nasa.gov/)

## Example NASA API Request

```bash
# Fetch temperature data for New Delhi
curl "https://power.larc.nasa.gov/api/temporal/daily/point?\
parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,PS&\
community=RE&\
longitude=77.21&\
latitude=28.61&\
start=20140101&\
end=20241231&\
format=JSON"
```

## Acknowledgments

This project uses data from:
- **NASA POWER Project**
- **NASA Langley Research Center (LaRC)**
- **NASA Earth Science Division**

Data Citation:
> NASA/POWER CERES/MERRA2 Native Resolution Daily Data  
> Dates: 1981-present  
> Location: User-specified  
> NASA Prediction Of Worldwide Energy Resources (POWER) Project  

---

**Created**: October 5, 2025  
**Challenge**: NASA Space Apps 2025 - "Will It Rain On My Parade?"  
**Status**: ✅ Fully Integrated  
**Data Source**: NASA POWER API + Seasonal Patterns  
**Coverage**: Global 🌍

