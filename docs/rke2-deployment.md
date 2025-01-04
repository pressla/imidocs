# RKE2 Default Deployment
rke2 version v1.31.4+rke2r1
30.12.2024

[RKE2 Quickstart](https://docs.rke2.io/install/quickstart)

kubeconfig env vaiable required to target kubectl to the file:
```bash
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
kubectl get pods --all-namespaces
helm ls --all-namespaces
```
cleanup_completed.sh:
```bash
#!/bin/bash

# List all namespaces
namespaces=$(kubectl get namespaces -o jsonpath="{.items[*].metadata.name}")

# Loop through each namespace and delete completed pods
for ns in $namespaces; do
    echo "Cleaning up completed pods in namespace: $ns"
    kubectl delete pod --namespace=$ns --field-selector=status.phase=Succeeded
done

```
or
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-completed-pods
  namespace: kube-system
spec:
  schedule: "0 0 * * *"  # Run daily at midnight
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - |
              kubectl delete pod --all-namespaces --field-selector=status.phase=Succeeded
          restartPolicy: OnFailure

```


This document describes the default deployment of RKE2 components in the `kube-system` namespace.

## Core Components

### Control Plane Components
- **kube-apiserver**: The API server is the front-end for the Kubernetes control plane, handling all API operations and serving as the gateway for the cluster.
- **kube-controller-manager**: Runs controller processes that regulate the state of the cluster.
- **kube-scheduler**: Handles pod scheduling across the cluster nodes.
- **etcd**: The distributed key-value store that maintains cluster state.

### Networking Components
- **rke2-canal**: Provides networking and network policy implementation using Calico and Flannel.
- **kube-proxy**: Maintains network rules on nodes for pod communication.
- **rke2-ingress-nginx-controller**: The NGINX ingress controller for handling incoming traffic to the cluster.

### DNS Services
- **rke2-coredns**: Provides DNS services within the cluster.
- **rke2-coredns-autoscaler**: Automatically scales CoreDNS deployments based on cluster load.

### Monitoring and Metrics
- **rke2-metrics-server**: Collects resource metrics from kubelets for horizontal pod autoscaling.

### Storage Management
- **rke2-snapshot-controller**: Manages volume snapshots in the cluster.
- **rke2-snapshot-validation-webhook**: Validates volume snapshot operations.

### Cloud Integration
- **cloud-controller-manager**: Integrates with underlying cloud provider APIs.

## Deployment Diagram

```kroki-plantuml

@startuml
!define RECTANGLE class

' Set vertical layout
left to right direction
skinparam nodesep 100
skinparam ranksep 50

skinparam component {
    BackgroundColor<<core>> LightBlue
    BackgroundColor<<network>> LightGreen
    BackgroundColor<<dns>> LightYellow
    BackgroundColor<<metrics>> LightPink
    BackgroundColor<<storage>> LightGray
    BackgroundColor<<cloud>> LightCyan
}

' Control Plane at the top
package "Control Plane" {
    [kube-apiserver]<<core>>
    database "etcd"<<core>>
    [kube-controller-manager]<<core>>
    [kube-scheduler]<<core>>
}

' Core infrastructure components
package "Networking" {
    [rke2-canal]<<network>>
    [kube-proxy]<<network>>
    [rke2-ingress-nginx-controller]<<network>>
}

' Service components
package "DNS Services" {
    [rke2-coredns]<<dns>>
    [rke2-coredns-autoscaler]<<dns>>
}

package "Monitoring" {
    [rke2-metrics-server]<<metrics>>
}

package "Storage" {
    [rke2-snapshot-controller]<<storage>>
    [rke2-snapshot-validation-webhook]<<storage>>
}

package "Cloud Integration" {
    [cloud-controller-manager]<<cloud>>
}

' Vertical relationships
[kube-apiserver] -down-> etcd : stores state
[kube-controller-manager] -up-> [kube-apiserver] : watches/updates
[kube-scheduler] -up-> [kube-apiserver] : watches/updates
[rke2-canal] -up-> [kube-apiserver] : reports status
[kube-proxy] -up-> [kube-apiserver] : watches services
[rke2-ingress-nginx-controller] -up-> [kube-apiserver] : watches ingress
[rke2-coredns] -up-> [kube-apiserver] : watches services
[rke2-coredns-autoscaler] -up-> [rke2-coredns] : scales
[rke2-metrics-server] -up-> [kube-apiserver] : reports metrics
[cloud-controller-manager] -up-> [kube-apiserver] : manages cloud resources
[rke2-snapshot-controller] -up-> [kube-apiserver] : manages snapshots
[rke2-snapshot-validation-webhook] -up-> [kube-apiserver] : validates requests

@enduml
```

## Installation Process
The deployment shows several completed Helm installations that set up these components:
- helm-install-rke2-canal
- helm-install-rke2-coredns
- helm-install-rke2-ingress-nginx
- helm-install-rke2-metrics-server
- helm-install-rke2-snapshot-controller
- helm-install-rke2-snapshot-validation-webhook

Each component is deployed and managed as part of the RKE2 system, ensuring a production-ready Kubernetes cluster with all necessary services for networking, DNS, metrics collection, and storage management.
