# Apache Airflow on RKE2

This guide provides instructions for deploying Apache Airflow on RKE2 Kubernetes cluster.

## Architecture Overview

### Celery Executor Architecture (Method 1)

```kroki-plantuml
@startuml
!define KUBERNETES #F0F0F0
!define POD #E8E8E8

skinparam component {
    BackgroundColor KUBERNETES
    BorderColor Black
}

package "Kubernetes Cluster" {
    component "Airflow Namespace" {
        component "Airflow Webserver Pod" as webserver POD
        component "Airflow Scheduler Pod" as scheduler POD
        component "Airflow Worker Pods" as workers POD
        database "PostgreSQL Pod" as postgres POD
        database "Redis Pod" as redis POD
    }
}

webserver --> postgres : Metadata
scheduler --> postgres : Metadata
workers --> postgres : Metadata
scheduler --> redis : Queue
workers --> redis : Queue
@enduml
```

## Installation

There are two methods to install Airflow on RKE2: using Helm with Celery executor (recommended for production) or using Kubernetes manifests with Kubernetes executor (simpler setup).

### Method 1: Helm Installation with Celery Executor

This method is recommended for production environments as it provides better scalability and worker management.

First, create the necessary PersistentVolumes. These must be created before installing Helm chart as they need to exist for the PVCs to bind successfully:

```yaml
# Create airflow-pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: data-airflow-postgresql-0
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
  hostPath:
    path: /opt/local-path-provisioner/airflow-postgres
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-dags
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
  hostPath:
    path: /opt/local-path-provisioner/airflow-dags
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-logs
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
  hostPath:
    path: /opt/local-path-provisioner/airflow-logs
    type: DirectoryOrCreate
```

Apply the PV configuration:

```bash
# Create the PVs
kubectl apply -f airflow-pv.yaml

# Create namespace for Airflow
kubectl create namespace airflow

# Add the official Apache Airflow Helm repository
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Install Airflow using Helm with storage configuration
helm install airflow apache-airflow/airflow \
    --namespace airflow \
    --set executor=CeleryExecutor \
    --set postgresql.enabled=true \
    --set redis.enabled=true \
    --set webserver.defaultUser.enabled=true \
    --set webserver.defaultUser.username=admin \
    --set webserver.defaultUser.password=admin \
    --set webserver.defaultUser.email=admin@example.com \
    --set dags.persistence.enabled=true \
    --set dags.persistence.storageClassName=local-path \
    --set dags.persistence.size=1Gi \
    --set logs.persistence.enabled=true \
    --set logs.persistence.storageClassName=local-path \
    --set logs.persistence.size=1Gi \
    --set postgresql.persistence.enabled=true \
    --set postgresql.persistence.storageClassName=local-path \
    --set postgresql.persistence.size=10Gi
```

Note: The PV names must match exactly what the Helm chart expects:
- `data-airflow-postgresql-0` for PostgreSQL data
- `airflow-dags` for DAGs storage
- `airflow-logs` for logs storage

### Method 2: Manifest Installation with Kubernetes Executor

This method uses native Kubernetes resources and the Kubernetes executor, which is simpler to set up and maintain for smaller deployments.

#### Architecture

```kroki-plantuml
@startuml
!define KUBERNETES #F0F0F0
!define POD #E8E8E8
!define PV #ADD8E6
!define INGRESS #98FB98

skinparam component {
    BackgroundColor KUBERNETES
    BorderColor Black
}

package "Kubernetes Cluster" {
    component "Ingress Controller" as ingress INGRESS {
        component "Ingress Rule\\n(/airflow)" as rule
    }
    
    package "Airflow Namespace" {
        component "Airflow Webserver Pod" as webserver POD {
            component "Webserver Service" as websvc
        }
        component "Airflow Scheduler Pod" as scheduler POD {
            component "Kubernetes Executor" as executor
        }
        database "PostgreSQL Pod" as postgres POD {
            component "PostgreSQL Service" as pgservice
        }
        
        component "Dynamic Worker Pods" as workers POD {
            component "Task Pod 1" as task1
            component "Task Pod 2" as task2
            component "Task Pod N" as taskn
        }

        database "Persistent Storage" as pvs PV {
            database "PostgreSQL Volume\\n(/airflow-postgres)" as postgrespv
            database "DAGs Volume\\n(/airflow-dags)" as dagspv
        }
    }
}

ingress --> rule
rule --> websvc : "Route /airflow"
websvc --> webserver
webserver --> pgservice : "Metadata"
scheduler --> pgservice : "Metadata"
executor ..> workers : "Creates"
workers --> pgservice : "Metadata"
postgres --> postgrespv : "Storage"
webserver --> dagspv : "Read DAGs"
scheduler --> dagspv : "Read DAGs"
workers --> dagspv : "Read DAGs"

note right of workers
  Kubernetes Executor dynamically creates
  worker pods for each task execution.
  Pods are ephemeral and removed after
  task completion.
end note

note right of pvs
  Persistent volumes provide durable
  storage for database and DAG files
  across all pods
end note
@enduml
```

```bash
# Create namespace
kubectl create namespace airflow
```

First, create the storage resources:

```yaml
# PostgreSQL PV and PVC
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-postgres-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
  hostPath:
    path: /opt/local-path-provisioner/airflow-postgres
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airflow-postgres-pvc
  namespace: airflow
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Gi
---
# DAGs PV and PVC
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-dags-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
  hostPath:
    path: /opt/local-path-provisioner/airflow-dags
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airflow-dags-pvc
  namespace: airflow
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: local-path
  resources:
    requests:
      storage: 1Gi
```

Create the ConfigMap for Airflow configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: airflow-config
  namespace: airflow
data:
  AIRFLOW__CORE__EXECUTOR: KubernetesExecutor
  AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@airflow-postgres:5432/airflow
  AIRFLOW__CORE__LOAD_EXAMPLES: "false"
  AIRFLOW__KUBERNETES__NAMESPACE: airflow
  AIRFLOW__KUBERNETES__WORKER_CONTAINER_REPOSITORY: apache/airflow
  AIRFLOW__KUBERNETES__WORKER_CONTAINER_TAG: 2.7.1
  AIRFLOW__KUBERNETES__DELETE_WORKER_PODS: "true"
```

Create the PostgreSQL deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-postgres
  namespace: airflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: airflow-postgres
  template:
    metadata:
      labels:
        app: airflow-postgres
    spec:
      containers:
        - name: postgres
          image: postgres:13
          env:
            - name: POSTGRES_USER
              value: airflow
            - name: POSTGRES_PASSWORD
              value: airflow
            - name: POSTGRES_DB
              value: airflow
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: airflow-postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: airflow-postgres
  namespace: airflow
spec:
  selector:
    app: airflow-postgres
  ports:
    - port: 5432
```

Create the Airflow webserver and scheduler deployments:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-webserver
  namespace: airflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: airflow-webserver
  template:
    metadata:
      labels:
        app: airflow-webserver
    spec:
      containers:
        - name: webserver
          image: apache/airflow:2.7.1
          command: ["airflow", "webserver"]
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: airflow-config
          volumeMounts:
            - name: dags
              mountPath: /opt/airflow/dags
      volumes:
        - name: dags
          persistentVolumeClaim:
            claimName: airflow-dags-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-scheduler
  namespace: airflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: airflow-scheduler
  template:
    metadata:
      labels:
        app: airflow-scheduler
    spec:
      containers:
        - name: scheduler
          image: apache/airflow:2.7.1
          command: ["airflow", "scheduler"]
          envFrom:
            - configMapRef:
                name: airflow-config
          volumeMounts:
            - name: dags
              mountPath: /opt/airflow/dags
      volumes:
        - name: dags
          persistentVolumeClaim:
            claimName: airflow-dags-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: airflow-webserver
  namespace: airflow
spec:
  selector:
    app: airflow-webserver
  ports:
    - port: 8080
```

Initialize the database and create admin user:

```bash
# Create initialization job
kubectl create job --namespace airflow airflow-init-db --from=deployment/airflow-scheduler -- airflow db init

# Create admin user
kubectl create job --namespace airflow airflow-create-user --from=deployment/airflow-scheduler -- airflow users create --username admin --password admin --firstname admin --lastname admin --role Admin --email admin@example.com
```

All the above manifests are combined in a single file for easier deployment. You can find it at `airflow-manifest.yaml`. To deploy:

```bash
# Create the namespace
kubectl create namespace airflow

# Apply the combined manifest
kubectl apply -f airflow-manifest.yaml
```

The manifest includes all necessary resources:
- Persistent Volumes and Claims for storage
- ConfigMap for Airflow configuration
- PostgreSQL deployment and service
- Airflow webserver and scheduler deployments
- Ingress configuration

## Configuration

### Environment Variables and ConfigMaps

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| AIRFLOW__CORE__EXECUTOR | The executor class to use | CeleryExecutor |
| AIRFLOW__CORE__SQL_ALCHEMY_CONN | Database connection string | postgresql+psycopg2://airflow:airflow@postgresql:5432/airflow |
| AIRFLOW__CELERY__BROKER_URL | Redis connection for Celery | redis://:@redis:6379/0 |
| AIRFLOW__CELERY__RESULT_BACKEND | Celery result backend | db+postgresql://airflow:airflow@postgresql:5432/airflow |
| AIRFLOW__WEBSERVER__SECRET_KEY | Secret key for the web interface | YOUR_SECRET_KEY_HERE |
| AIRFLOW__WEBSERVER__BASE_URL | The base URL of the web interface | http://localhost:8080 |
| AIRFLOW__CORE__LOAD_EXAMPLES | Whether to load example DAGs | false |
| AIRFLOW__CORE__DAGS_FOLDER | Location of DAG files | /opt/airflow/dags |

## Accessing the Web Interface

### Setting up Ingress

Create an ingress resource to expose the Airflow webserver:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airflow-ingress
  namespace: airflow
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
    - host: airflow.example.com  # Replace with your domain
      http:
        paths:
          - path: /airflow(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: airflow-webserver
                port:
                  number: 8080
```

The ingress configuration is included in the combined manifest. After applying the manifest and once the ingress controller is properly configured, you can access the Airflow web interface at `http://airflow.example.com/airflow`. Login with the default credentials:
- Username: admin
- Password: admin

## Verification

To verify the installation:

```bash
# Check all pods are running
kubectl get pods -n airflow

# Check services
kubectl get services -n airflow

# Check persistent volumes
kubectl get pvc -n airflow
```

## Uninstallation

### Method 1: Uninstalling Helm-based Installation

To remove the Helm-based Airflow installation:

```bash
# Delete the Helm release
helm uninstall airflow -n airflow

# Delete the namespace and all its resources
kubectl delete namespace airflow

# Delete the PersistentVolumes
kubectl delete pv data-airflow-postgresql-0
kubectl delete pv airflow-dags
kubectl delete pv airflow-logs

# Optional: Remove the Helm repository
helm repo remove apache-airflow

# Optional: Clean up the local storage directories
sudo rm -rf /opt/local-path-provisioner/airflow-postgres
sudo rm -rf /opt/local-path-provisioner/airflow-dags
sudo rm -rf /opt/local-path-provisioner/airflow-logs
```

### Method 2: Uninstalling Manifest-based Installation

To remove the manifest-based Airflow installation:

```bash
# Delete all Airflow resources using the combined manifest
kubectl delete -f airflow-manifest.yaml

# Alternative: Delete the namespace (this will delete all resources in the namespace)
kubectl delete namespace airflow

# Optional: Clean up the local storage directories
sudo rm -rf /opt/local-path-provisioner/airflow-postgres
sudo rm -rf /opt/local-path-provisioner/airflow-dags