@echo off
echo ============================================
echo    Flick - Enterprise Streaming Platform
echo    Setup Script
echo ============================================
echo.

:: Navigate to project root
cd /d "%~dp0"

:: Auth Service
echo [1/7] Setting up Auth Service...
cd auth_service
python manage.py makemigrations authentication 2>nul
python manage.py migrate
python manage.py seed_users
cd ..
echo.

:: Catalog Service
echo [2/7] Setting up Catalog Service...
cd catalog_service
python manage.py makemigrations catalog 2>nul
python manage.py migrate
python manage.py seed_catalog
cd ..
echo.

:: Access Service
echo [3/7] Setting up Access Service...
cd access_service
python manage.py makemigrations access 2>nul
python manage.py migrate
cd ..
echo.

:: Streaming Service
echo [4/7] Setting up Streaming Service...
cd streaming_service
python manage.py makemigrations streaming 2>nul
python manage.py migrate
cd ..
echo.

:: Recommendation Service
echo [5/7] Setting up Recommendation Service...
cd recommendation_service
python manage.py makemigrations recommendations 2>nul
python manage.py migrate
cd ..
echo.

:: Notification Service
echo [6/7] Setting up Notification Service...
cd notification_service
python manage.py makemigrations notifications 2>nul
python manage.py migrate
cd ..
echo.

:: Gateway
echo [7/7] Setting up Gateway...
cd gateway
python manage.py migrate
cd ..
echo.

echo ============================================
echo    Setup Complete!
echo.
echo    Credentials:
echo      Admin: admin / Admin123!
echo      Users: alice / Alice123!
echo             bob / Bobby123!
echo             charlie / Charlie123!
echo.
echo    To run all services:
echo      run_all.bat
echo.
echo    Or with Docker:
echo      docker-compose up --build
echo ============================================
