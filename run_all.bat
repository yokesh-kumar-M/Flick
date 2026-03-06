@echo off
echo ============================================
echo    Flick - Starting All Services
echo ============================================
echo.

:: Start each service in its own terminal
start "Flick - Auth :8001" cmd /k "cd /d %~dp0auth_service && python manage.py runserver 0.0.0.0:8001"
start "Flick - Catalog :8002" cmd /k "cd /d %~dp0catalog_service && python manage.py runserver 0.0.0.0:8002"
start "Flick - Access :8003" cmd /k "cd /d %~dp0access_service && python manage.py runserver 0.0.0.0:8003"
start "Flick - Streaming :8004" cmd /k "cd /d %~dp0streaming_service && python manage.py runserver 0.0.0.0:8004"
start "Flick - Recommendation :8005" cmd /k "cd /d %~dp0recommendation_service && python manage.py runserver 0.0.0.0:8005"
start "Flick - Notification :8006" cmd /k "cd /d %~dp0notification_service && python manage.py runserver 0.0.0.0:8006"

:: Wait a moment for services to start
timeout /t 3 /nobreak > nul

:: Start Gateway last
start "Flick - Gateway :8000" cmd /k "cd /d %~dp0gateway && python manage.py runserver 0.0.0.0:8000"

echo.
echo All services starting...
echo.
echo   Gateway:        http://localhost:8000
echo   Auth Service:   http://localhost:8001
echo   Catalog:        http://localhost:8002
echo   Access:         http://localhost:8003
echo   Streaming:      http://localhost:8004
echo   Recommendation: http://localhost:8005
echo   Notification:   http://localhost:8006
echo.
echo Press any key to exit this window...
pause > nul
