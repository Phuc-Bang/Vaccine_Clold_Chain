# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Server with SSH access
- Domain name (optional)
- SSL Certificate (optional, for production)

## Local Deployment (Development)

### Step 1: Start Services

```bash
docker-compose up -d
```

### Step 2: Verify Services

```bash
# Check status
docker-compose ps

# Test Backend
curl http://localhost:8000/health

# Test MQTT
mosquitto_pub -h localhost -t test -m "hello"
```

### Step 3: Access Applications

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000 (when implemented)
- **MQTT**: localhost:1883

## Production Deployment

### 1. Prepare Server

```bash
# SSH into server
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/Phuc-Bang/Vaccine_Clold_Chain.git
cd VaccineColdChain
```

### 2. Setup Environment

```bash
# Copy and edit production configuration
cp .env.example .env
nano .env

# Set production values:
# FLASK_ENV=production
# DEBUG=False
# DATABASE_URL=postgresql://user:pass@db:5432/vaccine_prod
# MQTT_BROKER_HOST=mqtt
```

### 3. Update Docker Compose for Production

```bash
# Use production configuration
cp docker-compose.yml docker-compose.prod.yml

# Edit docker-compose.prod.yml:
# - Remove volume mounts for code
# - Set image tags to specific versions
# - Configure logging drivers
# - Add resource limits
```

### 4. Deploy Services

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify health
docker exec vaccine_backend curl http://localhost:8000/health
```

### 5. Setup Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/vaccine-coldchain
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and start:

```bash
sudo ln -s /etc/nginx/sites-available/vaccine-coldchain /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 6. Setup SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 7. Backup Database

```bash
# Daily backup
docker-compose exec db pg_dump -U vaccine_user vaccine_coldchain > backup_$(date +%Y%m%d).sql

# Automate with cron
0 2 * * * cd /path/to/VaccineColdChain && docker-compose exec db pg_dump -U vaccine_user vaccine_coldchain > backup_$(date +\%Y\%m\%d).sql
```

### 8. Monitoring

```bash
# Check disk space
docker system df

# Monitor container stats
docker stats

# View logs
docker-compose logs -f --tail=100
```

## Rolling Update

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Start services (will replace old containers)
docker-compose up -d

# Verify
docker-compose ps
```

## Rollback

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout previous-tag

# Start previous version
docker-compose up -d
```

## Health Checks

```bash
# API health
curl https://your-domain.com/api/health

# Database
docker-compose exec db pg_isready

# MQTT
docker-compose exec mqtt mosquitto_pub -t test -m test

# Check logs for errors
docker-compose logs | grep ERROR
```

## Maintenance

```bash
# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Clean up unused networks
docker network prune

# View logs
docker-compose logs --tail=100

# Restart services
docker-compose restart

# Scale services (if using Docker Swarm)
docker-compose up -d --scale backend=3
```

## Troubleshooting

### Services Not Starting

```bash
# Check error logs
docker-compose logs backend

# Check resource availability
docker system df

# Restart Docker daemon
sudo systemctl restart docker
```

### Database Connection Issues

```bash
# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U vaccine_user -d vaccine_coldchain -c "SELECT 1;"
```

### MQTT Broker Issues

```bash
# Check MQTT logs
docker-compose logs mqtt

# Test MQTT
docker-compose exec mqtt mosquitto_pub -t test -m test
```

## Security Checklist

- [ ] Change default database passwords
- [ ] Setup SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Setup log aggregation
- [ ] Configure rate limiting
- [ ] Enable API authentication (v2.0)
- [ ] Setup monitoring and alerts
- [ ] Regular security updates

## Support

- GitHub Issues: https://github.com/Phuc-Bang/Vaccine_Clold_Chain/issues
- Email: support@vaccine-coldchain.com
