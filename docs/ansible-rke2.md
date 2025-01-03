# Installing Ansible on RKE2 Cluster

## Quick Steps
1. Install Ansible operator prerequisites:
   ```bash
   kubectl create namespace ansible-system
   ```
2. Install Ansible Operator:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/operator-framework/operator-lifecycle-manager/master/deploy/upstream/quickstart-catalog.yaml
   kubectl create -f https://operatorhub.io/install/ansible-operator.yaml
   ```
3. Verify installation:
   ```bash
   kubectl get pods -n ansible-system
   ```

## Architecture Overview

```kroki-plantuml
@startuml
!define RECTANGLE class

skinparam component {
    BackgroundColor<<existing>> LightGray
    BackgroundColor<<new>> LightGreen
}

package "RKE2 Control Plane" {
    [kube-apiserver]<<existing>>
    [etcd]<<existing>>
}

package "Ansible Components" {
    [ansible-operator]<<new>> #LightGreen
    [ansible-runner]<<new>> #LightGreen
    [ansible-controller]<<new>> #LightGreen
}

cloud "Managed Resources" {
    [Pods]<<existing>>
    [Services]<<existing>>
    [ConfigMaps]<<existing>>
}

[ansible-operator] -up-> [kube-apiserver] : Watches/Updates
[ansible-runner] -up-> [ansible-operator] : Executes Playbooks
[ansible-controller] -up-> [ansible-operator] : Manages State
[ansible-operator] -down-> [Pods] : Manages
[ansible-operator] -down-> [Services] : Configures
[ansible-operator] -down-> [ConfigMaps] : Updates

@enduml
```

## Prerequisites
- Running RKE2 cluster named "default"
- `kubectl` access to the cluster
- Cluster admin privileges

## Detailed Installation Steps

### 1. Prepare the Cluster

Create a dedicated namespace for Ansible components:
```bash
kubectl create namespace ansible-system
```

### 2. Install Operator Lifecycle Manager (OLM)

OLM is required to manage the Ansible Operator:
```bash
kubectl apply -f https://raw.githubusercontent.com/operator-framework/operator-lifecycle-manager/master/deploy/upstream/quickstart-catalog.yaml
```

Wait for OLM to be ready:
```bash
kubectl wait --for=condition=ready pod -l name=olm-operator -n olm --timeout=90s
```

### 3. Install Ansible Operator

Deploy the Ansible Operator using OperatorHub manifest:
```bash
kubectl create -f https://operatorhub.io/install/ansible-operator.yaml
```

### 4. Verify Installation

Check if the Ansible Operator pods are running:
```bash
kubectl get pods -n ansible-system
```

Verify the operator deployment:
```bash
kubectl get deployment -n ansible-system ansible-operator
```

### 5. Configure RBAC

Create necessary RBAC permissions:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ansible-operator
  namespace: ansible-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ansible-operator
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ansible-operator
subjects:
- kind: ServiceAccount
  name: ansible-operator
  namespace: ansible-system
roleRef:
  kind: ClusterRole
  name: ansible-operator
  apiGroup: rbac.authorization.k8s.io
EOF
```

## Usage Example

Create a simple Ansible playbook as a ConfigMap:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: sample-playbook
  namespace: ansible-system
data:
  playbook.yml: |
    - hosts: localhost
      tasks:
        - name: Create a namespace
          k8s:
            name: example-namespace
            kind: Namespace
            state: present
EOF
```

## Troubleshooting

### Common Issues

1. Operator Pod Not Starting
```bash
kubectl describe pod -n ansible-system -l name=ansible-operator
```

2. Permission Issues
```bash
kubectl describe clusterrolebinding ansible-operator
```

3. OLM Installation Problems
```bash
kubectl get events -n olm
```

## Maintenance

### Updating Ansible Operator

To update the operator to a newer version:
```bash
kubectl delete -f https://operatorhub.io/install/ansible-operator.yaml
kubectl create -f https://operatorhub.io/install/ansible-operator.yaml
```

### Cleanup

To remove Ansible from your cluster:
```bash
kubectl delete namespace ansible-system
kubectl delete clusterrole ansible-operator
kubectl delete clusterrolebinding ansible-operator