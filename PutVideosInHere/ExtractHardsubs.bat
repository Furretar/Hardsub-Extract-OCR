@echo off
setlocal enabledelayedexpansion

REM Set crop values, default (for Muse) L 0.15, R 0.85, T 0.19, B 0.02, (Bilibili) L 0.10, R 0.90, T 0.20, B 0.03
set CROP_LEFT=0.10
set CROP_RIGHT=0.90
set CROP_TOP=0.20
set CROP_BOTTOM=0.03

REM Set the path to VideoSubFinder
set VIDEOSUBFINDER_PATH="..\Release_x64\VideoSubFinderWXW.exe"

REM Set the video folder path
set VIDEOS_FOLDER=.

REM Set output folder
set OUTPUT_FOLDER=%VIDEOS_FOLDER%\output
if not exist %OUTPUT_FOLDER% (
    mkdir %OUTPUT_FOLDER%
)

REM Process each video file
for %%f in ("%VIDEOS_FOLDER%\*.mp4" "%VIDEOS_FOLDER%\*.mkv") do (
    echo Processing %%~nxf
    set VIDEO_FILE="%%f"
    set OUTPUT_FILE="%OUTPUT_FOLDER%\%%~nf"
    
    REM Run VideoSubFinder with binarization adjustments
    start /wait "" %VIDEOSUBFINDER_PATH% -c -r -ccti -i !VIDEO_FILE! -o !OUTPUT_FILE! -te %CROP_TOP% -be %CROP_BOTTOM% -le %CROP_LEFT% -re %CROP_RIGHT% -s 0:00:0:300 --use_cuda     
    REM Check success
    if errorlevel 1 (
        echo Failed to process !VIDEO_FILE!
    ) else (
        echo Successfully processed !VIDEO_FILE!
    )
)

echo All videos processed.
pause
