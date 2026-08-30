@echo off
title AI Trading Signal Terminal & Bot
echo ========================================================
echo   ALPHA SIGNAL AI - TRADING TERMINAL & ALERT BOT
echo ========================================================
echo.
echo Menjalankan backend server dan terminal...
echo URL Terminal: http://localhost:8000
echo.

start "" http://localhost:8000
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
