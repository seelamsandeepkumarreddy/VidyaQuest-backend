@echo off
echo Stopping all Python processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM python3.11.exe /T 2>nul
echo.
echo Starting RuralQuest Backend on Port 5001...

cd /d "C:\Users\sande\AndroidStudioProjects\ruralquest_backend"
python app.py
pause
