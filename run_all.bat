@echo off
echo Starting Flick Platform...
echo =========================
echo This will start all microservices and infrastructure components
echo Ensure Docker Desktop is running before continuing.
echo.

docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.es.yml up --build -d

echo.
echo Flick is now starting up in the background!
echo - Gateway/Frontend: http://localhost:8000
echo - Elasticsearch: http://localhost:9200
echo - Redis: localhost:6379
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
pause
