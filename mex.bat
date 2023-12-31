@echo off

set target=%1

if "%target%"=="install" goto install
if "%target%"=="test" goto test
echo invalid argument %target%
exit /b 1


:install
@REM install meta requirements system-wide
Python -m pip --disable-pip-version-check install --force-reinstall -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

@REM install pre-commit hooks when not in CI
if "%CI%"=="" (
    pre-commit install
    if %errorlevel% neq 0 exit /b %errorlevel%
)
exit /b 0


:test
@REM run the linter hooks from pre-commit on all files
echo linting all files
pre-commit run --all-files
exit /b %errorlevel%
