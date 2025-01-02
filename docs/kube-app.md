# Configuring an Application in Kubernetes



## 1. Define the Application Components
Determine what components your application requires:
- Containers (e.g., web server, database).
- Configuration (e.g., environment variables, command-line arguments).
- Networking (e.g., ports, service exposure).
- Storage (e.g., persistent data).

---

## 2. Create the Required Kubernetes Resources
You need to define the following resources based on your application:

### a. Pods
Pods are the smallest deployable unit in Kubernetes. Typically, you don't define pods directly but through higher-level resources like Deployments.

### b. Deployments
Manages the desired state of pods, ensuring availability and handling updates.

Example YAML:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: my-image:latest
        ports:
        - containerPort: 8080
```

---

### c. Services
Expose your application within the cluster or to the external world.

Example YAML:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

---

### d. ConfigMaps
Store configuration data (non-sensitive) in a key-value format.

Example YAML:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  app.properties: |
    key1=value1
    key2=value2
```

Mount or reference this in your pod:
```yaml
    envFrom:
    - configMapRef:
        name: my-config
```

---

### e. Secrets
Store sensitive data like passwords or API keys securely.

Example YAML:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: bXlVc2Vy
  password: bXlQYXNz
```

Reference this in your pod:
```yaml
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: password
```

---

### f. Persistent Volumes and Claims
If your application needs to store data persistently.

Define a PersistentVolumeClaim (PVC):
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Mount it in your pod:
```yaml
    volumeMounts:
    - mountPath: "/data"
      name: data-volume
  volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: my-pvc
```

---

## 3. Apply the Configuration
Use `kubectl` to apply your configuration files to the cluster:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

---

## 4. Monitor and Adjust
- Use `kubectl get pods` or `kubectl describe pod [pod-name]` to check the pod's status.
- Adjust configurations or scaling as needed:
  ```bash
  kubectl scale deployment my-app --replicas=5
  ```

---

You now have a fully configured Kubernetes application!
