"""
Generate synthetic historical weather data for training the ML model.
This creates realistic weather patterns based on location and seasonal variations.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_weather_data(num_samples=10000):
    """
    Generate synthetic weather data with realistic patterns.
    Features: latitude, longitude, day_of_year, month, temperature, humidity, pressure, wind_speed
    Targets: rain_probability, temperature_next_day, aqi
    """
    np.random.seed(42)
    
    data = []
    start_date = datetime(2018, 1, 1)
    
    for i in range(num_samples):
        # Random date within 5 years
        date = start_date + timedelta(days=np.random.randint(0, 365 * 5))
        
        # Random location (latitude and longitude)
        lat = np.random.uniform(-60, 70)  # Avoid extreme poles
        lon = np.random.uniform(-180, 180)
        
        # Seasonal effects
        day_of_year = date.timetuple().tm_yday
        month = date.month
        
        # Base temperature varies by latitude and season
        seasonal_factor = np.sin(2 * np.pi * (day_of_year - 80) / 365)  # Peak in summer
        latitude_factor = np.cos(np.radians(abs(lat))) * 30  # Hotter at equator
        base_temp = 15 + latitude_factor + seasonal_factor * 15 + np.random.normal(0, 5)
        
        # Humidity (higher in tropics and with rain)
        humidity = 40 + 30 * np.cos(np.radians(abs(lat))) + np.random.normal(0, 10)
        humidity = np.clip(humidity, 20, 100)
        
        # Atmospheric pressure
        pressure = 1013 + np.random.normal(0, 15)
        
        # Wind speed
        wind_speed = np.abs(np.random.normal(10, 5))
        
        # Rain probability (higher with high humidity, low pressure)
        rain_prob = 0.1 + 0.6 * (humidity / 100) - 0.3 * ((pressure - 1000) / 40)
        rain_prob = np.clip(rain_prob, 0, 1)
        # Add some randomness
        rain_prob = rain_prob + np.random.normal(0, 0.15)
        rain_prob = np.clip(rain_prob, 0, 1)
        
        # Temperature next day (correlated with current temp)
        temp_next_day = base_temp + np.random.normal(0, 3)
        
        # AQI (Air Quality Index) - worse in populated areas and with certain weather
        # Simulated as random with some correlation to wind speed (lower wind = worse AQI)
        base_aqi = np.random.uniform(20, 150)
        aqi = base_aqi - wind_speed * 2 + np.random.normal(0, 20)
        aqi = np.clip(aqi, 0, 500)
        
        data.append({
            'latitude': lat,
            'longitude': lon,
            'day_of_year': day_of_year,
            'month': month,
            'temperature': base_temp,
            'humidity': humidity,
            'pressure': pressure,
            'wind_speed': wind_speed,
            'rain_probability': rain_prob,
            'temperature_next_day': temp_next_day,
            'aqi': aqi
        })
    
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    print("Generating synthetic weather data...")
    df = generate_weather_data(10000)
    df.to_csv('weather_data.csv', index=False)
    print(f"Generated {len(df)} samples")
    print("\nData summary:")
    print(df.describe())
    print("\nData saved to weather_data.csv")

