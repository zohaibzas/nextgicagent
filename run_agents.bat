@echo off
title Nextgic Product Agent
echo ===================================================
echo Starting Nextgic Product Agent Services...
echo ===================================================

:: Ensure python packages are loaded
echo Checking Python dependencies...
python -c "import fastapi, uvicorn, openai, WooCommerce, rapidfuzz, PIL, psd_tools" 2>nul
if %errorlevel% neq 0 (
    echo Python dependencies are missing. Installing them now...
    pip install -r requirements.txt
)

:: Start Python Backend in a separate background window
echo Starting FastAPI Backend (Port 8000)...
start "Nextgic Backend" /min python -m uvicorn main:app --host 0.0.0.0 --port 8000

:: Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak >nul

:: Check if backend is running
curl -s http://localhost:8000/health >nul
if %errorlevel% neq 0 (
    echo [WARNING] Backend health check did not respond yet. It might still be starting.
)

:: Start WhatsApp Bot in the current window (logs and QR code will show here)
echo Starting WhatsApp Bot...
cd whatsapp
node bot.js

pause
