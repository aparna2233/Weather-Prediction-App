# 🚀 Quick Start Guide (Windows)

## Automated Setup (Recommended)

### Backend Setup
1. Open Command Prompt or PowerShell
2. Navigate to the backend folder:
   ```bash
   cd backend
   ```
3. Run the setup script:
   ```bash
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install all Python dependencies
   - Generate training data
   - Train the ML models

### Frontend Setup
1. Open a new Command Prompt or PowerShell
2. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
3. Run the setup script:
   ```bash
   setup.bat
   ```
   This will install all Node.js dependencies

## Running the Application

### Step 1: Start Backend Server
In the backend folder, run:
```bash
run.bat
```
The backend will start at `http://localhost:5000`

### Step 2: Start Frontend
In a new terminal, in the frontend folder, run:
```bash
run.bat
```
The app will open automatically in your browser at `http://localhost:3000`

## Manual Setup (Alternative)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py
python train_model.py
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Using the App

1. **Click on the map** to select a location
2. **Select a date** using the date picker
3. **Click "Predict Weather"** to get your forecast
4. View the results:
   - 🌧️ Rain probability percentage
   - 🌡️ Predicted temperature
   - 💨 Air Quality Index with category

## Troubleshooting

### Backend Issues
- **"Python not found"**: Make sure Python 3.8+ is installed and in PATH
- **"Module not found"**: Run `pip install -r requirements.txt` again
- **Port 5000 in use**: Change the port in `app.py` (last line)

### Frontend Issues
- **"npm not found"**: Install Node.js from nodejs.org
- **"Port 3000 in use"**: The app will prompt you to use a different port
- **Map not loading**: Check your internet connection (requires OpenStreetMap tiles)

### Connection Issues
- Make sure both backend and frontend are running
- Backend should be at `http://localhost:5000`
- Frontend will connect to backend automatically

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Customize the models by modifying `train_model.py`
- Adjust the UI styling in `frontend/src/App.css`
- Add more features based on your requirements

Enjoy predicting the weather! 🌤️

