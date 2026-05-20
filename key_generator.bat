@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Woo Product Generator - Lisans Olusturucu
color 0A

cd /d %~dp0

if not exist "licenses" mkdir licenses

if not exist "tools\private_key.pem" (
    echo.
    echo [HATA] tools\private_key.pem bulunamadi.
    echo Once anahtar ciftini olusturman gerekiyor.
    echo.
    pause
    exit /b 1
)

if exist "venv\Scripts\python.exe" (
    set "PYTHON=venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

:menu
cls
echo ==================================================
echo        WOO PRODUCT GENERATOR - LISANS PANELI
echo ==================================================
echo.
echo 1 ^) 30 Gun
echo 2 ^) 90 Gun
echo 3 ^) 180 Gun
echo 4 ^) 1 Yil
echo 5 ^) Cikis
echo.
set /p choice=Secim yapin (1-5): 

if "%choice%"=="1" (
    set "DAYS=30"
    set "PLAN=monthly"
    goto ask_customer
)

if "%choice%"=="2" (
    set "DAYS=90"
    set "PLAN=quarterly"
    goto ask_customer
)

if "%choice%"=="3" (
    set "DAYS=180"
    set "PLAN=semiannual"
    goto ask_customer
)

if "%choice%"=="4" (
    set "DAYS=365"
    set "PLAN=yearly"
    goto ask_customer
)

if "%choice%"=="5" exit /b 0

echo.
echo Gecersiz secim.
timeout /t 2 >nul
goto menu

:ask_customer
cls
echo ==================================================
echo        WOO PRODUCT GENERATOR - LISANS OLUSTR
echo ==================================================
echo.
echo Secilen sure: !DAYS! gun
echo Plan: !PLAN!
echo.
set /p CUSTOMER=Musteri adi girin: 

if "%CUSTOMER%"=="" (
    echo.
    echo Musteri adi bos olamaz.
    timeout /t 2 >nul
    goto ask_customer
)

set "SAFE_CUSTOMER=%CUSTOMER%"
set "SAFE_CUSTOMER=%SAFE_CUSTOMER: =_%"
set "SAFE_CUSTOMER=%SAFE_CUSTOMER:/=_%"
set "SAFE_CUSTOMER=%SAFE_CUSTOMER:\=_%"
set "SAFE_CUSTOMER=%SAFE_CUSTOMER::=_%"
set "SAFE_CUSTOMER=%SAFE_CUSTOMER:|=_%"

set "OUTPUT=licenses\%SAFE_CUSTOMER%_%DAYS%gun.key"

echo.
echo Lisans olusturuluyor...
echo Musteri: %CUSTOMER%
echo Sure: %DAYS% gun
echo Cikti: %OUTPUT%
echo.

%PYTHON% -m app_license.license_generator issue ^
    --private tools/private_key.pem ^
    --customer "%CUSTOMER%" ^
    --plan %PLAN% ^
    --days %DAYS% ^
    --output "%OUTPUT%"

if errorlevel 1 (
    echo.
    echo [HATA] Lisans olusturulamadi.
    pause
    goto menu
)

echo.
echo [OK] Lisans basariyla olusturuldu:
echo %OUTPUT%
echo.
choice /c OC /m "O = klasoru ac, C = devam et"
if errorlevel 2 goto menu
if errorlevel 1 start "" "%cd%\licenses"
goto menu