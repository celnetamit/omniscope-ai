# OmniScope AI - Monitoring and Alerting Guide

## Overview

This directory contains monitoring and alerting configurations for OmniScope AI using:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notifications

## Architecture

```
┌─────────────────────────────────────────────────┐
│              OmniScope Services                  │
│  (Backend, Frontend, Database, Redis, Dask)     │
└────────────────┬────────────────────────────────┘
                 │ Metrics
                 ▼
┌────────────────────────────────────────────────┐
│              Prometheus                         │
│  - Scrapes metrics every 15s                   │
│  - Evaluates alert rules                       │
│  - Stores time-series data                     │
└────────────┬───────────────────┬────────────────┘
             │                   │
             │ Alerts            │ Queries
             ▼                   ▼
┌────────────────────┐  ┌───────────────────────┐
│   Alertmanager     │  │      Grafana          │
│  - Routes alerts   │  │  - Visualizations     │
│  - Deduplicates    │  │  - Dashboards         │
│  - Sends notifs    │  │  - User interface     │
└────────────────────┘  └───────────────────────┘
```

## Quick Start

### 1. Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

### 2. Deploy Prometheus

```bash
# Apply configuration
kubectl apply -f prometheus/prometheus-config.yaml
kubectl apply -f prometheus/alert-rules.yaml

# Deploy Prometheus
kubectl apply -f prometheus/deployment.yaml

# Verify
kubectl get pods -n monitoring
kubectl logs -f deployment/prometheus -n monitoring
```

### 3. Deploy Grafana

```bash
# Create secrets
kubectl create secret generic grafana-secrets \
  --from-literal=admin-user=admin \
  --from-literal=admin-password=<strong-password> \
  -n monitoring

# Deploy Grafana
kubectl apply -f grafana/deployment.yaml

# Import dashboards
kubectl create configmap grafana-dashboards \
  --from-file=grafana/dashboards.json \
  -n monitoring

# Verify
kubectl get pods -n monitoring
```

### 4. Deploy Alertmanager

```bash
# Apply configuration
kubectl apply -f alertmanager/config.yaml

# Deploy Alertmanager
kubectl apply -f alertmanager/deployment.yaml

# Verify
kubectl get pods -n monitoring
```

### 5. Access Dashboards

**Prometheus:**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090
```

**Grafana:**
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open http://localhost:3000
# Login: admin / <your-password>
```

**Alertmanager:**
```bash
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
# Open http://localhost:9093
```

## Metrics

### Application Metrics

OmniScope services expose metrics at `/metrics` endpoint:

**Backend Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `active_users_total` - Number of active users
- `ml_training_jobs_active` - Active ML training jobs
- `ml_training_duration_seconds` - Training duration
- `ml_model_accuracy` - Model accuracy scores
- `websocket_connections_active` - Active WebSocket connections
- `collaboration_active_workspaces` - Active workspaces
- `job_failures_total` - Failed processing jobs

**Database Metrics:**
- `pg_stat_database_numbackends` - Active connections
- `pg_stat_database_xact_commit` - Committed transactions
- `pg_stat_database_blks_hit` - Cache hits
- `pg_replication_lag_seconds` - Replication lag

**Redis Metrics:**
- `redis_memory_used_bytes` - Memory usage
- `redis_connected_clients` - Connected clients
- `redis_commands_processed_total` - Commands processed

### Custom Metrics

Add custom metrics to your application:

**Python (Backend):**
```python
from prometheus_client import Counter, Histogram, Gauge

# Counter
requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Histogram
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Gauge
active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

# Usage
requests_total.labels(method='GET', endpoint='/api/data', status='200').inc()
with request_duration.labels(method='GET', endpoint='/api/data').time():
    # Your code here
    pass
active_users.set(42)
```

**TypeScript (Frontend):**
```typescript
import { Counter, Histogram } from 'prom-client';

const pageViews = new Counter({
  name: 'page_views_total',
  help: 'Total page views',
  labelNames: ['page']
});

pageViews.inc({ page: '/dashboard' });
```

## Dashboards

### Pre-built Dashboards

1. **OmniScope Overview**
   - Request rate and error rate
   - Response times (p50, p95, p99)
   - Active users
   - CPU and memory usage

2. **ML Training**
   - Active training jobs
   - Training duration
   - Model accuracy
   - GPU utilization

3. **Collaboration**
   - Active workspaces
   - WebSocket connections
   - Message rate
   - Sync latency

4. **Database**
   - Connection pool usage
   - Query duration
   - Transaction rate
   - Cache hit ratio

### Creating Custom Dashboards

1. Open Grafana
2. Click "+" → "Dashboard"
3. Add panel
4. Select Prometheus data source
5. Enter PromQL query
6. Configure visualization
7. Save dashboard

**Example PromQL Queries:**

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# CPU usage by pod
rate(container_cpu_usage_seconds_total{namespace="omniscope"}[5m])

# Memory usage by pod
container_memory_usage_bytes{namespace="omniscope"}

# Active users
active_users_total

# Training jobs
ml_training_jobs_active
```

## Alerts

### Alert Rules

Alerts are defined in `prometheus/alert-rules.yaml`:

**Critical Alerts:**
- High error rate (>5% for 5 minutes)
- Pod down (for 5 minutes)
- Disk space low (<10%)
- Backup failed (no backup in 24 hours)

**Warning Alerts:**
- Slow API response (p95 > 2s for 10 minutes)
- High CPU usage (>80% for 10 minutes)
- High memory usage (>90% for 5 minutes)
- Database connection pool exhausted (>80%)
- Certificate expiring soon (<30 days)

**Info Alerts:**
- Rate limit exceeded (>100/s for 5 minutes)

### Alert Routing

Alerts are routed based on severity and component:

```yaml
Critical → PagerDuty + Slack + Email
Warning → Slack + Email
Info → Email only

Database alerts → Database team
ML alerts → ML team
```

### Notification Channels

**Email:**
```yaml
email_configs:
- to: 'devops@omniscope.ai'
  headers:
    Subject: '[OmniScope] {{ .GroupLabels.alertname }}'
```

**Slack:**
```yaml
slack_configs:
- channel: '#alerts-critical'
  title: '🚨 Critical Alert'
  text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

**PagerDuty:**
```yaml
pagerduty_configs:
- service_key: 'YOUR_PAGERDUTY_KEY'
  description: '{{ .GroupLabels.alertname }}'
```

### Testing Alerts

**Trigger test alert:**
```bash
# Create test alert
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: alert-test
  namespace: omniscope
  labels:
    app: test
spec:
  containers:
  - name: test
    image: busybox
    command: ['sh', '-c', 'exit 1']
EOF

# Check Alertmanager
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
# Open http://localhost:9093
```

## Monitoring Best Practices

### 1. Define SLOs (Service Level Objectives)

```yaml
Availability: 99.9% uptime
Latency: p95 < 500ms
Error Rate: < 0.1%
```

### 2. Use the Four Golden Signals

- **Latency**: How long requests take
- **Traffic**: How many requests
- **Errors**: Rate of failed requests
- **Saturation**: Resource utilization

### 3. Alert on Symptoms, Not Causes

❌ Bad: "CPU usage > 80%"
✅ Good: "API response time > 2s"

### 4. Reduce Alert Fatigue

- Set appropriate thresholds
- Use inhibition rules
- Group related alerts
- Set proper repeat intervals

### 5. Document Runbooks

For each alert, document:
- What it means
- Why it matters
- How to investigate
- How to resolve

## Troubleshooting

### Prometheus Not Scraping Metrics

**Check service discovery:**
```bash
kubectl get pods -n omniscope -o wide
kubectl get svc -n omniscope
```

**Check Prometheus targets:**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090/targets
```

**Check pod annotations:**
```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8001"
    prometheus.io/path: "/metrics"
```

### Grafana Dashboard Not Loading

**Check data source:**
```bash
# Verify Prometheus is accessible
kubectl exec -it -n monitoring deployment/grafana -- curl http://prometheus:9090/api/v1/query?query=up
```

**Check dashboard JSON:**
```bash
kubectl get configmap grafana-dashboards -n monitoring -o yaml
```

### Alerts Not Firing

**Check alert rules:**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090/alerts
```

**Check Alertmanager:**
```bash
kubectl logs -n monitoring deployment/alertmanager
```

**Test alert rule:**
```bash
# Run PromQL query manually
curl 'http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])'
```

## Performance Tuning

### Prometheus

**Reduce cardinality:**
```yaml
# Avoid high-cardinality labels
# Bad: user_id, request_id
# Good: endpoint, status, method
```

**Adjust retention:**
```yaml
args:
  - '--storage.tsdb.retention.time=30d'  # Reduce if needed
  - '--storage.tsdb.retention.size=50GB'
```

**Increase resources:**
```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "2000m"
```

### Grafana

**Enable caching:**
```yaml
env:
- name: GF_RENDERING_SERVER_URL
  value: "http://renderer:8081/render"
- name: GF_RENDERING_CALLBACK_URL
  value: "http://grafana:3000/"
```

**Optimize queries:**
- Use recording rules for complex queries
- Set appropriate time ranges
- Limit number of series

## Security

### Secure Prometheus

**Enable authentication:**
```yaml
# Use OAuth2 proxy or basic auth
args:
  - '--web.config.file=/etc/prometheus/web-config.yml'
```

**Restrict access:**
```yaml
# Use NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: prometheus-network-policy
spec:
  podSelector:
    matchLabels:
      app: prometheus
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: grafana
```

### Secure Grafana

**Enable HTTPS:**
```yaml
env:
- name: GF_SERVER_PROTOCOL
  value: "https"
- name: GF_SERVER_CERT_FILE
  value: "/etc/grafana/ssl/tls.crt"
- name: GF_SERVER_CERT_KEY
  value: "/etc/grafana/ssl/tls.key"
```

**Enable OAuth:**
```yaml
env:
- name: GF_AUTH_GENERIC_OAUTH_ENABLED
  value: "true"
- name: GF_AUTH_GENERIC_OAUTH_CLIENT_ID
  value: "your-client-id"
```

## Backup and Recovery

### Backup Prometheus Data

```bash
# Create snapshot
kubectl exec -n monitoring deployment/prometheus -- \
  curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Copy snapshot
kubectl cp monitoring/prometheus-pod:/prometheus/snapshots/snapshot-name ./backup/
```

### Backup Grafana Dashboards

```bash
# Export dashboards
kubectl exec -n monitoring deployment/grafana -- \
  grafana-cli admin export-dashboards > dashboards-backup.json
```

## Maintenance

### Update Prometheus

```bash
# Update image version
kubectl set image deployment/prometheus \
  prometheus=prom/prometheus:v2.48.0 \
  -n monitoring

# Check rollout
kubectl rollout status deployment/prometheus -n monitoring
```

### Update Grafana

```bash
# Update image version
kubectl set image deployment/grafana \
  grafana=grafana/grafana:10.2.0 \
  -n monitoring

# Check rollout
kubectl rollout status deployment/grafana -n monitoring
```

## Support

- **Documentation**: https://docs.omniscope.ai/monitoring
- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/
- **Email**: monitoring@omniscope.ai
