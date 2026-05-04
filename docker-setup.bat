@echo off
REM Docker setup script for IPL Playoff Predictor Backend (Windows)

echo.
echo ======================================
echo 🐳 IPL Playoff Predictor - Docker Setup
echo ======================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop for Windows.
    echo    Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker is installed
echo.

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t ipl-predictor:latest .

if errorlevel 1 (
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

echo.
echo ✅ Docker image built successfully!
echo.

REM Option to run the container
set /p start_container="Do you want to start the container now? (y/n): "

if /i "%start_container%"=="y" (
    echo.
    echo 🚀 Starting container with docker-compose...
    docker-compose up -d
    
    if errorlevel 1 (
        echo ❌ Failed to start container
        pause
        exit /b 1
    )
    
    echo.
    echo ✅ Container is running!
    echo.
    echo 📋 Quick Commands:
    echo    View logs:    docker-compose logs -f
    echo    Stop:         docker-compose down
    echo    Restart:      docker-compose restart
    echo.
    echo 🌐 Test the API:
    echo    Health:       curl http://localhost:8000/health
    echo    Probabilities: curl http://localhost:8000/probabilities
)

echo.
echo ✨ Setup complete!
pause
