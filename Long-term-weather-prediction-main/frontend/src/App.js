import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './App.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Component to handle map clicks
function LocationMarker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition(e.latlng);
    },
  });

  return position === null ? null : <Marker position={position}></Marker>;
}

function App() {
  const [position, setPosition] = useState(null);
  const [date, setDate] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  
  // User-defined thresholds (in Celsius and metric units)
  const [thresholds, setThresholds] = useState({
    veryHotTemp: 32,      // 90°F = 32°C
    veryColdTemp: 0,      // 32°F = 0°C
    veryWindy: 15,        // m/s
    veryWet: 70,          // humidity %
    uncomfortableHeat: 35, // heat index °C
    uncomfortableWind: 5   // wind chill °C
  });

  const handleSearchLocation = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setError('Please enter a location to search');
      return;
    }

    setSearchLoading(true);
    setError(null);

    try {
      // Use Nominatim (OpenStreetMap) geocoding API
      const response = await axios.get(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`,
        {
          headers: {
            'User-Agent': 'WeatherPredictionApp/1.0'
          }
        }
      );

      if (response.data && response.data.length > 0) {
        const result = response.data[0];
        const newPosition = {
          lat: parseFloat(result.lat),
          lng: parseFloat(result.lon)
        };
        setPosition(newPosition);
        setError(null);
      } else {
        setError('Location not found. Please try a different search term.');
      }
    } catch (err) {
      setError('Failed to search location. Please try again.');
    } finally {
      setSearchLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!position) {
      setError('Please select a location on the map or search for a place');
      return;
    }
    if (!date) {
      setError('Please select a date');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await axios.post('http://localhost:5002/predict', {
        latitude: position.lat,
        longitude: position.lng,
        date: date,
      });

      setPrediction(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get prediction. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const getAQIColor = (aqi) => {
    if (aqi <= 50) return '#00e400';
    if (aqi <= 100) return '#ffff00';
    if (aqi <= 150) return '#ff7e00';
    if (aqi <= 200) return '#ff0000';
    if (aqi <= 300) return '#8f3f97';
    return '#7e0023';
  };

  const getRainIcon = (probability) => {
    if (probability < 30) return '☀️';
    if (probability < 60) return '⛅';
    return '🌧️';
  };

  // Generate weather condition comments based on thresholds
  const getWeatherComments = (data) => {
    const comments = [];
    
    // Very Hot
    if (data.temperature_max >= thresholds.veryHotTemp) {
      comments.push({
        type: 'warning',
        icon: '🔥',
        title: 'Very Hot',
        message: `Max temperature ${data.temperature_max}°C exceeds ${thresholds.veryHotTemp}°C threshold`
      });
    }
    
    // Very Cold
    if (data.temperature_min <= thresholds.veryColdTemp) {
      comments.push({
        type: 'warning',
        icon: '❄️',
        title: 'Very Cold',
        message: `Min temperature ${data.temperature_min}°C is below ${thresholds.veryColdTemp}°C threshold`
      });
    }
    
    // Very Windy
    if (data.wind_speed >= thresholds.veryWindy) {
      comments.push({
        type: 'warning',
        icon: '💨',
        title: 'Very Windy',
        message: `Wind speed ${data.wind_speed} m/s exceeds ${thresholds.veryWindy} m/s threshold`
      });
    }
    
    // Very Wet
    if (data.humidity >= thresholds.veryWet) {
      comments.push({
        type: 'info',
        icon: '💧',
        title: 'Very Wet',
        message: `High humidity at ${data.humidity}% (threshold: ${thresholds.veryWet}%)`
      });
    }
    
    // Very Uncomfortable - Heat Index
    if (data.heat_index >= thresholds.uncomfortableHeat) {
      comments.push({
        type: 'danger',
        icon: '🥵',
        title: 'Very Uncomfortable (Heat)',
        message: `Heat index ${data.heat_index}°C exceeds comfort threshold of ${thresholds.uncomfortableHeat}°C`
      });
    }
    
    // Very Uncomfortable - Wind Chill
    if (data.wind_chill <= thresholds.uncomfortableWind) {
      comments.push({
        type: 'danger',
        icon: '🥶',
        title: 'Very Uncomfortable (Cold)',
        message: `Wind chill ${data.wind_chill}°C is below comfort threshold of ${thresholds.uncomfortableWind}°C`
      });
    }
    
    // If no warnings, add a positive comment
    if (comments.length === 0) {
      comments.push({
        type: 'success',
        icon: '✅',
        title: 'Pleasant Conditions',
        message: 'All weather parameters are within comfortable ranges'
      });
    }
    
    return comments;
  };

  // Generate precautions based on weather conditions
  const getWeatherPrecautions = (data) => {
    const precautions = [];
    
    // High Rain Probability
    if (data.rain_probability >= 60) {
      precautions.push({
        icon: '☔',
        title: 'Rain Expected',
        items: [
          'Carry an umbrella or raincoat',
          'Wear waterproof footwear',
          'Allow extra travel time',
          'Keep electronics protected'
        ]
      });
    }
    
    // Hot Weather
    if (data.temperature_max >= 32 || data.heat_index >= 35) {
      precautions.push({
        icon: '🌡️',
        title: 'Extreme Heat',
        items: [
          'Stay hydrated - drink plenty of water',
          'Wear light, loose-fitting clothing',
          'Apply sunscreen (SPF 30+)',
          'Avoid outdoor activities 11 AM - 3 PM',
          'Wear a hat and sunglasses',
          'Seek shade whenever possible'
        ]
      });
    }
    
    // Cold Weather
    if (data.temperature_min <= 5 || data.wind_chill <= 5) {
      precautions.push({
        icon: '🧥',
        title: 'Cold Weather',
        items: [
          'Wear warm layers of clothing',
          'Cover head, hands, and feet',
          'Wear a jacket or coat',
          'Limit time outdoors',
          'Watch for signs of hypothermia'
        ]
      });
    }
    
    // High Humidity
    if (data.humidity >= 70) {
      precautions.push({
        icon: '💧',
        title: 'High Humidity',
        items: [
          'Wear breathable, moisture-wicking fabrics',
          'Stay in air-conditioned spaces when possible',
          'Drink water frequently',
          'Take breaks in cool areas'
        ]
      });
    }
    
    // Windy Conditions
    if (data.wind_speed >= 15) {
      precautions.push({
        icon: '🌬️',
        title: 'Strong Winds',
        items: [
          'Secure loose objects',
          'Be cautious of falling debris',
          'Avoid using umbrellas',
          'Drive carefully if traveling'
        ]
      });
    }
    
    // Poor Air Quality
    if (data.aqi >= 100) {
      precautions.push({
        icon: '😷',
        title: 'Poor Air Quality',
        items: [
          'Wear a mask (N95 or equivalent)',
          'Limit outdoor physical activities',
          'Keep windows closed',
          'Use air purifiers indoors',
          'Sensitive groups should stay indoors'
        ]
      });
    }
    
    // Monsoon Season
    if (data.season === 'Monsoon') {
      precautions.push({
        icon: '🌧️',
        title: 'Monsoon Season',
        items: [
          'Avoid waterlogged areas',
          'Be cautious of slippery surfaces',
          'Keep emergency contacts handy',
          'Check weather updates regularly'
        ]
      });
    }
    
    // General Good Weather
    if (precautions.length === 0) {
      precautions.push({
        icon: '✨',
        title: 'Pleasant Weather',
        items: [
          'Great day for outdoor activities!',
          'Stay hydrated',
          'Enjoy your day out',
          'No special precautions needed'
        ]
      });
    }
    
    return precautions;
  };

  const handleThresholdChange = (key, value) => {
    setThresholds(prev => ({
      ...prev,
      [key]: parseFloat(value)
    }));
  };

  // Get today's date in YYYY-MM-DD format for min date
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌍 Weather Prediction App</h1>
        <p>Select a location and date to predict weather conditions</p>
      </header>

      <div className="main-container">
        <div className="left-panel">
          <div className="search-container">
            <h2>🔍 Search Location</h2>
            <form onSubmit={handleSearchLocation} className="search-form">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter city name (e.g., New Delhi, London, Tokyo)"
                className="search-input"
                disabled={searchLoading}
              />
              <button 
                type="submit" 
                className="search-button"
                disabled={searchLoading}
              >
                {searchLoading ? '🔄 Searching...' : '🔍 Search'}
              </button>
            </form>
          </div>

          <div className="divider">
            <span>OR</span>
          </div>

          <div className="map-container">
            <h2>Click on Map</h2>
            <MapContainer
              center={position ? [position.lat, position.lng] : [20, 0]}
              zoom={position ? 10 : 2}
              style={{ height: '400px', width: '100%', borderRadius: '12px' }}
              key={position ? `${position.lat}-${position.lng}` : 'default'}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <LocationMarker position={position} setPosition={setPosition} />
            </MapContainer>
            {position && (
              <div className="coordinates">
                <p>
                  📍 Selected: {position.lat.toFixed(4)}°, {position.lng.toFixed(4)}°
                </p>
              </div>
            )}
          </div>

          <div className="date-selector">
            <h2>Select Date</h2>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min={today}
              className="date-input"
            />
          </div>

          <button
            onClick={handlePredict}
            disabled={loading || !position || !date}
            className="predict-button"
          >
            {loading ? '🔄 Predicting...' : '🔮 Predict Weather'}
          </button>

          {error && <div className="error-message">⚠️ {error}</div>}

          <div className="settings-section">
            <button 
              className="settings-toggle"
              onClick={() => setShowSettings(!showSettings)}
            >
              ⚙️ {showSettings ? 'Hide' : 'Show'} Threshold Settings
            </button>
            
            {showSettings && (
              <div className="threshold-settings">
                <h3>Weather Thresholds</h3>
                <div className="threshold-grid">
                  <div className="threshold-item">
                    <label>🔥 Very Hot (°C):</label>
                    <input
                      type="number"
                      value={thresholds.veryHotTemp}
                      onChange={(e) => handleThresholdChange('veryHotTemp', e.target.value)}
                    />
                  </div>
                  <div className="threshold-item">
                    <label>❄️ Very Cold (°C):</label>
                    <input
                      type="number"
                      value={thresholds.veryColdTemp}
                      onChange={(e) => handleThresholdChange('veryColdTemp', e.target.value)}
                    />
                  </div>
                  <div className="threshold-item">
                    <label>💨 Very Windy (m/s):</label>
                    <input
                      type="number"
                      value={thresholds.veryWindy}
                      onChange={(e) => handleThresholdChange('veryWindy', e.target.value)}
                    />
                  </div>
                  <div className="threshold-item">
                    <label>💧 Very Wet (%):</label>
                    <input
                      type="number"
                      value={thresholds.veryWet}
                      onChange={(e) => handleThresholdChange('veryWet', e.target.value)}
                    />
                  </div>
                  <div className="threshold-item">
                    <label>🥵 Heat Index (°C):</label>
                    <input
                      type="number"
                      value={thresholds.uncomfortableHeat}
                      onChange={(e) => handleThresholdChange('uncomfortableHeat', e.target.value)}
                    />
                  </div>
                  <div className="threshold-item">
                    <label>🥶 Wind Chill (°C):</label>
                    <input
                      type="number"
                      value={thresholds.uncomfortableWind}
                      onChange={(e) => handleThresholdChange('uncomfortableWind', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="right-panel">
          <h2>Prediction Results</h2>
          {prediction ? (
            <div className="results">
              <div className="result-card rain-card">
                <div className="result-icon">{getRainIcon(prediction.rain_probability)}</div>
                <div className="result-content">
                  <h3>Rain Probability</h3>
                  <p className="result-value">{prediction.rain_probability}%</p>
                  <p className="result-subtext">
                    {prediction.season === 'Monsoon' && '🌧️ High rain expected (Monsoon season)'}
                    {prediction.season === 'Summer' && '☀️ Low rain expected (Summer season)'}
                    {prediction.season === 'Winter' && '⛅ Moderate rain expected (Winter season)'}
                  </p>
                  <div className="progress-bar">
                    <div
                      className="progress-fill rain-fill"
                      style={{ width: `${prediction.rain_probability}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="result-card temp-card">
                <div className="result-icon">🌡️</div>
                <div className="result-content">
                  <h3>Temperature</h3>
                  <p className="result-value">{prediction.temperature}°C</p>
                  <p className="result-subtext">
                    {prediction.temperature > 30
                      ? 'Hot'
                      : prediction.temperature > 20
                      ? 'Warm'
                      : prediction.temperature > 10
                      ? 'Mild'
                      : 'Cold'}
                  </p>
                </div>
              </div>

              <div className="result-card aqi-card">
                <div className="result-icon">💨</div>
                <div className="result-content">
                  <h3>Air Quality Index</h3>
                  <p className="result-value" style={{ color: getAQIColor(prediction.aqi) }}>
                    {prediction.aqi}
                  </p>
                  <p className="result-subtext">{prediction.aqi_category}</p>
                  <div className="aqi-scale">
                    <div className="aqi-marker" style={{ left: `${(prediction.aqi / 500) * 100}%` }}></div>
                  </div>
                </div>
              </div>

              <div className="result-card details-card">
                <h3>Additional Details</h3>
                <div className="details-grid">
                  <div className="detail-item">
                    <span className="detail-label">🌡️ Max Temp:</span>
                    <span className="detail-value">{prediction.temperature_max}°C</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">🌡️ Min Temp:</span>
                    <span className="detail-value">{prediction.temperature_min}°C</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">💧 Humidity:</span>
                    <span className="detail-value">{prediction.humidity}%</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">💨 Wind Speed:</span>
                    <span className="detail-value">{prediction.wind_speed} m/s</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">🥵 Heat Index:</span>
                    <span className="detail-value">{prediction.heat_index}°C</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">🥶 Wind Chill:</span>
                    <span className="detail-value">{prediction.wind_chill}°C</span>
                  </div>
                </div>
              </div>

              <div className="seasonal-info-card">
                <h3>🌤️ Seasonal Weather Pattern</h3>
                <div className="seasonal-details">
                  <div className="seasonal-item">
                    <span className="seasonal-label">Current Season:</span>
                    <span className="seasonal-value">
                      {prediction.season === 'Monsoon' && '🌧️ Monsoon (June-October)'}
                      {prediction.season === 'Summer' && '☀️ Summer (March-May)'}
                      {prediction.season === 'Winter' && '❄️ Winter (November-February)'}
                    </span>
                  </div>
                  <div className="seasonal-item">
                    <span className="seasonal-label">Expected Rain:</span>
                    <span className="seasonal-value">
                      {prediction.season === 'Monsoon' && '🌧️ High (60-90% probability)'}
                      {prediction.season === 'Summer' && '☀️ Low (5-25% probability)'}
                      {prediction.season === 'Winter' && '⛅ Moderate (20-40% probability)'}
                    </span>
                  </div>
                  <div className="seasonal-item">
                    <span className="seasonal-label">Temperature Range:</span>
                    <span className="seasonal-value">
                      {prediction.season === 'Monsoon' && '25-30°C'}
                      {prediction.season === 'Summer' && '30-43°C'}
                      {prediction.season === 'Winter' && '18-25°C'}
                    </span>
                  </div>
                  <div className="seasonal-item">
                    <span className="seasonal-label">Humidity Level:</span>
                    <span className="seasonal-value">
                      {prediction.season === 'Monsoon' && '💧 High (70-95%)'}
                      {prediction.season === 'Summer' && '🏜️ Low (30-50%)'}
                      {prediction.season === 'Winter' && '💨 Moderate (40-65%)'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="weather-comments">
                <h3>⚠️ Weather Conditions</h3>
                {getWeatherComments(prediction).map((comment, index) => (
                  <div key={index} className={`comment-card comment-${comment.type}`}>
                    <div className="comment-icon">{comment.icon}</div>
                    <div className="comment-content">
                      <h4>{comment.title}</h4>
                      <p>{comment.message}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="precautions-section">
                <h3>🎒 Precautions Before Going Out</h3>
                {getWeatherPrecautions(prediction).map((precaution, index) => (
                  <div key={index} className="precaution-card">
                    <div className="precaution-header">
                      <span className="precaution-icon">{precaution.icon}</span>
                      <h4>{precaution.title}</h4>
                    </div>
                    <ul className="precaution-list">
                      {precaution.items.map((item, itemIndex) => (
                        <li key={itemIndex}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>

              <div className="prediction-meta">
                <p>📅 Date: {prediction.date}</p>
                <p>🌤️ Season: <strong>{prediction.season}</strong></p>
                <p>
                  📍 Location: {prediction.location.latitude.toFixed(2)}°,{' '}
                  {prediction.location.longitude.toFixed(2)}°
                </p>
                {prediction.nasa_data && (
                  <p className="nasa-badge">
                    🛰️ <strong>NASA POWER API Data</strong> - 10-year historical average
                  </p>
                )}
                {!prediction.nasa_data && (
                  <p className="fallback-badge">
                    📊 Seasonal Pattern Data
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <p>Select a location and date, then click "Predict Weather" to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

