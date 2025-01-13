# Open Source Kubernetes Deployment Guide

## Summary
This guide describes a production-grade Kubernetes deployment using RKE2 as the distribution, featuring a comprehensive stack of open-source components. The deployment includes a 3-node cluster with Traefik for API and web gateway services, Keycloak for OAuth2 authentication, OpenEBS for storage management, PostgreSQL as a stateful database, and Apache Airflow for orchestrating analysis workloads.

## Quick Start

```bash
# Install RKE2 on the first server node
curl -sfL https://get.rke2.io | sh -
systemctl enable rke2-server.service
systemctl start rke2-server.service

# Get the node token from the first server
cat /var/lib/rancher/rke2/server/node-token

# Install and join additional server nodes
curl -sfL https://get.rke2.io | sh -
mkdir -p /etc/rancher/rke2/
cat << EOF > /etc/rancher/rke2/config.yaml
server: https://<first-server-ip>:9345
token: <node-token>
EOF
systemctl enable rke2-server.service
systemctl start rke2-server.service

# Install kubectl and configure access
mkdir ~/.kube
cp /etc/rancher/rke2/rke2.yaml ~/.kube/config
chmod 600 ~/.kube/config

# Deploy OpenEBS
kubectl apply -f https://openebs.github.io/charts/openebs-operator.yaml

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

# Add and update required Helm repositories
helm repo add traefik https://helm.traefik.io/traefik
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Deploy Traefik
helm install traefik traefik/traefik -n traefik --create-namespace

# Deploy PostgreSQL with OpenEBS storage
kubectl create namespace database
helm install postgresql bitnami/postgresql \
  --namespace database \
  --set persistence.storageClass=openebs-hostpath \
  --set persistence.size=10Gi

# Deploy Keycloak
kubectl create namespace auth
helm install keycloak bitnami/keycloak \
  --namespace auth \
  --set postgresql.enabled=false \
  --set externalDatabase.host=postgresql.database.svc.cluster.local \
  --set externalDatabase.port=5432 \
  --set externalDatabase.user=postgres \
  --set externalDatabase.database=keycloak

# Deploy Airflow
helm install airflow bitnami/airflow \
  --namespace airflow --create-namespace \
  --set postgresql.enabled=false \
  --set externalDatabase.host=postgresql.database.svc.cluster.local \
  --set externalDatabase.port=5432 \
  --set externalDatabase.user=postgres \
  --set externalDatabase.database=airflow
```

## Architecture

```kroki-plantuml
@startuml
skinparam componentStyle uml2

cloud "External Network" {
  [Client Applications]
}

node "RKE2 Kubernetes Cluster" {
  [RKE2 Server Node 1]
  [RKE2 Server Node 2]
  [RKE2 Server Node 3]
  [Traefik Ingress]
  [Keycloak]
  [OpenEBS]
  [PostgreSQL StatefulSet]
  [Airflow Scheduler]
  [Airflow WebServer]
  [Analysis Pods]
}

[Client Applications] --> [Traefik Ingress]
[Traefik Ingress] --> [Keycloak]
[Traefik Ingress] --> [Airflow WebServer]
[Keycloak] --> [PostgreSQL StatefulSet]
[Airflow Scheduler] --> [PostgreSQL StatefulSet]
[Airflow WebServer] --> [PostgreSQL StatefulSet]
[PostgreSQL StatefulSet] --> [OpenEBS]
[Airflow Scheduler] --> [Analysis Pods]

@enduml
```

## Component Details

### RKE2 Cluster
- 3-node highly available control plane
- Built-in containerd runtime
- Automated certificate management
- Integrated security features

### Traefik Gateway
- API and Web Gateway services
- Automatic SSL/TLS termination
- Rate limiting capabilities
- Monitoring endpoints
- Load balancing

### Keycloak OAuth2
- Centralized authentication
- OAuth2/OpenID Connect support
- User federation
- Role-based access control
- Single sign-on capabilities

### OpenEBS Storage
- Dynamic volume provisioning
- Local and distributed storage options
- Storage class management
- Snapshot and backup support

### PostgreSQL StatefulSet
- Persistent storage with OpenEBS
- Automated backups
- High availability configuration
- Data replication

### Airflow Orchestration
- Dynamic pod spawning
- Workflow management
- Scheduled analysis jobs
- Resource optimization
- Monitoring and logging

## Data Flow

```kroki-plantuml
@startuml
participant "Client Request" as CR
participant "Traefik Gateway" as TG
participant "Keycloak Auth" as KA
participant "Protected Service" as PS
participant "PostgreSQL" as PG
participant "Airflow" as AF
participant "Analysis Pod" as AP

CR -> TG: 1. HTTP/HTTPS Request
TG -> KA: 2. Auth Request
KA -> PG: 3. Validate Token
KA -> TG: 4. Auth Response
TG -> PS: 5. Forward Request
PS -> AF: 6. Trigger Analysis
AF -> PG: 7. Store Job Status
AF -> AP: 8. Launch Analysis Pod
AP -> PG: 9. Store Results

@enduml
```

## Security Considerations

1. Network Security
   - All external traffic routed through Traefik
   - Internal service communication encrypted
   - Network policies for pod isolation

2. Authentication & Authorization
   - Centralized OAuth2 with Keycloak
   - Role-based access control (RBAC)
   - Service account management
   - Token-based authentication

3. Data Security
   - Encrypted storage with OpenEBS
   - Regular database backups
   - Secure credential management
   - Pod security policies

## Monitoring and Maintenance

1. Cluster Health
   - Node status monitoring
   - Control plane metrics
   - Resource utilization

2. Application Monitoring
   - Traefik metrics
   - Keycloak audit logs
   - PostgreSQL performance metrics
   - Airflow task monitoring

3. Storage Management
   - Volume health monitoring
   - Capacity planning
   - Backup verification
   - Performance metrics

## Scaling Considerations

1. Horizontal Scaling
   - Add worker nodes as needed
   - Scale Traefik replicas
   - Increase analysis pod capacity

2. Vertical Scaling
   - Adjust resource limits
   - Optimize pod requests
   - Tune database resources

3. Storage Scaling
   - Expand volume capacity
   - Add storage nodes
   - Optimize storage classes

## Troubleshooting

1. Cluster Issues
   - Check node status
   - Verify control plane health
   - Review system logs

2. Application Issues
   - Monitor pod status
   - Check service endpoints
   - Review application logs

3. Storage Issues
   - Verify volume status
   - Check storage provisioner
   - Monitor capacity alerts

## Backup and Disaster Recovery

1. Regular Backups
   - Database dumps
   - Volume snapshots
   - Configuration backups

2. Recovery Procedures
   - Node replacement
   - Data restoration
   - Service recovery

3. High Availability
   - Multi-node redundancy
   - Service replication
   - Automated failover
