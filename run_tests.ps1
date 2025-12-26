# PowerShell script to run tests with proper PYTHONPATH
$env:PYTHONPATH = "$PSScriptRoot\src"
python -m pytest tests/ $args
