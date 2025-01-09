# Portworx on SUSE Leap 15.5 with RKE2

This guide provides instructions for deploying Portworx on SUSE Leap 15.5 with RKE2 Kubernetes cluster.

## Quick Start

```bash
# Install required packages
export KUBECTL_SERVER_VERSION=$(kubectl version -oyaml | grep serverVersion: -A5 | grep gitVersion: | awk '{print $2}' | sed 's/+.*//')

kubectl apply -f "https://install.portworx.com/3.2?comp=pxoperator&kbver=$KUBECTL_SERVER_VERSION&ns=portworx"

zypper install -y docker python3-pip

# Start and enable docker service
systemctl enable --now docker

# Download Portworx Spec Generator
curl -o px-spec.yaml "https://install.portworx.com/3.2?operator=true&mc=false&kbver=$KUBECTL_SERVER_VERSION&ns=portworx&b=true&iop=6&r=17001&c=px-cluster-d7b5a3e7-93c6-4fb5-9bed-3623c2df15c5&osft=true&stork=true&csi=true&tel=true&st=k8s"

# Apply the spec
kubectl apply -f px-spec.yaml
```

## Deployment Architecture

```kroki-plantuml
@startuml
!define RECTANGLE class

skinparam componentStyle rectangle
skinparam monochrome true

cloud "RKE2 Cluster" {
    package "kube-system" {
        [RKE2 Components]
    }
    
    package "portworx" {
        [Portworx Operator]
        [Portworx DaemonSet]
        [Storage Cluster]
        database "Storage Pool"
    }
    
    package "Application Namespace" {
        [PVC]
        [Pod]
    }
}

[Portworx Operator] --> [Storage Cluster] : manages
[Storage Cluster] --> [Portworx DaemonSet] : controls
[Portworx DaemonSet] --> [Storage Pool] : manages
[Pod] --> [PVC]
[PVC] --> [Storage Cluster] : requests storage
@enduml
```

## Manifest Components

| Component | Type | Purpose |
|-----------|------|---------|
| portworx-operator | Deployment | Manages the Portworx cluster lifecycle |
| portworx | DaemonSet | Runs Portworx storage on each node |
| px-cluster | StorageCluster | Defines the Portworx storage cluster configuration |
| stork | Deployment | Storage orchestration for Kubernetes |
| stork-scheduler | Deployment | Custom scheduler for Portworx volumes |
| px-api | Service | Exposes Portworx API |
| portworx-service | Service | Internal communication service |

## Available StorageClasses

Portworx creates several StorageClasses by default:

| StorageClass | Description |
|--------------|-------------|
| px-replicated | Replication factor of 3 for high availability |
| px-secure-sc | Encrypted volumes with replication |
| px-db-sc | Optimized for database workloads |
| px-shared-sc | ReadWriteMany volumes for shared access |

### Sample PVC Definitions

```yaml
# High Availability PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: px-ha-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: px-replicated
  resources:
    requests:
      storage: 10Gi
---
# Encrypted Volume PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: px-secure-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: px-secure-sc
  resources:
    requests:
      storage: 20Gi
---
# Shared Volume PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: px-shared-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: px-shared-sc
  resources:
    requests:
      storage: 50Gi
```

## Verification

To verify the Portworx installation:

```bash
# Check Portworx pods
kubectl get pods -n portworx

# Verify StorageClasses
kubectl get sc

# Check Portworx status
PX_POD=$(kubectl get pods -l name=portworx -n portworx -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n portworx $PX_POD -- /opt/pwx/bin/pxctl status
```