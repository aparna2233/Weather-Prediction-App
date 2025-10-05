"""
Train ML models to predict rain probability, temperature, and AQI.
Uses Random Forest models for robust predictions.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
import joblib

def train_models():
    """Train three models: rain probability, temperature, and AQI prediction."""
    
    # Load data
    print("Loading data...")
    df = pd.read_csv('weather_data.csv')
    
    # Features for prediction
    feature_columns = ['latitude', 'longitude', 'day_of_year', 'month', 
                      'temperature', 'humidity', 'pressure', 'wind_speed']
    
    X = df[feature_columns]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save scaler
    joblib.dump(scaler, 'scaler.pkl')
    print("Scaler saved.")
    
    # Train-test split
    X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
    
    # Model 1: Rain Probability
    print("\nTraining rain probability model...")
    y_rain = df['rain_probability']
    y_rain_train, y_rain_test = train_test_split(y_rain, test_size=0.2, random_state=42)
    
    rain_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
    rain_model.fit(X_train, y_rain_train)
    
    y_rain_pred = rain_model.predict(X_test)
    y_rain_pred = np.clip(y_rain_pred, 0, 1)  # Ensure 0-1 range
    
    rain_mae = mean_absolute_error(y_rain_test, y_rain_pred)
    rain_r2 = r2_score(y_rain_test, y_rain_pred)
    print(f"Rain Model - MAE: {rain_mae:.4f}, R2: {rain_r2:.4f}")
    
    joblib.dump(rain_model, 'rain_model.pkl')
    
    # Model 2: Temperature
    print("\nTraining temperature model...")
    y_temp = df['temperature_next_day']
    y_temp_train, y_temp_test = train_test_split(y_temp, test_size=0.2, random_state=42)
    
    temp_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
    temp_model.fit(X_train, y_temp_train)
    
    y_temp_pred = temp_model.predict(X_test)
    
    temp_mae = mean_absolute_error(y_temp_test, y_temp_pred)
    temp_r2 = r2_score(y_temp_test, y_temp_pred)
    print(f"Temperature Model - MAE: {temp_mae:.2f}°C, R2: {temp_r2:.4f}")
    
    joblib.dump(temp_model, 'temperature_model.pkl')
    
    # Model 3: AQI
    print("\nTraining AQI model...")
    y_aqi = df['aqi']
    y_aqi_train, y_aqi_test = train_test_split(y_aqi, test_size=0.2, random_state=42)
    
    aqi_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
    aqi_model.fit(X_train, y_aqi_train)
    
    y_aqi_pred = aqi_model.predict(X_test)
    y_aqi_pred = np.clip(y_aqi_pred, 0, 500)  # AQI range
    
    aqi_mae = mean_absolute_error(y_aqi_test, y_aqi_pred)
    aqi_r2 = r2_score(y_aqi_test, y_aqi_pred)
    print(f"AQI Model - MAE: {aqi_mae:.2f}, R2: {aqi_r2:.4f}")
    
    joblib.dump(aqi_model, 'aqi_model.pkl')
    
    print("\n✓ All models trained and saved successfully!")

if __name__ == '__main__':
    train_models()

