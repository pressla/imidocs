# Chapter 5: Managed Lifecycle

The Managed Lifecycle pattern defines how containerized applications should react to platform lifecycle events.

## Problem
Applications need to respond to platform-issued commands for proper lifecycle management beyond basic process monitoring.

## Solution

### SIGTERM Signal
- Sent when Kubernetes initiates container shutdown
- Allows for clean shutdown before SIGKILL
- Triggered by Pod shutdown or failed liveness probe

### SIGKILL Signal
- Forcefully terminates container if not shut down after SIGTERM
- Sent 30 seconds after SIGTERM by default

### PostStart Hook
Executes commands when container starts.

Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: post-start-hook
spec:
  containers:
  - image: k8spatterns/random-generator:1.0
    name: random-generator
    lifecycle:
      postStart:
        exec:
          command:
          - sh
          - -c
          - sleep 30 && echo "Wake up!" > /tmp/postStart_done
```

### PreStop Hook
Blocking call before container termination, similar to SIGTERM.

Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pre-stop-hook
spec:
  containers:
  - image: k8spatterns/random-generator:1.0
    name: random-generator
    lifecycle:
      preStop:
        httpGet:
          path: /shutdown
          port: 8080
```

### Lifecycle Controls Comparison

| Aspect | Lifecycle hooks | Init containers |
|--------|----------------|-----------------|
| Activates on | Container lifecycle phases | Pod lifecycle phases |
| Startup phase | postStart command | initContainers list |
| Shutdown phase | preStop command | None |
| Timing | Concurrent with ENTRYPOINT | Sequential before app containers |
| Use cases | Container-specific cleanup | Sequential Pod initialization |

### Advanced Container Control
Example of entrypoint rewriting for advanced lifecycle management:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: wrapped-random-generator
spec:
  restartPolicy: OnFailure
  volumes:
  - name: wrapper
    emptyDir: { }
  initContainers:
  - name: copy-supervisor
    image: k8spatterns/supervisor
    volumeMounts:
    - mountPath: /var/run/wrapper
      name: wrapper
    command: [ cp ]
    args: [ supervisor, /var/run/wrapper/supervisor ]
  containers:
  - image: k8spatterns/random-generator:1.0
    name: random-generator
    volumeMounts:
    - mountPath: /var/run/wrapper
      name: wrapper
    command:
    - "/var/run/wrapper/supervisor"
    args:
    - "random-generator-runner"
    - "--seed"
    - "42"
```

## Best Practices
- Implement graceful startup and shutdown handling
- Honor platform lifecycle events for reliable operation
- Application lifecycle is fully automated by the platform
