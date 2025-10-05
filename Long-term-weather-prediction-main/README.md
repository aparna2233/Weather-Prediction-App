# 🌍 Long-Term Weather Prediction App

A modern web application that predicts weather conditions (rain probability, temperature, and Air Quality Index) for any location on Earth using Machine Learning models trained on historical data.

![Weather Prediction App](https://img.shields.io/badge/ML-Weather%20Prediction-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-red)

## ✨ Features

- 🗺️ **Interactive Map**: Click anywhere on the map to select a location
- 📅 **Date Selection**: Choose any future date for prediction
- 🤖 **ML-Powered Predictions**: Random Forest models trained on synthetic historical data
- 🌧️ **Rain Probability**: Get percentage probability of rainfall
- 🌡️ **Temperature Forecast**: Predicted temperature in Celsius
- 💨 **Air Quality Index**: AQI prediction with color-coded categories
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## 🏗️ Architecture

### Backend (Python/Flask)
- **Flask API**: RESTful API for weather predictions
- **Data Generation**: Synthetic weather data with realistic patterns
- **Models**: Separate models for rain probability, temperature, and AQI

### Frontend (React)
- **React**: Modern component-based UI
- **Leaflet**: Interactive map with OpenStreetMap tiles
- **Axios**: HTTP client for API communication
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Long-term-weather-prediction
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate training data
python generate_data.py

# Train ML models
python train_model.py
```

This will create:
- `weather_data.csv`: Synthetic historical weather data (10,000 samples)
- `rain_model.pkl`: Trained model for rain probability
- `temperature_model.pkl`: Trained model for temperature
- `aqi_model.pkl`: Trained model for Air Quality Index
- `scaler.pkl`: Feature scaler for preprocessing

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install
```

## ▶️ Running the Application

### Start Backend Server

```bash
cd backend
# Activate virtual environment if not already activated
python app.py
```

The Flask server will start at `http://localhost:5000`

### Start Frontend Server

Open a new terminal:

```bash
cd frontend
npm start
```

The React app will start at `http://localhost:3000` and automatically open in your browser.

## 🎮 How to Use

1. **Select Location**: Click anywhere on the map to select a location for weather prediction
2. **Choose Date**: Pick a date using the date selector
3. **Get Prediction**: Click the "Predict Weather" button
4. **View Results**: See the predicted rain probability, temperature, and AQI with visual indicators

## 📊 Model Performance

The ML models are trained on 10,000 synthetic data points with realistic weather patterns:

- **Rain Model**: Predicts probability (0-100%) based on humidity, pressure, and other factors
- **Temperature Model**: Predicts temperature with seasonal and geographical variations
- **AQI Model**: Predicts air quality index (0-500) considering wind and location

## 🎨 UI Features

- **Gradient Backgrounds**: Eye-catching purple gradient theme
- **Animated Cards**: Smooth hover effects and transitions
- **Progress Bars**: Visual representation of rain probability
- **Color-Coded AQI**: AQI scale with standard color coding
- **Responsive Design**: Adapts to different screen sizes
- **Weather Icons**: Dynamic icons based on predictions

## 📁 Project Structure

```
Long-term-weather-prediction/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── generate_data.py       # Data generation script
│   ├── train_model.py         # Model training script
│   ├── requirements.txt       # Python dependencies
│   ├── weather_data.csv       # Generated training data
│   ├── rain_model.pkl         # Trained rain model
│   ├── temperature_model.pkl  # Trained temperature model
│   ├── aqi_model.pkl          # Trained AQI model
│   └── scaler.pkl             # Feature scaler
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styles
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Global styles
│   └── package.json          # Node dependencies
└── README.md
```

## 🔧 API Endpoints

### POST /predict

Predicts weather for a given location and date.

**Request Body:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "date": "2025-10-15"
}
```

**Response:**
```json
{
  "rain_probability": 45.3,
  "temperature": 22.5,
  "aqi": 65,
  "aqi_category": "Moderate",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "date": "2025-10-15"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Weather prediction API is running"
}
```

## 🎯 Future Enhancements

- [ ] Integrate real weather APIs for current conditions
- [ ] Add multi-day forecasts
- [ ] Include more weather parameters (wind speed, humidity, etc.)
- [ ] User location detection
- [ ] Historical weather data visualization
- [ ] Save favorite locations
- [ ] Weather alerts and notifications
- [ ] Dark mode toggle

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created with ❤️ for weather prediction enthusiasts

## 🙏 Acknowledgments

- OpenStreetMap for map tiles
- Leaflet for the mapping library
- Scikit-learn for ML models
- React community for excellent documentation

