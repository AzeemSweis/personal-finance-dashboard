# GitHub Actions CI/CD Pipeline Guide

## Overview

This guide covers the comprehensive GitHub Actions CI/CD pipeline for the Personal Finance Dashboard, including testing, building, security scanning, and deployment automation.

## Pipeline Architecture

### Workflow Structure

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pull Request  │    │   Main Branch   │    │   Release Tag   │
│     Checks      │    │   Deployment    │    │   Release       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ • Code Quality  │    │ • Build Images  │    │ • Build Release │
│ • Security Scan │    │ • Deploy Staging│    │ • Create Release│
│ • Tests         │    │ • Deploy Prod   │    │ • Deploy Prod   │
│ • Build Verify  │    │ • Performance   │    │ • Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Workflows

### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Backend Testing**: Unit tests, linting, type checking, coverage
- **Frontend Testing**: Unit tests, linting, type checking, coverage
- **Security Scanning**: Trivy vulnerability scanner, Bandit, npm audit
- **Build & Push**: Docker image building and registry push
- **Deploy Staging**: Automatic deployment to staging environment
- **Deploy Production**: Automatic deployment to production environment
- **Performance Testing**: Load testing and performance validation
- **Notifications**: Success/failure notifications

### 2. Pull Request Checks (`pull-request.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Code Quality Analysis**: Linting, formatting, TODO checks
- **Dependency Security Check**: Vulnerability scanning
- **Automated Testing**: Unit and integration tests
- **Build Verification**: Docker build validation
- **Documentation Check**: README and API doc updates
- **Performance Impact Check**: Dependency and migration analysis
- **PR Summary**: Automated summary generation

### 3. Release Workflow (`release.yml`)

**Triggers:**
- Push of version tags (e.g., `v1.0.0`)

**Jobs:**
- **Build Release Images**: Production Docker images
- **Create Release**: GitHub release with changelog
- **Deploy Release**: Production deployment
- **Cleanup**: Post-release maintenance

## Setup Instructions

### Prerequisites

1. **GitHub Repository**: Ensure your repository is on GitHub
2. **GitHub Actions**: Enable Actions in repository settings
3. **Container Registry**: GitHub Container Registry (ghcr.io) access
4. **Environments**: Set up staging and production environments

### Environment Setup

#### 1. GitHub Environments

Create environments in your GitHub repository:

**Staging Environment:**
```bash
# Go to Settings > Environments > New environment
Name: staging
Protection rules: Required reviewers (optional)
```

**Production Environment:**
```bash
# Go to Settings > Environments > New environment
Name: production
Protection rules: Required reviewers (required)
```

#### 2. Repository Secrets

Add the following secrets in your repository settings:

```bash
# Go to Settings > Secrets and variables > Actions

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis
REDIS_URL=redis://:password@host:port

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com

# Monitoring
GRAFANA_PASSWORD=your-grafana-password
GRAFANA_URL=https://grafana.yourdomain.com

# Cloud Deployment (if applicable)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
KUBECONFIG=your-kubeconfig
```

#### 3. Branch Protection Rules

Set up branch protection for `main` and `develop`:

```bash
# Go to Settings > Branches > Add rule

# For main branch:
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators
- Restrict pushes that create files
- Allow force pushes: Disabled
- Allow deletions: Disabled

# For develop branch:
- Require pull request reviews before merging
- Require status checks to pass before merging
- Include administrators
```

## Usage Guide

### Development Workflow

#### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

#### 2. Pull Request Process

1. **Create PR**: GitHub will automatically trigger PR checks
2. **Review Checks**: All quality gates must pass
3. **Code Review**: At least one approval required
4. **Merge**: Merge to `develop` for staging deployment

#### 3. Staging Deployment

```bash
# Merge to develop branch
git checkout develop
git merge feature/new-feature
git push origin develop
```

The pipeline will automatically:
- Run all tests
- Build Docker images
- Deploy to staging environment

#### 4. Production Deployment

```bash
# Merge to main branch
git checkout main
git merge develop
git push origin main
```

The pipeline will automatically:
- Run all tests and security scans
- Build production Docker images
- Deploy to production environment

### Release Process

#### 1. Create Release

```bash
# Create and push version tag
git tag v1.0.0
git push origin v1.0.0
```

#### 2. Automated Release

The release workflow will:
- Build release Docker images
- Create GitHub release with changelog
- Deploy to production
- Send notifications

### Monitoring and Debugging

#### 1. Workflow Status

Monitor workflow status in the **Actions** tab:
- Green checkmark: Success
- Red X: Failure
- Yellow dot: In progress

#### 2. Logs and Debugging

```bash
# View workflow logs
# Go to Actions > [Workflow] > [Job] > [Step]

# Common debugging commands
echo "Debug information"  # Add to workflow steps
```

#### 3. Artifacts

Workflows generate artifacts:
- Test coverage reports
- Security scan results
- Build logs
- Docker images

## Configuration Files

### 1. Workflow Files

- `.github/workflows/ci-cd.yml`: Main CI/CD pipeline
- `.github/workflows/pull-request.yml`: PR quality checks
- `.github/workflows/release.yml`: Release automation

### 2. Dependabot

- `.github/dependabot.yml`: Automated dependency updates

### 3. Code Quality

- `frontend/.prettierrc`: Prettier configuration
- `backend/pyproject.toml`: Python tooling configuration

## Best Practices

### 1. Commit Messages

Use conventional commit format:
```bash
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: maintenance tasks
```

### 2. Branch Strategy

```bash
main          # Production-ready code
develop       # Integration branch
feature/*     # Feature development
hotfix/*      # Critical bug fixes
release/*     # Release preparation
```

### 3. Testing Strategy

- **Unit Tests**: Fast, isolated tests
- **Integration Tests**: API and database tests
- **E2E Tests**: Full application flow tests
- **Performance Tests**: Load and stress testing

### 4. Security Practices

- **Dependency Scanning**: Automated vulnerability detection
- **Code Scanning**: Static analysis for security issues
- **Secret Management**: Use GitHub secrets for sensitive data
- **Access Control**: Environment protection rules

## Troubleshooting

### Common Issues

#### 1. Workflow Failures

**Test Failures:**
```bash
# Check test logs
# Fix failing tests locally first
npm test  # Frontend
pytest    # Backend
```

**Build Failures:**
```bash
# Check Docker build locally
docker build -f backend/Dockerfile ./backend
docker build -f frontend/Dockerfile ./frontend
```

**Deployment Failures:**
```bash
# Check environment variables
# Verify deployment credentials
# Review deployment logs
```

#### 2. Performance Issues

**Slow Builds:**
- Enable Docker layer caching
- Use dependency caching
- Optimize Dockerfile layers

**Resource Limits:**
- Increase GitHub Actions minutes
- Optimize workflow parallelization
- Use self-hosted runners if needed

#### 3. Security Issues

**Vulnerability Alerts:**
- Review security scan results
- Update vulnerable dependencies
- Implement security fixes

**Secret Exposure:**
- Rotate exposed secrets
- Review commit history
- Use git-secrets for prevention

### Debugging Commands

```bash
# Check workflow syntax
# GitHub Actions validates YAML automatically

# Test locally
npm run lint
npm run test
pytest
flake8
black --check

# Docker testing
docker-compose up -d
docker-compose logs
```

## Advanced Configuration

### 1. Self-Hosted Runners

For better performance or security:

```yaml
runs-on: self-hosted
```

### 2. Matrix Builds

For multiple versions:

```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
    node-version: [16, 18, 20]
```

### 3. Conditional Steps

```yaml
- name: Conditional step
  if: github.ref == 'refs/heads/main'
  run: echo "Main branch only"
```

### 4. Manual Triggers

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
```

## Next Steps

After setting up the CI/CD pipeline:

1. **Cloud Deployment**: Configure cloud provider deployment
2. **Monitoring**: Set up application monitoring and alerting
3. **Backup Strategy**: Implement automated backups
4. **Disaster Recovery**: Plan for failure scenarios
5. **Performance Optimization**: Continuous performance monitoring
6. **Security Hardening**: Regular security audits and updates

## Support

For issues and questions:

1. Check GitHub Actions documentation
2. Review workflow logs and error messages
3. Test locally before pushing
4. Use GitHub Issues for bug reports
5. Consult the troubleshooting section 