# Testing Guide

## Overview

Testing strategy for VaccineColdChain includes unit tests, integration tests, and end-to-end tests.

## Test Structure

```
backend/tests/
├── unit/                      # Unit tests for services
├── integration/               # Integration tests for APIs
├── fixtures/                  # Test data and mocks
├── conftest.py               # Pytest configuration
└── pytest.ini                # Pytest settings
```

## Running Tests

### All Tests

```bash
pytest backend/tests/ -v
```

### Unit Tests Only

```bash
pytest backend/tests/unit/ -v
```

### Integration Tests Only

```bash
pytest backend/tests/integration/ -v
```

### Specific Test File

```bash
pytest backend/tests/unit/test_device_service.py -v
```

### Specific Test Function

```bash
pytest backend/tests/unit/test_device_service.py::TestDeviceService::test_create_device -v
```

### With Coverage Report

```bash
pytest backend/tests/ --cov=backend/app --cov-report=html
```

### With Verbose Output

```bash
pytest backend/tests/ -vv -s
```

## Writing Tests

### Unit Test Template

```python
import pytest

class TestMyService:
    """Test MyService"""

    def test_method_name(self):
        """Test method description"""
        # Arrange
        data = {"key": "value"}

        # Act
        result = my_service.method(data)

        # Assert
        assert result == expected_value
```

### Integration Test Template

```python
import pytest

class TestMyAPI:
    """Test MyAPI endpoints"""

    def test_get_endpoint(self, client):
        """Test GET endpoint"""
        # Arrange
        headers = {"Authorization": "Bearer token"}

        # Act
        response = client.get("/api/endpoint", headers=headers)

        # Assert
        assert response.status_code == 200
        assert response.json["success"] == True
```

## Test Fixtures

Define reusable test data in `fixtures/mock_data.py`:

```python
@pytest.fixture
def sample_device():
    """Sample device for testing"""
    return {
        "id": "device_001",
        "name": "Kho Lạnh A",
        "location": "Hà Nội"
    }

@pytest.fixture
def sample_telemetry():
    """Sample telemetry for testing"""
    return {
        "device_id": "device_001",
        "temperature": 5.2,
        "humidity": 45.3
    }
```

## Mocking

### Mock External Services

```python
from unittest.mock import patch, MagicMock

@patch('app.services.mqtt_service.MQTTService.publish')
def test_publish_with_mock(self, mock_publish):
    """Test with mocked MQTT publish"""
    mock_publish.return_value = True

    result = my_service.publish_data()

    assert result == True
    mock_publish.assert_called_once()
```

## Assertions

### Common Assertions

```python
# Equality
assert result == expected

# Truthy/Falsy
assert condition
assert not condition

# Type
assert isinstance(obj, MyClass)

# Exceptions
with pytest.raises(ValueError):
    function_that_raises()

# Lists
assert item in list
assert len(list) == 3

# Dicts
assert "key" in dict
assert dict["key"] == value
```

## Coverage

### Generate Coverage Report

```bash
pytest backend/tests/ --cov=backend/app --cov-report=html
```

### View Report

```bash
open htmlcov/index.html
```

### Coverage Goals

- Unit tests: 80%+ coverage
- Integration tests: 60%+ coverage
- Overall: 70%+ coverage

## Continuous Integration

Tests run automatically on every push via GitHub Actions (see `.github/workflows/test.yml`).

### Local Pre-commit Hook

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
pytest backend/tests/ -q
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

## Performance Testing

```bash
# Load testing
pytest backend/tests/load/ -v

# Timing
pytest backend/tests/ --durations=10
```

## Debugging Tests

### Print Debug Info

```python
def test_my_function():
    result = my_function()
    print(f"Result: {result}")  # Will appear with -s flag
    assert result == expected
```

### Run with Debug

```bash
pytest backend/tests/unit/test_device_service.py -v -s --tb=short
```

### Interactive Debugging

```bash
pytest backend/tests/unit/test_device_service.py --pdb
```

## Best Practices

1. **Test one thing per test** - Keep tests focused
2. **Use meaningful names** - `test_create_device_with_valid_data()` not `test1()`
3. **Arrange, Act, Assert** - Follow AAA pattern
4. **Use fixtures** - Share common test data
5. **Mock external dependencies** - Don't hit real APIs/DBs
6. **Test edge cases** - Empty inputs, None values, etc.
7. **Keep tests fast** - Should run in seconds
8. **Isolate tests** - No test should depend on another

## Troubleshooting

### Tests Fail Locally But Pass on CI

```bash
# Clear cache
pytest --cache-clear backend/tests/

# Run with specific Python version
python3.9 -m pytest backend/tests/
```

### Import Errors

```bash
# Add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
pytest backend/tests/
```

### Database Locked

```bash
# Reset test database
rm -f vaccine_coldchain_test.db
pytest backend/tests/
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
