@echo off
echo ==============================================================================
echo  Iniciando Google Chrome con Depuracion Remota en Puerto 9222
echo  (Permite a Playwright interactuar con tu sesion activa de Azure sin re-login)
echo ==============================================================================

:: Si Chrome ya esta en ejecucion sin puerto de depuracion, se recomienda cerrarlo primero
:: o usar un directorio de perfil temporal con tus credenciales.
tasklist /fi "imagename eq chrome.exe" | findstr /i "chrome.exe" >nul
if %errorlevel% equ 0 (
    echo [AVISO] Se detectaron procesos de Google Chrome abiertos.
    echo Para que el puerto de depuracion 9222 se active correctamente,
    echo se iniciara una instancia conectable.
)

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --restore-last-session "https://portal.azure.com"

echo.
echo Google Chrome iniciado con --remote-debugging-port=9222.
echo Ahora puedes ejecutar:
echo python automation\document_azure_setup.py --mode cdp
echo.
pause
