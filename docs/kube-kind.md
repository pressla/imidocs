# Local Kubernetes Development with Kind

| Resource | Link |
|----------|------|
|OpenSuse Hauptseite|[opensuse.org](https://de.opensuse.org/Hauptseite)|
| SUSE Container Guide | [documentation.suse.com/container](https://documentation.suse.com/container/all/html/Container-guide/index.html) |
| SUSE Container Registry | [registry.suse.com](https://registry.suse.com/repositories?categories%5B%5D=apps) |
| openSUSE Leap 15.6 | [build.opensuse.org](https://build.opensuse.org/project/show/openSUSE:Leap:15.6) |

This guide walks through setting up a complete local Kubernetes development environment using Kind (Kubernetes in Docker), along with essential tools and monitoring.

## Prerequisites

This guide is specifically for openSUSE Linux distributions. Ensure you have:
- openSUSE Leap 15.6 or newer
- Root/sudo access
- Terminal access
- At least 8GB RAM and 4 CPU cores recommended

## Installing Podman

Podman is the officially supported container engine in SUSE/openSUSE:

1. Install Podman and required tools:
```bash
sudo zypper install podman podman-docker cni-plugins
```

2. Enable and start Podman socket (for Docker API compatibility):
```bash
sudo systemctl enable --now podman.socket
```

3. Configure Podman for rootless mode:
```bash
sudo touch /etc/subuid /etc/subgid
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER
```

4. Set up Docker compatibility:
```bash
# Create Docker compatibility symlink
sudo ln -sf /run/podman/podman.sock /var/run/docker.sock

# Add current user to podman group
sudo usermod -aG podman $USER
```

5. Log out and back in for group changes to take effect, then verify:
```bash
podman --version
podman ps
```

Note: The `docker` command will also work due to the podman-docker compatibility package.

## Installing Kind

Kind (Kubernetes in Docker) allows running local Kubernetes clusters using Docker containers as nodes.

```bash
# Download Kind binary
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Verify installation
kind --version
```

## Installing kubectl

Install kubectl using the official Kubernetes repository:

```bash
# Add Kubernetes repository
sudo zypper addrepo --refresh https://download.opensuse.org/repositories/containers:/kubetools/15.5/containers:kubetools.repo

# Install kubectl
sudo zypper install kubernetes-client

# Verify installation
kubectl version --client
```

## Installing Helm

Install Helm using the openSUSE package manager:

```bash
# Add Helm repository
sudo zypper addrepo https://download.opensuse.org/repositories/home:tlusk:kubectl/15.6/home:tlusk:kubectl.repo

# Install Helm
sudo zypper refresh
sudo zypper install helm

# Verify installation
helm version
```

## Creating a Kind Cluster

1. Create a cluster configuration file `kind-config.yaml`:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
- role: worker
- role: worker
```

2. Create the cluster:
```bash
kind create cluster --name monitoring --config kind-config.yaml
```

3. Verify cluster is running:
```bash
kubectl cluster-info
```


## Installing Monitoring Stack

We'll set up a complete monitoring solution with Prometheus, Grafana, and Loki using Helm charts.

1. Create monitoring namespace:
```bash 
kubectl create namespace monitoring
```

2. Add required Helm repositories:
```bash 
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

3. Install Prometheus stack:
```bash 
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.enabled=true \
  --set prometheus.service.type=ClusterIP \
  --values - <<EOF
grafana:
  service:
    type: ClusterIP
  adminPassword: admin123
prometheus:
  prometheusSpec:
    retention: 7d
EOF
```

4. Install Loki stack:
```bash 
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi
```

5. Verify installations:
```bash 
kubectl get pods -n monitoring
```

## Setting up Nginx Reverse Proxy

Create a file named `nginx-proxy.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: monitoring
data:
  nginx.conf: |
    events {
      worker_connections 1024;
    }
    http {
      server {
        listen 80;
        
        location /grafana/ {
          proxy_pass http://prometheus-grafana.monitoring.svc.cluster.local:80/;
          proxy_set_header Host $host;
        }
        
        location /prometheus/ {
          proxy_pass http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090/;
          proxy_set_header Host $host;
        }
        
        location /loki/ {
          proxy_pass http://loki.monitoring.svc.cluster.local:3100/;
          proxy_set_header Host $host;
        }
      }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-proxy
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: nginx-proxy
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx-proxy
    spec:
      containers:
      - name: nginx
        image: registry.suse.com/suse/nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-proxy
  namespace: monitoring
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 80
  selector:
    app: nginx-proxy
```

Apply the configuration:
```bash 
kubectl apply -f nginx-proxy.yaml
```

## Accessing the Dashboards

Get the Grafana admin password (if you didn't set it in the values):
```bash 
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

Access the dashboards through the Nginx proxy:
- Grafana: http://localhost/grafana
  - Username: admin
  - Password: admin123 (or from above command if not set in values)
- Prometheus: http://localhost/prometheus
- Loki: http://localhost/loki

Configure Loki as a data source in Grafana:
1. Go to Configuration > Data Sources in Grafana
2. Add a new Loki data source
3. Set the URL to: http://loki:3100
4. Click "Save & Test"

## Cleaning Up

To delete the Kind cluster:
```bash 
kind delete cluster --name monitoring
```

## Next Steps

With this setup, you now have:
  - A local multi-node Kubernetes cluster
  - The Kubernetes CLI (kubectl) for cluster management
  - Helm for package management
  - A complete monitoring stack with Prometheus and Grafana

You can now:
  1. Deploy applications to your cluster
  2. Monitor cluster and application metrics
  3. Set up alerts based on metrics
  4. Explore Grafana dashboards for visualization

## Troubleshooting

### Common Issues

1. **Podman service not running**
  Check Podman socket status: `sudo systemctl status podman.socket`
  Start Podman if stopped: `sudo systemctl start podman.socket`
  Verify Podman is working: `podman ps`

2. **Permission issues**
  Check subuid/subgid mappings: `grep $USER /etc/subuid /etc/subgid`
  Verify Podman socket permissions: `ls -l /run/podman/podman.sock`
  Ensure your user is in the podman group: `groups $USER`
  Run: `podman system migrate` to update container storage

3. **Port conflicts**
  Check if port 80 is in use: `sudo netstat -tulpn | grep :80`
  Ensure no other web servers are running on port 80
  You may need root privileges to bind to port 80

4. **Resource constraints**
  Check available resources: `free -h` and `nproc`
  Close unnecessary applications
  Consider adding swap space if needed
  Verify cgroup settings: `cat /proc/cmdline | grep cgroup`

5. **Repository issues**
   Refresh repositories: `sudo zypper refresh`
   Check for repository errors: `sudo zypper repos -u`
   Verify network connectivity to repository URLs
