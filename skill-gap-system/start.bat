@echo off
echo Starting Graduate Skill Gap Prediction System...
echo Note: Ensure Docker Desktop is running before starting.
docker-compose up -d --build
echo.
echo =======================================================
echo System started successfully!
echo.
echo Frontend URL: http://localhost:5501
echo Backend API Docs: http://localhost:8001/docs
echo =======================================================
echo.
echo Run stop.bat to shut down the system.
pause
