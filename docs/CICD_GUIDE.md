# OmniScope AI - CI/CD Guide

## Overview

This guide describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for OmniScope AI using GitHub Actions.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Code Push/PR                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              CI Pipeline (GitHub Actions)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Lint    │  │  Test    │  │ Security │             │
│  │  Check   │  │  Suite   │  │  Scan    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────┬────────────────────────────────────────┘
                 │ (on success)
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Build & Push Images                         │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Backend Image   │  │  Frontend Image  │            │
│  └──────────────────┘  └──────────────────┘            │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Staging    │  │  Production  │
│  Deployment  │  │  Deployment  │
└──────────────┘  └──────────────┘
```

## Workflows

### 1. CI Workflow (`ci.yml`)

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
1. **Backend Tests**
   - Linting (flake8, black, isort)
   - Type checking (mypy)
   - Security scanning (bandit, safety)
   - Unit tests with coverage
   - Integration tests

2. **Frontend Tests**
   - Linting (ESLint)
   - Type checking (TypeScript)
   - Unit tests with coverage
   - Build verification

3. **Integration Tests**
   - End-to-end tests
   - API integration tests
   - Database integration tests

4. **Security Scanning**
   - Trivy vulnerability scanner
   - OWASP Dependency Check
   - SARIF upload to GitHub Security

5. **Code Quality**
   - SonarCloud analysis
   - Code coverage reporting
   - Technical debt tracking

### 2. CD Workflow (`cd.yml`)

Runs on pushes to `main` branch and version tags.

**Jobs:**
1. **Build and Push**
   - Build Docker images for backend and frontend
   - Push to GitHub Container Registry
   - Multi-platform builds (amd64, arm64)
   - Image vulnerability scanning

2. **Deploy to Staging**
   - Triggered on `develop` branch
   - Deploy to staging Kubernetes cluster
   - Run smoke tests
   - Notify team via Slack

3. **Deploy to Production**
   - Triggered on version tags (v*)
   - Create database backup
   - Deploy to production Kubernetes cluster
   - Run smoke tests and E2E tests
   - Rollback on failure
   - Create GitHub release
   - Notify team and PagerDuty on failure

4. **Run Migrations**
   - Execute database migrations
   - Verify migration success

### 3. Scheduled Tasks (`scheduled-tasks.yml`)

Runs daily at 2 AM UTC.

**Jobs:**
1. **Database Backup**
   - Create PostgreSQL backup
   - Upload to S3
   - Clean old backups (keep 30 days)

2. **Security Scanning**
   - Daily vulnerability scan
   - Alert on critical vulnerabilities

3. **Performance Testing**
   - Load testing with Locust
   - Performance threshold checks
   - Generate performance reports

4. **Cleanup**
   - Remove old Kubernetes jobs
   - Clean completed pods
   - Delete old container images

5. **Health Check**
   - Verify production health
   - Verify staging health
   - Alert on failures

## Setup Instructions

### 1. GitHub Secrets

Configure the following secrets in your GitHub repository:

**Required Secrets:**
```bash
# Kubernetes
KUBE_CONFIG_STAGING    # Base64-encoded kubeconfig for staging
KUBE_CONFIG_PROD       # Base64-encoded kubeconfig for production

# Container Registry
GITHUB_TOKEN           # Automatically provided by GitHub

# AWS (for backups)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

# Notifications
SLACK_WEBHOOK          # Slack webhook URL
PAGERDUTY_INTEGRATION_KEY

# Code Quality
SONAR_TOKEN            # SonarCloud token
CODECOV_TOKEN          # Codecov token (optional)
```

**Generate kubeconfig secret:**
```bash
# Encode kubeconfig
cat ~/.kube/config | base64 -w 0

# Add to GitHub secrets
gh secret set KUBE_CONFIG_PROD --body "$(cat ~/.kube/config | base64 -w 0)"
```

### 2. Enable GitHub Actions

1. Go to repository Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"
3. Set workflow permissions to "Read and write permissions"

### 3. Configure Branch Protection

**Main Branch:**
```yaml
Required status checks:
  - backend-tests
  - frontend-tests
  - integration-tests
  - security-scan

Require pull request reviews: 2
Require conversation resolution: true
Require signed commits: true
```

**Develop Branch:**
```yaml
Required status checks:
  - backend-tests
  - frontend-tests

Require pull request reviews: 1
```

### 4. Set up Environments

**Staging Environment:**
```yaml
Name: staging
URL: https://staging.omniscope.ai
Protection rules:
  - Required reviewers: 0
  - Wait timer: 0 minutes
```

**Production Environment:**
```yaml
Name: production
URL: https://omniscope.ai
Protection rules:
  - Required reviewers: 2
  - Wait timer: 5 minutes
  - Restrict to specific branches: main, tags/v*
```

## Deployment Process

### Deploying to Staging

**Automatic:**
```bash
# Push to develop branch
git checkout develop
git push origin develop

# GitHub Actions automatically:
# 1. Runs CI tests
# 2. Builds images
# 3. Deploys to staging
# 4. Runs smoke tests
```

**Manual:**
```bash
# Trigger workflow manually
gh workflow run cd.yml -f environment=staging
```

### Deploying to Production

**Via Version Tag:**
```bash
# Create and push version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions automatically:
# 1. Runs CI tests
# 2. Builds images with version tag
# 3. Creates database backup
# 4. Deploys to production
# 5. Runs smoke tests
# 6. Creates GitHub release
```

**Manual Deployment:**
```bash
# Trigger workflow manually (requires approval)
gh workflow run cd.yml -f environment=production
```

### Rollback Procedure

**Automatic Rollback:**
- Triggered automatically if smoke tests fail
- Reverts to previous deployment

**Manual Rollback:**
```bash
# Set up kubectl
export KUBECONFIG=~/.kube/config

# Rollback backend
kubectl rollout undo deployment/omniscope-backend -n omniscope

# Rollback frontend
kubectl rollout undo deployment/omniscope-frontend -n omniscope

# Verify rollback
kubectl rollout status deployment/omniscope-backend -n omniscope
kubectl rollout status deployment/omniscope-frontend -n omniscope
```

## Testing

### Running Tests Locally

**Backend Tests:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=backend_db --cov=modules

# Run specific test file
pytest tests/test_integration_ml_framework.py -v

# Run with coverage report
pytest tests/ --cov=backend_db --cov-report=html
```

**Frontend Tests:**
```bash
# Install dependencies
npm ci

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test
npm test -- src/components/ml/automl-config-form.test.tsx
```

**Integration Tests:**
```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/test_integration_*.py -v

# Stop services
docker-compose down
```

### Load Testing

```bash
# Install Locust
pip install locust

# Run load test
locust -f tests/load_test.py \
  --host https://api.omniscope.ai \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless

# With web UI
locust -f tests/load_test.py --host https://api.omniscope.ai
# Open http://localhost:8089
```

## Monitoring Deployments

### GitHub Actions Dashboard

View workflow runs:
```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Watch run in real-time
gh run watch <run-id>

# View logs
gh run view <run-id> --log
```

### Kubernetes Deployment Status

```bash
# Check deployment status
kubectl get deployments -n omniscope

# View rollout status
kubectl rollout status deployment/omniscope-backend -n omniscope

# View deployment history
kubectl rollout history deployment/omniscope-backend -n omniscope

# View pod status
kubectl get pods -n omniscope

# View logs
kubectl logs -f deployment/omniscope-backend -n omniscope
```

### Metrics and Alerts

**Prometheus Queries:**
```promql
# Deployment success rate
rate(deployment_success_total[1h]) / rate(deployment_total[1h])

# Deployment duration
deployment_duration_seconds

# Rollback rate
rate(deployment_rollback_total[1h])
```

**Grafana Dashboard:**
- Deployment frequency
- Success rate
- Mean time to recovery (MTTR)
- Change failure rate

## Troubleshooting

### CI Pipeline Failures

**Tests Failing:**
```bash
# View test logs
gh run view <run-id> --log

# Run tests locally
pytest tests/ -v --tb=short

# Check for flaky tests
pytest tests/ --count=10
```

**Build Failures:**
```bash
# Check Docker build logs
docker build -t omniscope/backend:test -f Dockerfile.backend .

# Check for dependency issues
pip check
npm audit
```

**Security Scan Failures:**
```bash
# Run Trivy locally
trivy fs .

# Check for vulnerabilities
safety check
npm audit

# Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

### Deployment Failures

**Image Pull Errors:**
```bash
# Verify image exists
docker pull ghcr.io/omniscope/omniscope-backend:latest

# Check image pull secrets
kubectl get secrets -n omniscope
kubectl describe secret regcred -n omniscope
```

**Pod Crashes:**
```bash
# Check pod logs
kubectl logs <pod-name> -n omniscope --previous

# Describe pod
kubectl describe pod <pod-name> -n omniscope

# Check events
kubectl get events -n omniscope --sort-by='.lastTimestamp'
```

**Database Migration Failures:**
```bash
# Check migration status
kubectl exec -it deployment/omniscope-backend -n omniscope -- \
  python -m alembic current

# View migration history
kubectl exec -it deployment/omniscope-backend -n omniscope -- \
  python -m alembic history

# Rollback migration
kubectl exec -it deployment/omniscope-backend -n omniscope -- \
  python -m alembic downgrade -1
```

## Best Practices

### 1. Commit Messages

Follow conventional commits:
```
feat: add new ML training endpoint
fix: resolve database connection issue
docs: update API documentation
test: add integration tests for collaboration
chore: update dependencies
```

### 2. Pull Requests

- Keep PRs small and focused
- Include tests for new features
- Update documentation
- Request reviews from relevant team members
- Ensure CI passes before merging

### 3. Version Tagging

Use semantic versioning:
```
v1.0.0 - Major release
v1.1.0 - Minor release (new features)
v1.1.1 - Patch release (bug fixes)
```

### 4. Deployment Strategy

- Deploy to staging first
- Run smoke tests
- Monitor for 24 hours
- Deploy to production during low-traffic hours
- Have rollback plan ready

### 5. Security

- Scan images before deployment
- Keep dependencies updated
- Rotate secrets regularly
- Use least privilege access
- Enable audit logging

## Performance Optimization

### 1. Build Optimization

**Use build cache:**
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Multi-stage builds:**
```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
COPY --from=builder /app/.next ./.next
CMD ["npm", "start"]
```

### 2. Test Optimization

**Parallel testing:**
```yaml
strategy:
  matrix:
    test-group: [unit, integration, e2e]
```

**Test caching:**
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pytest
    key: pytest-${{ hashFiles('requirements.txt') }}
```

### 3. Deployment Optimization

**Blue-green deployment:**
```bash
# Deploy new version alongside old
kubectl apply -f deployment-v2.yaml

# Switch traffic
kubectl patch service omniscope-backend -p '{"spec":{"selector":{"version":"v2"}}}'

# Remove old version
kubectl delete deployment omniscope-backend-v1
```

**Canary deployment:**
```yaml
# Deploy canary (10% traffic)
kubectl apply -f canary-deployment.yaml

# Monitor metrics
# If successful, increase to 50%, then 100%
```

## Support

- **CI/CD Issues**: devops@omniscope.ai
- **GitHub Actions Docs**: https://docs.github.com/actions
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Slack**: #devops-support
