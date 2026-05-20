@echo off
cd /d %~dp0

where python >nul 2>nul
if errorlevel 1 (
    echo Python bulunamadi. Lutfen Python 3.11+ kurup PATH'e ekleyin.
    pause
    exit /b 1
)

if not exist .venv\Scripts\python.exe (
    echo Sanal ortam olusturuluyor...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m streamlit run app.py

pause
