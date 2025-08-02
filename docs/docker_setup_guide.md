# Docker Setup Guide

## Overview

This guide covers the Docker configuration for the Personal Finance Dashboard, including development and production environments.

## Architecture

The application consists of the following services:

- **Backend API** (FastAPI) - Port 8000
- **Frontend** (Next.js) - Port 3000
- **PostgreSQL** - Port 5432
- **Redis** - Port 6379
- **Prometheus** - Port 9090
- **Grafana** - Port 3001
- **Nginx** (Production) - Ports 80/443

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM
- Ports 3000, 8000, 5432, 6379 available

### Development Environment

1. **Clone the repository and navigate to the project directory**
   ```bash
   cd personal-finance-dashboard
   ```

2. **Copy environment file**
   ```bash
   cp env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Grafana: http://localhost:3001 (admin/admin)

### Production Environment

1. **Set up environment variables**
   ```bash
   cp env.example .env.prod
   # Edit .env.prod with production values
   ```

2. **Build and start production services**
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

## Docker Configuration Details

### Backend Dockerfile

**Features:**
- Multi-stage build (development/production)
- Python 3.11 slim base image
- Non-root user for security
- Health checks
- Optimized layer caching

**Build targets:**
- `development`: Includes dev dependencies, hot reload
- `production`: Optimized for production, multiple workers

### Frontend Dockerfile

**Features:**
- Multi-stage build with dependency caching
- Next.js standalone output
- Alpine Linux for smaller image size
- Non-root user for security
- Health checks

**Build targets:**
- `development`: Includes dev dependencies, hot reload
- `production`: Optimized build with standalone output

### Docker Compose Configuration

#### Development (`docker-compose.yml`)

**Features:**
- Hot reload for development
- Volume mounts for live code changes
- Health checks for all services
- Development-friendly environment variables
- Optional nginx for production-like testing

#### Production (`docker-compose.prod.yml`)

**Features:**
- Production-optimized builds
- Resource limits and reservations
- Secure port binding (127.0.0.1)
- Environment variable configuration
- Nginx reverse proxy
- Monitoring stack

## Service Configuration

### Environment Variables

#### Required Variables
```bash
# Database
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://user:password@host:port/database

# Redis
REDIS_PASSWORD=your-redis-password
REDIS_URL=redis://:password@host:port

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com
```

#### Optional Variables
```bash
# Application
ENVIRONMENT=production
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoring
GRAFANA_PASSWORD=your-grafana-password
GRAFANA_URL=https://grafana.yourdomain.com
```

### Database Configuration

**PostgreSQL:**
- Version: 15-alpine
- Extensions: uuid-ossp, pg_trgm
- Timezone: UTC
- Initialization script included

**Redis:**
- Version: 7-alpine
- Persistence enabled (AOF)
- Password protection in production

### Monitoring Stack

**Prometheus:**
- Metrics collection from all services
- 200-hour retention
- Lifecycle management enabled

**Grafana:**
- Pre-configured dashboards
- Data source provisioning
- User management disabled

## Development Workflow

### Starting Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access services
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# With coverage
docker-compose exec backend pytest --cov=app
docker-compose exec frontend npm test -- --coverage
```

### Database Operations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Code Changes

The development environment includes volume mounts for live code changes:

- Backend: `./backend:/app`
- Frontend: `./frontend:/app`

Changes are reflected immediately with hot reload enabled.

## Production Deployment

### Security Considerations

1. **Environment Variables**
   - Use strong, unique passwords
   - Store secrets securely (Docker secrets, environment files)
   - Never commit `.env` files

2. **Network Security**
   - Bind services to 127.0.0.1 in production
   - Use nginx for SSL termination
   - Implement proper firewall rules

3. **Container Security**
   - Non-root users in all containers
   - Resource limits to prevent DoS
   - Regular security updates

### Deployment Steps

1. **Prepare Environment**
   ```bash
   cp env.example .env.prod
   # Edit with production values
   ```

2. **Build and Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

3. **Verify Deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   docker-compose -f docker-compose.prod.yml logs
   ```

4. **Run Migrations**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

### Monitoring and Maintenance

**Health Checks:**
- All services include health checks
- Monitor via Docker or external monitoring

**Logs:**
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

**Updates:**
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :3000
   
   # Change ports in docker-compose.yml
   ports:
     - "3001:3000"  # Use different host port
   ```

2. **Database Connection Issues**
   ```bash
   # Check database health
   docker-compose exec postgres pg_isready -U finance_user -d finance_dashboard
   
   # View database logs
   docker-compose logs postgres
   ```

3. **Memory Issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

4. **Build Failures**
   ```bash
   # Clean build cache
   docker-compose build --no-cache
   
   # Remove all containers and volumes
   docker-compose down -v
   docker system prune -a
   ```

### Performance Optimization

1. **Build Optimization**
   - Use .dockerignore files
   - Leverage multi-stage builds
   - Cache dependencies properly

2. **Runtime Optimization**
   - Set appropriate resource limits
   - Use health checks
   - Monitor resource usage

3. **Network Optimization**
   - Use custom networks
   - Optimize service discovery
   - Implement proper load balancing

## Next Steps

After Docker setup, consider:

1. **CI/CD Pipeline** - GitHub Actions for automated testing and deployment
2. **Cloud Deployment** - AWS, GCP, or Azure container services
3. **Monitoring** - Set up alerts and dashboards
4. **Backup Strategy** - Database and volume backups
5. **SSL/TLS** - Certificate management and HTTPS
6. **Load Balancing** - Multiple instances and traffic distribution

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review Docker and service logs
3. Verify environment configuration
4. Test with minimal configuration
5. Check resource availability 