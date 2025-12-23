@echo off
setlocal DISABLEDELAYEDEXPANSION

REM Set crop values, default (for Muse) L 0.15, R 0.85, T 0.19, B 0.02, (Bilibili) L 0.10, R 0.90, T 0.20, B 0.03
set "CROP_LEFT=0.10"
set "CROP_RIGHT=0.90"
set "CROP_TOP=0.20"
set "CROP_BOTTOM=0.03"

REM Set the path to VideoSubFinder (no surrounding quotes in the value)
set "VIDEOSUBFINDER_PATH=..\Release_x64\VideoSubFinderWXW.exe"

REM Set the video folder path
set "VIDEOS_FOLDER=."

REM Set output folder
set "OUTPUT_FOLDER=%VIDEOS_FOLDER%\output"
if not exist "%OUTPUT_FOLDER%" (
    mkdir "%OUTPUT_FOLDER%"
)

REM Process each video file (use FOR variables directly so '!' in names is preserved)
for %%f in ("%VIDEOS_FOLDER%\*.mp4" "%VIDEOS_FOLDER%\*.mkv") do (
    echo Processing "%%~nxf"
    start /wait "" "%VIDEOSUBFINDER_PATH%" -c -r -ccti -i "%%~f" -o "%OUTPUT_FOLDER%\%%~nf" -te %CROP_TOP% -be %CROP_BOTTOM% -le %CROP_LEFT% -re %CROP_RIGHT% -s 0:00:0:300 --use_cuda
    if errorlevel 1 (
        echo Failed to process "%%~f"
    ) else (
        echo Successfully processed "%%~f"
    )
)

echo All videos processed.
pause
