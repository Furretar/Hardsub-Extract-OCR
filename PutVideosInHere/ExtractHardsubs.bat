@echo off
setlocal enabledelayedexpansion

REM Set crop values
set CROP_LEFT=0.15
set CROP_RIGHT=0.85
set CROP_TOP=0.20
set CROP_BOTTOM=0.05

REM Set the path to the VideoSubFinder executable
set VIDEOSUBFINDER_PATH="..\Release_x64\VideoSubFinderWXW.exe"

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
    
    REM Run VideoSubFinder CLI for the current video file, using the crop values
    start /wait "" %VIDEOSUBFINDER_PATH% -c -r -ccti -i !VIDEO_FILE! -o !OUTPUT_FILE! -te %CROP_TOP% -be %CROP_BOTTOM% -le %CROP_LEFT% -re %CROP_RIGHT% -s 0:00:0:300 --use_cuda
   
    REM Check if the command succeeded
    if errorlevel 1 (
        echo Failed to process !VIDEO_FILE!
    ) else (
        echo Successfully processed !VIDEO_FILE!
    )
)

echo All videos processed.
pause
