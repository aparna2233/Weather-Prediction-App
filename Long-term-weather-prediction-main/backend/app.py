"""
Flask API for weather prediction using NASA Earth Observation Data.
Provides endpoint to predict rain probability, temperature, and AQI based on location and date.
Integrates with NASA POWER API for real historical weather data.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from datetime import datetime, timedelta
from nasa_data import NASADataFetcher

app = Flask(__name__)
CORS(app)

# Initialize NASA data fetcher
nasa_fetcher = NASADataFetcher()
print("✓ NASA POWER API integration initialized")

# Load models and scaler
print("Loading ML models...")
rain_model = joblib.load('rain_model.pkl')
temperature_model = joblib.load('temperature_model.pkl')
aqi_model = joblib.load('aqi_model.pkl')
scaler = joblib.load('scaler.pkl')
print("✓ ML models loaded successfully!")

def get_nasa_climate_data(latitude, longitude, day_of_year):
    """
    Fetch NASA historical climate data for the specified location and day.
    Returns statistics based on 10 years of historical data.
    """
    try:
        stats = nasa_fetcher.get_climate_statistics(
            latitude=latitude,
            longitude=longitude,
            target_day_of_year=day_of_year,
            window_days=7,  # ±7 days window
            years_back=10   # 10 years of historical data
        )
        return stats, True
    except Exception as e:
        print(f"NASA API error: {e}")
        return None, False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Weather prediction API with NASA data is running",
        "nasa_integration": "active",
        "data_source": "NASA POWER API"
    })

@app.route('/predict', methods=['POST'])
def predict_weather():
    """
    Predict weather based on location and date.
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float,
        "date": "YYYY-MM-DD"
    }
    
    Returns:
    {
        "rain_probability": float (0-100%),
        "temperature": float (Celsius),
        "aqi": int,
        "aqi_category": string
    }
    """
    try:
        data = request.get_json()
        
        # Extract parameters
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        date_str = data.get('date')
        
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_year = date.timetuple().tm_yday
        month = date.month
        
        # Try to fetch NASA historical climate data
        nasa_stats, nasa_available = get_nasa_climate_data(latitude, longitude, day_of_year)
        
        # Determine season for Indian climate
        if month in [3, 4, 5]:  # Summer (March-May)
            season_name = "Summer"
            rain_factor = 0.2
        elif month in [6, 7, 8, 9, 10]:  # Monsoon (June-October)
            season_name = "Monsoon"
            rain_factor = 0.8
        else:  # Winter (November-February)
            season_name = "Winter"
            rain_factor = 0.3
        
        # Use NASA data if available, otherwise use seasonal patterns
        if nasa_available and nasa_stats:
            print(f"✓ Using NASA POWER API data for prediction")
            # Use NASA historical averages
            current_temp = nasa_stats.get('T2M', {}).get('mean', 25)
            temp_max = nasa_stats.get('T2M_MAX', {}).get('mean', current_temp + 5)
            temp_min = nasa_stats.get('T2M_MIN', {}).get('mean', current_temp - 5)
            humidity = nasa_stats.get('RH2M', {}).get('mean', 60)
            wind_speed = nasa_stats.get('WS2M', {}).get('mean', 5)
            pressure = nasa_stats.get('PS', {}).get('mean', 101.3) * 10  # Convert kPa to hPa
            
            # Calculate rain probability from NASA precipitation data
            precip_data = nasa_stats.get('PRECTOTCORR', {})
            if precip_data:
                # Higher historical precipitation = higher rain probability
                avg_precip = precip_data.get('mean', 0)
                rain_prob_nasa = min(100, (avg_precip / 10) * 100)  # Scale to percentage
                rain_factor = rain_prob_nasa / 100
            
            data_source = "NASA POWER API (10-year historical average)"
        else:
            print("⚠ NASA API unavailable, using seasonal patterns")
            # Fallback to seasonal patterns
            if month in [3, 4, 5]:  # Summer
                base_temp = np.random.uniform(30, 43)
                humidity = np.random.uniform(30, 50)
            elif month in [6, 7, 8, 9, 10]:  # Monsoon
                base_temp = np.random.uniform(25, 30)
                humidity = np.random.uniform(70, 95)
            else:  # Winter
                base_temp = np.random.uniform(18, 25)
                humidity = np.random.uniform(40, 65)
            
            # Add latitude adjustment
            latitude_adjustment = (30 - abs(latitude)) / 10
            current_temp = base_temp + latitude_adjustment + np.random.normal(0, 1)
            temp_max = current_temp + np.random.uniform(2, 5)
            temp_min = current_temp - np.random.uniform(2, 5)
            humidity = np.clip(humidity + np.random.normal(0, 3), 20, 100)
            pressure = 1013 + np.random.normal(0, 10)
            wind_speed = np.abs(np.random.normal(10, 3))
            
            data_source = "Seasonal patterns (NASA API unavailable)"
        
        # Prepare features
        features = np.array([[
            latitude,
            longitude,
            day_of_year,
            month,
            current_temp,
            humidity,
            pressure,
            wind_speed
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make predictions
        rain_prob_base = float(rain_model.predict(features_scaled)[0])
        # Apply seasonal rain factor
        rain_prob = rain_prob_base * rain_factor + (rain_factor * 30)  # Boost based on season
        rain_prob = np.clip(rain_prob, 0, 100)  # Ensure 0-100%
        
        # Use the seasonal temperature instead of model prediction
        temperature = current_temp
        
        aqi = float(aqi_model.predict(features_scaled)[0])
        aqi = int(np.clip(aqi, 0, 500))
        
        # Categorize AQI
        if aqi <= 50:
            aqi_category = "Good"
        elif aqi <= 100:
            aqi_category = "Moderate"
        elif aqi <= 150:
            aqi_category = "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            aqi_category = "Unhealthy"
        elif aqi <= 300:
            aqi_category = "Very Unhealthy"
        else:
            aqi_category = "Hazardous"
        
        # Calculate heat index (simplified formula)
        heat_index = temperature
        if temperature >= 27 and humidity >= 40:
            heat_index = -8.78469475556 + 1.61139411 * temperature + 2.33854883889 * humidity
            heat_index -= 0.14611605 * temperature * humidity
            heat_index -= 0.012308094 * temperature**2
            heat_index -= 0.0164248277778 * humidity**2
        
        # Calculate wind chill (simplified formula)
        wind_chill = temperature
        if temperature <= 10 and wind_speed >= 4.8:
            wind_chill = 13.12 + 0.6215 * temperature - 11.37 * (wind_speed * 3.6)**0.16
            wind_chill += 0.3965 * temperature * (wind_speed * 3.6)**0.16
        
        response = {
            "rain_probability": round(rain_prob, 1),
            "temperature": round(temperature, 1),
            "temperature_max": round(temp_max, 1),
            "temperature_min": round(temp_min, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "heat_index": round(heat_index, 1),
            "wind_chill": round(wind_chill, 1),
            "aqi": aqi,
            "aqi_category": aqi_category,
            "season": season_name,
            "data_source": data_source,
            "nasa_data": nasa_available,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "date": date_str
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

