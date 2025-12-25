@echo off
REM Full pipeline script for The Obsolescence novel generation
REM Runs cleanup, image generation, audio generation, and video generation sequentially

setlocal enabledelayedexpansion

echo ================================================================================
echo The Obsolescence - Full Generation Pipeline
echo ================================================================================
echo.
echo This script will run the following steps:
echo   1. Cleanup all generated files
echo   2. Generate scene images
echo   3. Generate scene audio
echo   4. Generate video
echo.
echo WARNING: This will delete all existing generated files!
echo.

REM Get chapter selection ONCE at the beginning
set /p CHAPTERS="Enter chapter numbers to process (e.g., 1 2 3) or press Enter for all: "

echo.
if "%CHAPTERS%"=="" (
    echo Selected: ALL chapters
    set /p CONFIRM="Continue with full pipeline for ALL chapters? (y/N): "
) else (
    echo Selected: Chapters %CHAPTERS%
    set /p CONFIRM="Continue with full pipeline for chapters %CHAPTERS%? (y/N): "
)

if /i not "%CONFIRM%"=="y" (
    echo Pipeline cancelled.
    exit /b 0
)

echo.
echo Starting pipeline - will run to completion without further prompts...
echo.

echo ================================================================================
echo Step 1: Cleanup
echo ================================================================================
echo.

REM Run cleanup script with --yes flag to skip confirmation
..\venv\Scripts\python cleanup.py --yes

if !errorlevel! neq 0 (
    echo [ERROR] Cleanup failed with exit code !errorlevel!
    exit /b !errorlevel!
)

echo.
echo ================================================================================
echo Step 2: Generate Scene Images
echo ================================================================================
echo.

if "%CHAPTERS%"=="" (
    echo Generating images for all chapters...
    ..\venv\Scripts\python generate_scene_images.py
) else (
    echo Generating images for chapters: %CHAPTERS%
    ..\venv\Scripts\python generate_scene_images.py --chapters %CHAPTERS%
)

if !errorlevel! neq 0 (
    echo [ERROR] Image generation failed with exit code !errorlevel!
    exit /b !errorlevel!
)

echo.
echo ================================================================================
echo Step 3: Generate Scene Audio
echo ================================================================================
echo.

if "%CHAPTERS%"=="" (
    echo Generating audio for all chapters...
    ..\venv\Scripts\python generate_scene_audio.py
) else (
    echo Generating audio for chapters: %CHAPTERS%
    ..\venv\Scripts\python generate_scene_audio.py --chapters %CHAPTERS%
)

if !errorlevel! neq 0 (
    echo [ERROR] Audio generation failed with exit code !errorlevel!
    exit /b !errorlevel!
)

echo.
echo ================================================================================
echo Step 4: Generate Video
echo ================================================================================
echo.

if "%CHAPTERS%"=="" (
    echo Generating video for all chapters...
    ..\venv\Scripts\python generate_video.py --all
) else (
    echo Generating video for chapters: %CHAPTERS%
    ..\venv\Scripts\python generate_video.py --chapters %CHAPTERS%
)

if !errorlevel! neq 0 (
    echo [ERROR] Video generation failed with exit code !errorlevel!
    exit /b !errorlevel!
)

echo.
echo ================================================================================
echo Pipeline Complete!
echo ================================================================================
echo.
echo All steps completed successfully.
echo Generated files can be found in:
echo   - Images: ..\images\
echo   - Audio:  ..\audio\
echo   - Videos: ..\videos\
echo.

exit /b 0
