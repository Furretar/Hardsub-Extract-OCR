@echo off
for %%F in (*.sup) do (
    setlocal enabledelayedexpansion
    set "folder=%%~nF"
    mkdir "%%~dpF!folder!\TXTImages"
    java -jar BDSup2Sub.jar "%%F" -o "%%~dpF!folder!\TXTImages\%%~nF.xml"
    endlocal
)
pause