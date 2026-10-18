@echo off
title LLM Router Dashboard Runner
cls
echo ==============================================================================
echo                 LLM Router Dashboard — Starting Containers
echo ==============================================================================
echo.

docker compose up -d

echo.
echo ==============================================================================
echo                          Application is ONLINE!
echo ==============================================================================
echo.
echo   [1] Local Browser (Your PC):
echo       http://localhost:3000
echo.
echo   [2] Other Devices on the Same Wi-Fi (Phone, Laptop):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    echo       http:%%a:3000
)
echo.
echo   [3] Backend OpenAPI Documentation:
echo       http://localhost:8000/docs
echo.
echo ==============================================================================
echo   To generate a FREE Public Internet Link for external friends:
echo   Run: docker compose --profile tunnel up -d
echo   Then view link with: docker compose logs tunnel
echo ==============================================================================
echo.
echo Opening dashboard in your default browser...
start http://localhost:3000
pause
