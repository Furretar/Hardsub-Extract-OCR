@echo off
setlocal disabledelayedexpansion

REM Set crop values, default (for Muse) L 0.15, R 0.85, T 0.19, B 0.02, (Bilibili) L 0.10, R 0.90, T 0.20, B 0.03
set CROP_LEFT=0.10
set CROP_RIGHT=0.90
set CROP_TOP=0.20
set CROP_BOTTOM=0.03

set VIDEOSUBFINDER_PATH="..\Release_x64\VideoSubFinderWXW.exe"
set VIDEOS_FOLDER=.
set OUTPUT_FOLDER=%VIDEOS_FOLDER%\output

REM Process each video file
for %%f in ("%VIDEOS_FOLDER%\*.mp4" "%VIDEOS_FOLDER%\*.mkv") do (
    echo Processing %%~nxf
    set "VIDEO_FILE=%%f"
    set "OUTPUT_FILE=%OUTPUT_FOLDER%\%%~nf"

    start /wait "" %VIDEOSUBFINDER_PATH% -c -r -ccti -i "%%f" -o "%OUTPUT_FILE%" -te %CROP_TOP% -be %CROP_BOTTOM% -le %CROP_LEFT% -re %CROP_RIGHT% -s 0:00:0:300 --use_cuda

    if errorlevel 1 (
        echo Failed to process "%%f"
    ) else (
        echo Successfully processed "%%f"
    )
)

echo All videos processed.
pause

