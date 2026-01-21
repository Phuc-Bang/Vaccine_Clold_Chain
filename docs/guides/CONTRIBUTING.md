# Contributing Guide

## Code of Conduct

Be respectful, helpful, and collaborative.

## How to Contribute

### 1. Report Bugs

Create an issue with:

- **Title**: Clear and descriptive
- **Description**: Steps to reproduce, expected vs actual behavior
- **Environment**: OS, Python version, Docker version
- **Screenshots/Logs**: If applicable

### 2. Suggest Enhancements

Create an issue with:

- **Title**: Feature name
- **Motivation**: Why this feature is needed
- **Proposed Solution**: How to implement it
- **Alternatives**: Other solutions considered

### 3. Submit Code Changes

1. **Fork the repository**

   ```bash
   git clone https://github.com/YOUR-USERNAME/Vaccine_Clold_Chain.git
   ```

2. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PEP 8 for Python code
   - Write clear commit messages
   - Add tests for new features

4. **Commit changes**

   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push to branch**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Link related issues
   - Describe changes clearly
   - Include screenshots if UI changes

## Development Workflow

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Phuc-Bang/Vaccine_Clold_Chain.git
cd VaccineColdChain

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows

# Install dependencies
pip install -r backend/requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black pylint
```

### Running Tests Before Submitting

```bash
# Run all tests
pytest backend/tests/ -v

# Check code style
pylint backend/app/

# Format code
black backend/app/

# Check coverage
pytest backend/tests/ --cov=backend/app
```

## Code Style

### Python (PEP 8)

```python
# Good
def calculate_temperature_average(readings: List[float]) -> float:
    """Calculate average temperature from readings."""
    return sum(readings) / len(readings)

# Bad
def calc_temp_avg(r):
    return sum(r)/len(r)
```

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### Docstrings

```python
def create_device(device_id: str, name: str) -> dict:
    """
    Create a new device.

    Args:
        device_id: Unique device identifier
        name: Device name

    Returns:
        Created device data

    Raises:
        ValueError: If device_id is empty
        DatabaseError: If database operation fails
    """
```

### Comments

```python
# Good: Explains why, not what
# Retry up to 3 times for network resilience
for attempt in range(3):
    try:
        connect_to_mqtt()
        break
    except ConnectionError:
        pass

# Bad: Obvious from code
# Loop 3 times
for i in range(3):
    pass
```

## Git Commit Messages

Format: `Type: Description`

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build, CI/CD changes

Examples:

```
feat: Add device filtering by location
fix: Resolve MQTT connection timeout
docs: Update API documentation
test: Add unit tests for device service
```

## Pull Request Process

1. **Before submitting**:
   - Run `pytest` - all tests pass
   - Run `pylint` - no critical errors
   - Run `black` - code formatted
   - Update documentation

2. **PR Description template**:

   ```markdown
   ## Description

   Brief description of changes

   ## Related Issues

   Closes #123

   ## Type of Change

   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change

   ## Testing Done

   Describe testing performed

   ## Checklist

   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No new warnings generated
   ```

3. **After submitting**:
   - Address review comments
   - Re-run tests if changes made
   - Be patient and responsive

## Community

- **GitHub Issues**: Ask questions, report bugs
- **Discussions**: Share ideas and discuss
- **Email**: contact@vaccine-coldchain.com

## Recognition

Contributors will be recognized in:

- README.md
- CONTRIBUTORS.md
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
