# Testing Guide

## Setup

```bash
pip install -r requirements.txt
```

## Running Tests

### All Tests

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest -q                 # Quiet output
```

### Specific Test Files

```bash
pytest tests/test_database.py      # Database tests only
pytest tests/test_pdf_generator.py # PDF generation tests only
```

### Test Categories

```bash
pytest -k "database"     # Tests with 'database' in name
pytest -k "pdf"          # Tests with 'pdf' in name
pytest -k "validation"   # Validation tests
```

### Test Markers

```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Skip slow tests
```

## Test Structure

```bash
tests/
├── conftest.py           # Shared fixtures
├── test_database.py      # Database operations
└── test_pdf_generator.py # PDF generation
```

## Coverage (Optional)

```bash
pip install pytest-cov
pytest --cov=.           # Show coverage
pytest --cov=. --cov-report=html  # HTML report
```

