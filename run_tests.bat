@echo off
REM Run tests with proper PYTHONPATH
set PYTHONPATH=%~dp0src
python -m pytest tests/ %*
