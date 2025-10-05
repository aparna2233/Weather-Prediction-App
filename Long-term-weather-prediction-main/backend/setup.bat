@echo off
echo ====================================
echo Weather Prediction Backend Setup
echo ====================================
echo.

echo Creating virtual environment...
python -m venv venv
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Generating training data...
python generate_data.py
echo.

echo Training ML models...
python train_model.py
echo.

echo ====================================
echo Setup complete!
echo ====================================
echo.
echo To start the server, run:
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
pause

