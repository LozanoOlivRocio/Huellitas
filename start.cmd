@echo off
setlocal
where node >nul 2>nul
if errorlevel 1 goto portable
node "%~dp0scripts\start.mjs"
exit /b %errorlevel%

:portable
for /d %%D in ("%LOCALAPPDATA%\Huellitas\tools\node-v*-win-x64") do (
  if exist "%%~D\node.exe" set "TASK_NODE=%%~D\node.exe"
)
if not defined TASK_NODE goto missing
"%TASK_NODE%" "%~dp0scripts\start.mjs"
exit /b %errorlevel%

:missing
echo Instala Node.js LTS para iniciar Huellitas.
exit /b 1
