"""
Enhanced Backend Setup Script
Automates the setup process for the NASA Weather Prediction Dashboard backend.
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step_num, text):
    """Print formatted step."""
    print(f"\n[{step_num}] {text}")

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"    Running: {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"    ✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ✗ {description} failed")
        print(f"    Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is adequate."""
    print_step("1", "Checking Python Version")
    
    version = sys.version_info
    print(f"    Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"    ✗ Python 3.8 or higher is required")
        return False
    
    print(f"    ✓ Python version is adequate")
    return True

def install_dependencies():
    """Install required Python packages."""
    print_step("2", "Installing Dependencies")
    
    if not Path("requirements.txt").exists():
        print("    ✗ requirements.txt not found")
        return False
    
    print("    This may take a few minutes...")
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Package installation"
    )

def generate_sample_data():
    """Generate synthetic training data."""
    print_step("3", "Generating Sample Data")
    
    if not Path("generate_data.py").exists():
        print("    ✗ generate_data.py not found")
        return False
    
    if Path("weather_data.csv").exists():
        print("    ℹ weather_data.csv already exists, skipping...")
        return True
    
    return run_command(
        f"{sys.executable} generate_data.py",
        "Data generation"
    )

def train_models():
    """Train ML models."""
    print_step("4", "Training ML Models")
    
    if not Path("train_model.py").exists():
        print("    ✗ train_model.py not found")
        return False
    
    models_exist = all([
        Path("rain_model.pkl").exists(),
        Path("temperature_model.pkl").exists(),
        Path("aqi_model.pkl").exists(),
        Path("scaler.pkl").exists()
    ])
    
    if models_exist:
        print("    ℹ Models already exist, skipping training...")
        print("    (Delete .pkl files to retrain)")
        return True
    
    print("    Training models (this may take a minute)...")
    return run_command(
        f"{sys.executable} train_model.py",
        "Model training"
    )

def test_imports():
    """Test if custom modules can be imported."""
    print_step("5", "Testing Module Imports")
    
    modules = [
        ("nasa_data", "NASA Data Fetcher"),
        ("location_service", "Location Service")
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"    ✓ {description} imported successfully")
        except ImportError as e:
            print(f"    ✗ Failed to import {description}")
            print(f"      Error: {e}")
            all_ok = False
    
    return all_ok

def create_test_script():
    """Create a simple test script."""
    print_step("6", "Creating Test Script")
    
    if Path("test_api.py").exists():
        print("    ✓ test_api.py already exists")
        return True
    
    print("    ✗ test_api.py not found")
    print("      Manual testing required")
    return True

def print_summary():
    """Print setup summary and next steps."""
    print_header("SETUP COMPLETE!")
    
    print("✓ Backend setup is complete\n")
    
    print("Next Steps:")
    print("\n1. Start the Enhanced API Server:")
    print("   python app_enhanced.py")
    print("\n   OR use the original API:")
    print("   python app.py")
    
    print("\n2. Test the API:")
    print("   python test_api.py")
    
    print("\n3. API will be available at:")
    print("   http://localhost:5000")
    
    print("\n4. Test endpoints:")
    print("   - Health check: http://localhost:5000/health")
    print("   - API docs: See BACKEND_IMPLEMENTATION_GUIDE.md")
    
    print("\n5. Frontend Integration:")
    print("   - Configure frontend to use http://localhost:5000")
    print("   - CORS is enabled for all origins")
    
    print("\nAvailable Files:")
    print("   - app_enhanced.py         : Full-featured API")
    print("   - app.py                  : Original simple API")
    print("   - nasa_data.py            : NASA data integration")
    print("   - location_service.py     : Location handling")
    print("   - test_api.py             : API testing script")
    print("   - BACKEND_IMPLEMENTATION_GUIDE.md : Full documentation")
    
    print("\n" + "="*60 + "\n")

def main():
    """Main setup routine."""
    print_header("NASA WEATHER PREDICTION DASHBOARD")
    print("Backend Setup Script\n")
    
    # Change to backend directory if needed
    if not Path("app.py").exists() and Path("backend/app.py").exists():
        os.chdir("backend")
        print("    Changed directory to: backend/")
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Generate Sample Data", generate_sample_data),
        ("Train ML Models", train_models),
        ("Test Module Imports", test_imports),
        ("Verify Test Script", create_test_script)
    ]
    
    results = []
    
    for name, func in steps:
        try:
            success = func()
            results.append((name, success))
            if not success and name in ["Python Version Check", "Install Dependencies"]:
                print(f"\n✗ Critical step failed: {name}")
                print("   Setup cannot continue")
                return False
        except Exception as e:
            print(f"\n✗ Error in step: {name}")
            print(f"   {str(e)}")
            results.append((name, False))
    
    # Print results
    print("\n" + "="*60)
    print("  SETUP RESULTS")
    print("="*60)
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\n  {passed}/{total} steps completed successfully")
    
    if passed == total:
        print_summary()
        return True
    else:
        print("\n⚠️  Some steps failed. Please review errors above.")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

