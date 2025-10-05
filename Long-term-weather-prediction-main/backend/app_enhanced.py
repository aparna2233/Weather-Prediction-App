"""
Enhanced Flask API for NASA Weather Prediction Dashboard.
Provides comprehensive endpoints for weather analysis, predictions, and data export.
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import io
import json
import os

# Import custom modules
from nasa_data import NASADataFetcher
from location_service import LocationService, parse_location_input

app = Flask(__name__)
CORS(app)

# Initialize services
nasa_fetcher = NASADataFetcher()
location_service = LocationService()

# Load ML models (if they exist)
try:
    rain_model = joblib.load('rain_model.pkl')
    temperature_model = joblib.load('temperature_model.pkl')
    aqi_model = joblib.load('aqi_model.pkl')
    scaler = joblib.load('scaler.pkl')
    models_loaded = True
    print("✓ ML models loaded successfully")
except FileNotFoundError:
    models_loaded = False
    print("⚠ ML models not found. Run train_model.py first.")

# ==================== CORE ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "NASA Weather Prediction API is running",
        "ml_models_loaded": models_loaded,
        "version": "2.0"
    })

@app.route('/api/location/resolve', methods=['POST'])
def resolve_location():
    """
    Resolve location from various input types.
    
    Expected JSON body (one of):
    - {"latitude": X, "longitude": Y}
    - {"place_name": "City, Country"}
    - {"boundary": {"north": N, "south": S, "east": E, "west": W}}
    
    Returns:
    {
        "type": "point" | "boundary",
        "latitude": float,
        "longitude": float,
        "address": string,
        ...
    }
    """
    try:
        data = request.get_json()
        result = parse_location_input(data)
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/current', methods=['POST'])
def get_current_weather():
    """
    Get current/latest weather data for a location.
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float
    }
    
    Returns weather data from NASA POWER API.
    """
    try:
        data = request.get_json()
        
        # Parse location
        location = parse_location_input(data)
        if 'error' in location:
            return jsonify({"error": location['error']}), 400
        
        lat = location['latitude']
        lon = location['longitude']
        
        # Get last 7 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        df = nasa_fetcher.fetch_historical_data(
            lat, lon,
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )
        
        # Get most recent data
        latest = df.iloc[-1] if len(df) > 0 else None
        
        if latest is None:
            return jsonify({"error": "No data available"}), 404
        
        response = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "address": location.get('address')
            },
            "date": df.index[-1].strftime('%Y-%m-%d'),
            "temperature": float(latest.get('T2M', np.nan)) if 'T2M' in latest else None,
            "temperature_max": float(latest.get('T2M_MAX', np.nan)) if 'T2M_MAX' in latest else None,
            "temperature_min": float(latest.get('T2M_MIN', np.nan)) if 'T2M_MIN' in latest else None,
            "precipitation": float(latest.get('PRECTOTCORR', np.nan)) if 'PRECTOTCORR' in latest else None,
            "humidity": float(latest.get('RH2M', np.nan)) if 'RH2M' in latest else None,
            "wind_speed": float(latest.get('WS2M', np.nan)) if 'WS2M' in latest else None,
            "pressure": float(latest.get('PS', np.nan)) if 'PS' in latest else None
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/statistics', methods=['POST'])
def get_weather_statistics():
    """
    Get statistical analysis for a specific day of year.
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float,
        "day_of_year": int (1-365),
        "window_days": int (optional, default 15),
        "years_back": int (optional, default 10)
    }
    
    Returns statistical measures (mean, median, percentiles, etc.)
    """
    try:
        data = request.get_json()
        
        # Parse location
        location = parse_location_input(data)
        if 'error' in location:
            return jsonify({"error": location['error']}), 400
        
        lat = location['latitude']
        lon = location['longitude']
        
        day_of_year = int(data.get('day_of_year', 1))
        window_days = int(data.get('window_days', 15))
        years_back = int(data.get('years_back', 10))
        
        if not 1 <= day_of_year <= 365:
            return jsonify({"error": "day_of_year must be between 1 and 365"}), 400
        
        # Get statistics
        stats = nasa_fetcher.get_climate_statistics(
            lat, lon, day_of_year, window_days, years_back
        )
        
        response = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "address": location.get('address')
            },
            "day_of_year": day_of_year,
            "window_days": window_days,
            "years_analyzed": years_back,
            "statistics": stats
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/probability', methods=['POST'])
def get_threshold_probability():
    """
    Calculate probability of exceeding specified thresholds.
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float,
        "day_of_year": int (1-365),
        "thresholds": {
            "T2M_MAX": 32.0,  // Example: probability of exceeding 32°C
            "PRECTOTCORR": 10.0  // Example: probability of >10mm precipitation
        },
        "window_days": int (optional, default 15),
        "years_back": int (optional, default 10)
    }
    
    Returns probability percentages for each threshold.
    """
    try:
        data = request.get_json()
        
        # Parse location
        location = parse_location_input(data)
        if 'error' in location:
            return jsonify({"error": location['error']}), 400
        
        lat = location['latitude']
        lon = location['longitude']
        
        day_of_year = int(data.get('day_of_year', 1))
        thresholds = data.get('thresholds', {})
        window_days = int(data.get('window_days', 15))
        years_back = int(data.get('years_back', 10))
        
        if not thresholds:
            return jsonify({"error": "No thresholds provided"}), 400
        
        # Calculate probabilities
        probabilities = nasa_fetcher.calculate_threshold_probabilities(
            lat, lon, day_of_year, thresholds, window_days, years_back
        )
        
        response = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "address": location.get('address')
            },
            "day_of_year": day_of_year,
            "window_days": window_days,
            "years_analyzed": years_back,
            "probabilities": probabilities
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/timeseries', methods=['POST'])
def get_time_series():
    """
    Get time series data for visualization.
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float,
        "parameter": string (e.g., "T2M", "PRECTOTCORR"),
        "years": int (optional, default 5)
    }
    
    Returns array of {date, value} pairs.
    """
    try:
        data = request.get_json()
        
        # Parse location
        location = parse_location_input(data)
        if 'error' in location:
            return jsonify({"error": location['error']}), 400
        
        lat = location['latitude']
        lon = location['longitude']
        
        parameter = data.get('parameter', 'T2M')
        years = int(data.get('years', 5))
        
        # Get time series
        time_series = nasa_fetcher.get_time_series(lat, lon, parameter, years)
        
        response = {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "parameter": parameter,
            "parameter_name": nasa_fetcher.available_parameters.get(parameter, parameter),
            "years": years,
            "data": time_series
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/predict', methods=['POST'])
def predict_weather():
    """
    Predict weather using ML models (original endpoint maintained for compatibility).
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float,
        "date": "YYYY-MM-DD"
    }
    """
    if not models_loaded:
        return jsonify({"error": "ML models not loaded. Please train models first."}), 503
    
    try:
        data = request.get_json()
        
        # Parse location
        location = parse_location_input(data)
        if 'error' in location:
            return jsonify({"error": location['error']}), 400
        
        lat = location['latitude']
        lon = location['longitude']
        date_str = data.get('date')
        
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_year = date.timetuple().tm_yday
        month = date.month
        
        # Generate features
        seasonal_factor = np.sin(2 * np.pi * (day_of_year - 80) / 365)
        latitude_factor = np.cos(np.radians(abs(lat))) * 30
        current_temp = 15 + latitude_factor + seasonal_factor * 15 + np.random.normal(0, 2)
        
        humidity = 40 + 30 * np.cos(np.radians(abs(lat))) + np.random.normal(0, 5)
        humidity = np.clip(humidity, 20, 100)
        
        pressure = 1013 + np.random.normal(0, 10)
        wind_speed = np.abs(np.random.normal(10, 3))
        
        features = np.array([[lat, lon, day_of_year, month, current_temp, humidity, pressure, wind_speed]])
        features_scaled = scaler.transform(features)
        
        # Make predictions
        rain_prob = float(rain_model.predict(features_scaled)[0])
        rain_prob = np.clip(rain_prob, 0, 1) * 100
        
        temperature = float(temperature_model.predict(features_scaled)[0])
        aqi = int(np.clip(aqi_model.predict(features_scaled)[0], 0, 500))
        
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
        
        response = {
            "rain_probability": round(rain_prob, 1),
            "temperature": round(temperature, 1),
            "aqi": aqi,
            "aqi_category": aqi_category,
            "location": {
                "latitude": lat,
                "longitude": lon,
                "address": location.get('address')
            },
            "date": date_str
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/weather/export', methods=['POST'])
def export_weather_data():
    """
    Export weather data as CSV or JSON file.
    
    Expected JSON body:
    {
        "latitude": float,
        "longitude": float,
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "format": "csv" | "json" (optional, default "csv")
    }
    
    Returns file for download.
    """
    try:
        data = request.get_json()
        
        # Parse location
        location = parse_location_input(data)
        if 'error' in location:
            return jsonify({"error": location['error']}), 400
        
        lat = location['latitude']
        lon = location['longitude']
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        export_format = data.get('format', 'csv').lower()
        
        if not start_date or not end_date:
            return jsonify({"error": "start_date and end_date are required"}), 400
        
        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Fetch data
        df = nasa_fetcher.fetch_historical_data(
            lat, lon,
            start.strftime('%Y%m%d'),
            end.strftime('%Y%m%d')
        )
        
        # Add location info to DataFrame
        df['latitude'] = lat
        df['longitude'] = lon
        
        # Reset index to make date a column
        df = df.reset_index()
        
        if export_format == 'csv':
            # Export as CSV
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'weather_data_{lat}_{lon}_{start_date}_to_{end_date}.csv'
            )
        
        elif export_format == 'json':
            # Export as JSON
            json_data = df.to_json(orient='records', date_format='iso')
            
            return send_file(
                io.BytesIO(json_data.encode()),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'weather_data_{lat}_{lon}_{start_date}_to_{end_date}.json'
            )
        
        else:
            return jsonify({"error": f"Unsupported format: {export_format}"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parameters', methods=['GET'])
def get_available_parameters():
    """
    Get list of available weather parameters.
    
    Returns dictionary of parameter codes and descriptions.
    """
    return jsonify({
        "parameters": nasa_fetcher.available_parameters
    })

# ==================== UTILITY ENDPOINTS ====================

@app.route('/api/location/search', methods=['GET'])
def search_location():
    """
    Search for location by name.
    
    Query params:
    - q: Search query
    
    Returns geocoding results.
    """
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        result = location_service.geocode_place_name(query)
        
        if not result['success']:
            return jsonify({"error": result['error']}), 404
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/location/reverse', methods=['GET'])
def reverse_geocode_endpoint():
    """
    Get location name from coordinates.
    
    Query params:
    - lat: Latitude
    - lon: Longitude
    
    Returns address information.
    """
    try:
        lat = float(request.args.get('lat', 0))
        lon = float(request.args.get('lon', 0))
        
        result = location_service.reverse_geocode(lat, lon)
        
        if not result['success']:
            return jsonify({"error": result['error']}), 404
        
        return jsonify(result)
    
    except ValueError:
        return jsonify({"error": "Invalid coordinates"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("NASA Weather Prediction Dashboard API")
    print("="*60)
    print(f"ML Models Loaded: {models_loaded}")
    print(f"NASA Data Integration: Active")
    print(f"Location Services: Active")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

