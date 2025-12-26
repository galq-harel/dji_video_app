# Testing Guide

## Overview

This project uses **pytest** for testing with coverage reporting and mocking capabilities.

## Installation

Install testing dependencies:

```bash
pip install -r requirements.txt
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

## Running Tests

### Windows (PowerShell)
```powershell
.\run_tests.ps1
```

### Windows (Command Prompt)
```cmd
run_tests.bat
```

### Linux/Mac or Manual
```bash
export PYTHONPATH=src
python -m pytest
```

### Run with verbose output
```powershell
.\run_tests.ps1 -v
```

### Run specific test file
```powershell
.\run_tests.ps1 tests/test_models.py
```

### Run specific test class or function
```powershell
.\run_tests.ps1 tests/test_models.py::TestVideoFrameMetadata
.\run_tests.ps1 tests/test_models.py::TestVideoFrameMetadata::test_create_valid_frame
```

### Run with coverage report
```powershell
.\run_tests.ps1 --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

### Run with coverage in terminal
```powershell
.\run_tests.ps1 --cov-report=term-missing
```

## Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Shared fixtures and configuration
├── test_models.py           # Tests for Pydantic models
├── test_video_metadata_service.py  # Tests for metadata extraction
├── test_csv_export_service.py      # Tests for CSV export
└── test_integration.py      # Integration tests
```

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `sample_srt_path` - Temporary SRT file with valid GPS data
- `empty_srt_path` - Empty SRT file for error handling tests
- `invalid_srt_path` - SRT file without GPS data
- `sample_frames` - List of VideoFrameMetadata objects
- `csv_output_path` - Temporary CSV output path

## Writing New Tests

### Model Tests
Test Pydantic models in `test_models.py`:
```python
def test_my_model_feature():
    frame = VideoFrameMetadata(latitude=31.0, longitude=34.0)
    assert frame.latitude == 31.0
```

### Service Tests
Test business logic in service test files:
```python
def test_my_service_method(service, sample_srt_path):
    result = service.extract_from_video(sample_srt_path)
    assert len(result) > 0
```

### Integration Tests
Test complete workflows in `test_integration.py`:
```python
def test_complete_workflow(sample_srt_path, tmp_path):
    # Extract + Export + Verify
    ...
```

## Best Practices

1. **Use fixtures** - Avoid repeating test setup code
2. **Test edge cases** - Empty data, None values, invalid input
3. **Test error handling** - Verify exceptions are raised appropriately
4. **Keep tests isolated** - Each test should be independent
5. **Use meaningful names** - Test names should describe what they verify
6. **Mock external dependencies** - Use `pytest-mock` for external calls

## Coverage Goals

- Aim for **>80% code coverage**
- Focus on critical paths (metadata extraction, CSV export)
- Ensure error handling is tested

## CI/CD

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests

See `.github/workflows/tests.yml` for configuration.

## Troubleshooting

### Tests fail locally but pass in CI
- Check Python version (`python --version`)
- Ensure all dependencies are installed
- Clear pytest cache: `pytest --cache-clear`

### Import errors
- Make sure you're running pytest from project root
- Verify `src/` is in PYTHONPATH (handled by pytest.ini)

### Coverage reports missing files
- Check `pytest.ini` configuration
- Ensure source files are in `src/` directory
