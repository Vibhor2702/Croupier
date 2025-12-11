# Croupier Tests

This directory contains the test suite for the Croupier application.

## Test Structure

- `conftest.py` - Pytest fixtures and test configuration
- `test_organization.py` - Tests for organization management endpoints
- `test_admin.py` - Tests for admin authentication
- `test_health.py` - Tests for health check and utility endpoints

## Running Tests

Install test dependencies:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_organization.py
```

Run specific test class:
```bash
pytest tests/test_organization.py::TestOrganizationCreate
```

Run specific test:
```bash
pytest tests/test_organization.py::TestOrganizationCreate::test_create_organization_success
```

## Test Coverage

The test suite covers:
- ✅ Organization creation with validation
- ✅ Organization retrieval
- ✅ Organization updates (authenticated)
- ✅ Organization deletion (authenticated)
- ✅ Admin login and JWT token generation
- ✅ JWT authentication for protected endpoints
- ✅ Health check endpoint
- ✅ Error handling and edge cases
