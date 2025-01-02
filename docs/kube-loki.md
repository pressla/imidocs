# Installing Grafana Loki on RKE2

This guide provides step-by-step instructions for installing Grafana Loki on an RKE2 cluster with existing Prometheus and Rancher installations.

## Prerequisites

- RKE2 cluster up and running
- Helm v3.x installed
- kubectl configured to access your cluster
- Prometheus installed
- Rancher installed
- Grafana installed (typically comes with Rancher monitoring)

## Installation Steps

### 1. Add Grafana Helm Repository

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 2. Create Custom Values File

Create a file named `loki-values.yaml` with the following content:

```yaml
loki:
  auth_enabled: false
  commonConfig:
    replication_factor: 1
  storage:
    type: filesystem
  
monitoring:
  selfMonitoring:
    enabled: true
    grafanaAgent:
      installOperator: false

  lokiCanary:
    enabled: false

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: pod
      - source_labels: [__meta_kubernetes_container_name]
        action: replace
        target_label: container

  - job_name: kubernetes-nodes
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - source_labels: [__meta_kubernetes_node_name]
        action: replace
        target_label: node

  - job_name: kubernetes-system-containers
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ['kube-system']
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: pod
```

### 3. Install Loki Using Helm

```bash
# Create namespace for Loki
kubectl create namespace loki-stack

# Install Loki using Helm with custom values
helm install loki grafana/loki-stack \
  --namespace loki-stack \
  --values loki-values.yaml \
  --set grafana.enabled=false
```

### 4. Configure Grafana Data Source

1. Access your Grafana instance through Rancher UI
2. Go to Configuration > Data Sources
3. Click "Add data source"
4. Select "Loki"
5. Set the URL to: `http://loki.loki-stack.svc.cluster.local:3100`
6. Click "Save & Test"

### 5. Verify Installation

Check if all pods are running:

```bash
kubectl get pods -n loki-stack
```

Verify Loki is collecting logs:

```bash
# Get one of the Loki pod names
LOKI_POD=$(kubectl get pods -n loki-stack -l app=loki -o jsonpath="{.items[0].metadata.name}")

# Check Loki logs
kubectl logs -n loki-stack $LOKI_POD
```

### 6. Using Loki in Grafana

1. In Grafana, go to "Explore"
2. Select "Loki" as the data source
3. Try a simple LogQL query:
   ```
   {namespace="kube-system"}
   ```

## Troubleshooting

### Common Issues

1. If pods are not starting:
```bash
kubectl describe pod -n loki-stack <pod-name>
```

2. If logs are not appearing:
- Verify Promtail configuration:
```bash
kubectl get configmap -n loki-stack
kubectl describe configmap -n loki-stack loki-promtail
```

3. If Grafana can't connect to Loki:
- Verify the Loki service is running:
```bash
kubectl get svc -n loki-stack
```
- Check Loki is accessible within the cluster:
```bash
kubectl run curl --image=curlimages/curl -i --tty --rm -- curl http://loki.loki-stack.svc.cluster.local:3100/ready
```

## Best Practices

1. **Resource Limits**: Adjust resource limits based on your cluster size and log volume
2. **Retention**: Configure log retention period based on your requirements
3. **Monitoring**: Set up alerts for Loki component health
4. **Backup**: Regularly backup Loki storage if using persistent storage

## Additional Configuration

### Scaling Loki

For production environments, consider:

1. Using object storage (S3, GCS) instead of filesystem
2. Implementing retention policies
3. Setting up proper resource limits
4. Configuring index and chunk storage separately

Example production values:

```yaml
loki:
  auth_enabled: true
  storage:
    type: s3
    s3:
      endpoint: your-s3-endpoint
      bucketnames: your-bucket
      access_key_id: your-access-key
      secret_access_key: your-secret-key
  limits_config:
    retention_period: 30d
    ingestion_rate_mb: 10
    ingestion_burst_size_mb: 20
```

Remember to adjust these values according to your specific requirements and infrastructure setup.
