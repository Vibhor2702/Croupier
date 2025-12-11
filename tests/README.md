# Croupier Test Suite

Comprehensive pytest-based test suite covering all API endpoints and authentication flows.

## Test Structure

- **conftest.py** - Pytest fixtures and configuration (auto-configures PYTHONPATH)
- **test_organization.py** - Organization CRUD operations (9 tests)
- **test_admin.py** - Admin authentication and JWT tokens (8 tests)
- **test_health.py** - Health check endpoint (3 tests)

**Total:** 20 tests with 100% pass rate

## Quick Start

```bash
# Run all tests (requires MongoDB connection)
pytest

# Verbose output with detailed results
pytest -v

# Quiet mode (summary only)
pytest -q

# Run specific test file
pytest tests/test_organization.py

# Run specific test class
pytest tests/test_organization.py::TestOrganizationCreate

# Run specific test
pytest tests/test_organization.py::TestOrganizationCreate::test_create_organization_success
```

## Prerequisites

**1. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**2. MongoDB Connection:**
- Ensure MongoDB is running (locally or Atlas)
- Configure `.env` with valid `MONGODB_URL`

**3. Environment Setup:**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string
```

## Test Features

**Automated Test Isolation:**
- Random suffixes prevent data conflicts between test runs
- Unique organization names per test execution
- Clean database state management

**JWT Authentication Testing:**
- Token generation and validation
- Protected endpoint authorization
- Expired token handling

**Edge Case Coverage:**
- Duplicate organization names
- Invalid credentials
- Missing authentication tokens
- Password validation rules
- Organization name format validation

## Expected Output

```bash
$ pytest -q
....................                                                    [100%]
20 passed, 8 warnings in 7.72s
```

**All 20 tests should pass consistently.**

## Test Coverage Breakdown

### Organization Management (9 tests)
- ✅ Create organization with admin
- ✅ Create duplicate organization (error handling)
- ✅ Get organization by name
- ✅ Get non-existent organization
- ✅ Update organization (authenticated)
- ✅ Update with collection migration on rename
- ✅ Update without authentication (401 error)
- ✅ Delete organization (authenticated)
- ✅ Delete without authentication (401 error)

### Admin Authentication (8 tests)
- ✅ Successful login with valid credentials
- ✅ Login with invalid password
- ✅ Login with non-existent email
- ✅ JWT token format validation
- ✅ Token expiry handling
- ✅ Protected endpoint access with valid token
- ✅ Protected endpoint access without token
- ✅ Protected endpoint access with invalid token

### Health & Utilities (3 tests)
- ✅ Health check endpoint
- ✅ API metadata verification
- ✅ Database connectivity status

## Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'app'`  
**Solution:** The `pytest.ini` file automatically configures PYTHONPATH. If issues persist, run from project root.

**Issue:** Tests fail with MongoDB connection error  
**Solution:** Verify MongoDB is running and `.env` has correct `MONGODB_URL`

**Issue:** Tests fail with duplicate key errors  
**Solution:** Random suffixes should prevent this. If persistent, manually clean test data from MongoDB.

**Issue:** JWT token tests fail  
**Solution:** Ensure `JWT_SECRET_KEY` in `.env` matches the one used during token generation.

## Running Tests in CI/CD

```yaml
# Example GitHub Actions workflow
- name: Run tests
  env:
    MONGODB_URL: ${{ secrets.MONGODB_URL }}
    JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  run: pytest -v --tb=short
```

---

**Note:** Tests use the same MongoDB instance as development. For production CI/CD, consider using a separate test database or MongoDB container.
