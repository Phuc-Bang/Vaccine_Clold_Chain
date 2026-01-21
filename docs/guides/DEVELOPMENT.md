# Development Guide

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git
- Virtual Environment (recommended)

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/Phuc-Bang/Vaccine_Clold_Chain.git
cd VaccineColdChain
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Setup Environment Variables

```bash
# Copy example
cp .env.example .env

# Edit .env with your settings
```

### 5. Start Services with Docker

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 6. Run Tests

```bash
# All tests
pytest backend/tests/ -v

# Unit tests only
pytest backend/tests/unit/ -v

# Integration tests only
pytest backend/tests/integration/ -v

# With coverage
pytest backend/tests/ --cov=backend/app
```

### 7. Run Backend Locally

```bash
cd backend
python main.py
```

Backend will be available at `http://localhost:8000`

## Code Style

- Python: PEP 8 (use `pylint` or `black`)
- JavaScript: ESLint + Prettier
- Use provided `.editorconfig`

## Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -am "Add feature"`
3. Push branch: `git push origin feature/your-feature`
4. Create Pull Request
5. Wait for CI/CD checks to pass
6. Merge after review

## Debugging

### Backend Logs

```bash
docker-compose logs -f backend
tail -f logs/app_*.log
```

### MQTT Debugging

```bash
# Subscribe to all topics
docker-compose exec mqtt mosquitto_sub -t '#'

# Publish test message
docker-compose exec mqtt mosquitto_pub -t test/topic -m "test message"
```

### Database Debugging

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U vaccine_user -d vaccine_coldchain

# List tables
\dt

# View data
SELECT * FROM devices;
```

## Common Issues

### Docker Port Already in Use

Change ports in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000" # Change 8000 to 8001
```

### Database Connection Error

```bash
# Check database status
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

### MQTT Connection Refused

```bash
# Check MQTT broker
docker-compose logs mqtt

# Test connection
docker-compose exec mqtt mosquitto_pub -h localhost -t test -m test
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MQTT Protocol](https://mqtt.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
