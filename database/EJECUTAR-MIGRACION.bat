@echo off
chcp 65001 >nul
echo ============================================================
echo   MIGRACIÓN DE BASE DE DATOS - AI PRINT STUDIO
echo ============================================================
echo.
echo Este script ejecutará la migración completa de PrendeteRock
echo.
echo IMPORTANTE:
echo   - Se creará un backup automático antes de comenzar
echo   - La migración puede tardar 5-10 minutos
echo   - Cierra todas las aplicaciones que usen la base de datos
echo.
pause
echo.
echo Ejecutando migración...
echo.

cd /d "%~dp0"
python ejecutar-migracion.py

echo.
echo ============================================================
echo   Presiona cualquier tecla para cerrar...
echo ============================================================
pause >nul
