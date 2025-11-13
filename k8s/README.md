# OmniScope AI - Kubernetes Deployment Guide

## Overview

This directory contains Kubernetes manifests for deploying OmniScope AI in production, staging, and development environments.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Ingress Controller                    │
│              (NGINX + Let's Encrypt TLS)                │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────┐
│   Frontend   │  │    Backend    │
│  (Next.js)   │  │   (FastAPI)   │
│  Replicas: 2 │  │  Replicas: 3  │
└──────────────┘  └───────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌──────▼────────┐  ┌────▼──────┐
│  PostgreSQL  │  │     Redis     │  │   Dask    │
│ StatefulSet  │  │  Deployment   │  │  Cluster  │
└──────────────┘  └───────────────┘  └───────────┘
```

## Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - Managed: GKE, EKS, AKS
   - Self-hosted: kubeadm, k3s, microk8s

2. **kubectl** (v1.24+)
   ```bash
   kubectl version --client
   ```

3. **kustomize** (v4.5+)
   ```bash
   kustomize version
   ```

4. **Helm** (v3.10+) - for cert-manager
   ```bash
   helm version
   ```

5. **Storage Class** - for persistent volumes
   ```bash
   kubectl get storageclass
   ```

## Quick Start

### 1. Install Prerequisites

**Install NGINX Ingress Controller:**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

**Install cert-manager (for TLS):**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Create ClusterIssuer for Let's Encrypt:**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@omniscope.ai
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 2. Configure Secrets

**Create secrets file (DO NOT commit to git):**
```bash
cp base/secrets.yaml secrets-prod.yaml
# Edit secrets-prod.yaml with actual values
vim secrets-prod.yaml
```

**Apply secrets:**
```bash
kubectl apply -f secrets-prod.yaml
```

### 3. Deploy to Development

```bash
# Build and push images
docker build -t omniscope/backend:dev -f Dockerfile.backend .
docker build -t omniscope/frontend:dev -f Dockerfile .
docker push omniscope/backend:dev
docker push omniscope/frontend:dev

# Deploy
kubectl apply -k overlays/dev/

# Check status
kubectl get pods -n omniscope-dev
kubectl get svc -n omniscope-dev
```

### 4. Deploy to Staging

```bash
# Build and push images
docker build -t omniscope/backend:staging -f Dockerfile.backend .
docker build -t omniscope/frontend:staging -f Dockerfile .
docker push omniscope/backend:staging
docker push omniscope/frontend:staging

# Deploy
kubectl apply -k overlays/staging/

# Check status
kubectl get pods -n omniscope-staging
```

### 5. Deploy to Production

```bash
# Build and tag release
docker build -t omniscope/backend:v1.0.0 -f Dockerfile.backend .
docker build -t omniscope/frontend:v1.0.0 -f Dockerfile .
docker push omniscope/backend:v1.0.0
docker push omniscope/frontend:v1.0.0

# Deploy
kubectl apply -k overlays/prod/

# Verify deployment
kubectl get pods -n omniscope
kubectl get ingress -n omniscope
```

## Configuration

### Environment Variables

Edit `base/configmap.yaml` for application configuration:

```yaml
data:
  api-url: "https://api.omniscope.ai"
  websocket-url: "wss://api.omniscope.ai/socket.io"
  log-level: "info"
  max-upload-size: "100MB"
```

### Secrets Management

**Option 1: Kubernetes Secrets (Basic)**
```bash
kubectl create secret generic omniscope-secrets \
  --from-literal=postgres-password=<password> \
  --from-literal=jwt-secret=<secret> \
  -n omniscope
```

**Option 2: Sealed Secrets (Recommended)**
```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Seal secrets
kubeseal --format yaml < secrets-prod.yaml > sealed-secrets.yaml
kubectl apply -f sealed-secrets.yaml
```

**Option 3: External Secrets Operator (Enterprise)**
```bash
# Install external-secrets
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# Configure AWS Secrets Manager, HashiCorp Vault, etc.
```

### Resource Limits

Adjust resources in deployment files:

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Scaling

**Manual Scaling:**
```bash
kubectl scale deployment omniscope-backend --replicas=5 -n omniscope
```

**Auto-scaling (HPA):**
```bash
kubectl apply -f base/hpa.yaml
kubectl get hpa -n omniscope
```

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/omniscope-backend -n omniscope

# Frontend logs
kubectl logs -f deployment/omniscope-frontend -n omniscope

# All pods
kubectl logs -l app=omniscope -n omniscope --tail=100
```

### Check Pod Status

```bash
kubectl get pods -n omniscope
kubectl describe pod <pod-name> -n omniscope
```

### Check Services

```bash
kubectl get svc -n omniscope
kubectl get ingress -n omniscope
```

### Port Forwarding (for debugging)

```bash
# Backend
kubectl port-forward svc/omniscope-backend 8001:8001 -n omniscope

# Frontend
kubectl port-forward svc/omniscope-frontend 3000:3000 -n omniscope

# Dask Dashboard
kubectl port-forward svc/dask-scheduler 8787:8787 -n omniscope
```

## Database Management

### Initialize Database

```bash
# Run migrations
kubectl exec -it deployment/omniscope-backend -n omniscope -- python -m alembic upgrade head
```

### Backup Database

```bash
# Create backup
kubectl exec -it statefulset/postgres -n omniscope -- pg_dump -U omniscope_user omniscope > backup.sql

# Restore backup
kubectl exec -i statefulset/postgres -n omniscope -- psql -U omniscope_user omniscope < backup.sql
```

### Access Database

```bash
kubectl exec -it statefulset/postgres -n omniscope -- psql -U omniscope_user -d omniscope
```

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl get events -n omniscope --sort-by='.lastTimestamp'

# Check pod details
kubectl describe pod <pod-name> -n omniscope

# Check logs
kubectl logs <pod-name> -n omniscope --previous
```

### Image Pull Errors

```bash
# Check image pull secrets
kubectl get secrets -n omniscope

# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n omniscope
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n omniscope

# Check ingress
kubectl describe ingress omniscope-ingress -n omniscope

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Database Connection Issues

```bash
# Test database connection
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql -h postgres.omniscope.svc.cluster.local -U omniscope_user -d omniscope

# Check database logs
kubectl logs statefulset/postgres -n omniscope
```

## Maintenance

### Rolling Updates

```bash
# Update image
kubectl set image deployment/omniscope-backend backend=omniscope/backend:v1.1.0 -n omniscope

# Check rollout status
kubectl rollout status deployment/omniscope-backend -n omniscope

# Rollback if needed
kubectl rollout undo deployment/omniscope-backend -n omniscope
```

### Restart Deployments

```bash
kubectl rollout restart deployment/omniscope-backend -n omniscope
kubectl rollout restart deployment/omniscope-frontend -n omniscope
```

### Clean Up

```bash
# Delete specific environment
kubectl delete -k overlays/dev/

# Delete all resources
kubectl delete namespace omniscope
```

## Security Best Practices

1. **Use Network Policies**
   ```bash
   kubectl apply -f base/network-policy.yaml
   ```

2. **Enable Pod Security Standards**
   ```bash
   kubectl label namespace omniscope pod-security.kubernetes.io/enforce=restricted
   ```

3. **Use RBAC**
   ```bash
   kubectl apply -f base/rbac.yaml
   ```

4. **Scan Images**
   ```bash
   trivy image omniscope/backend:latest
   ```

5. **Rotate Secrets Regularly**
   ```bash
   # Update secrets every 90 days
   kubectl create secret generic omniscope-secrets --from-literal=jwt-secret=<new-secret> --dry-run=client -o yaml | kubectl apply -f -
   ```

## Performance Tuning

### Database Optimization

```yaml
# postgres-statefulset.yaml
env:
- name: POSTGRES_SHARED_BUFFERS
  value: "2GB"
- name: POSTGRES_EFFECTIVE_CACHE_SIZE
  value: "6GB"
- name: POSTGRES_MAX_CONNECTIONS
  value: "200"
```

### Redis Optimization

```yaml
# redis-deployment.yaml
command:
- redis-server
- --maxmemory
- "2gb"
- --maxmemory-policy
- "allkeys-lru"
```

### Application Tuning

```yaml
# backend-deployment.yaml
env:
- name: WORKERS
  value: "4"
- name: WORKER_CLASS
  value: "uvicorn.workers.UvicornWorker"
- name: WORKER_CONNECTIONS
  value: "1000"
```

## Cost Optimization

1. **Use Spot/Preemptible Instances** for Dask workers
2. **Enable Cluster Autoscaler**
3. **Set Resource Requests/Limits** appropriately
4. **Use Horizontal Pod Autoscaling**
5. **Schedule Non-Critical Jobs** during off-peak hours

## Disaster Recovery

### Backup Strategy

```bash
# Automated backups with CronJob
kubectl apply -f base/backup-cronjob.yaml
```

### Restore Procedure

1. Deploy infrastructure
2. Restore database from backup
3. Restore persistent volumes
4. Deploy applications
5. Verify functionality

## Support

- **Documentation**: https://docs.omniscope.ai/kubernetes
- **Issues**: https://github.com/omniscope/omniscope/issues
- **Slack**: #kubernetes-support
- **Email**: devops@omniscope.ai
