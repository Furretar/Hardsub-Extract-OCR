@echo off
setlocal enabledelayedexpansion

REM Set the path to the VideoSubFinder executable
set VIDEOSUBFINDER_PATH="C:\Program Files\videosubfinder\VideoSubFinderWXW.exe"

REM Set the path to the folder containing the videos
set VIDEOS_FOLDER=.

REM Set the path to the output folder in the working directory
set OUTPUT_FOLDER=%VIDEOS_FOLDER%\output

REM Ensure the output folder exists
if not exist %OUTPUT_FOLDER% (
    mkdir %OUTPUT_FOLDER%
)

REM Iterate over each video file in the videos folder with .mp4 or .mkv extension
for %%f in ("%VIDEOS_FOLDER%\*.mp4" "%VIDEOS_FOLDER%\*.mkv") do (
    echo Processing %%~nxf
    set VIDEO_FILE="%%f"
    set OUTPUT_FILE="%OUTPUT_FOLDER%\%%~nf"
    
    REM Run VideoSubFinder CLI for the current video file, le = cropped off left, re = cropped off right, te = cropped off top, be = cropped off bottom
    start /wait "" %VIDEOSUBFINDER_PATH% -c -r -ccti -i !VIDEO_FILE! -o !OUTPUT_FILE! -te 0.20 -be 0.05 -le 0.15 -re 0.85 -s 0:00:0:300 --use_cuda
    
    REM Check if the command succeeded
    if errorlevel 1 (
        echo Failed to process !VIDEO_FILE!
    ) else (
        echo Successfully processed !VIDEO_FILE!
    )
)

echo All videos processed.
pause
