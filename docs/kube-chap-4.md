# Chapter 4: Health Probe

The Health Probe pattern enables applications to communicate their health state to Kubernetes, allowing automated management of Pods and traffic routing.

## Problem
Process status checks alone are insufficient for determining application health, as applications may hang while their processes remain running.

## Solution

### Process Health Checks
- Kubelet performs basic container process monitoring
- Containers are restarted if processes stop running

### Liveness Probes
Kubelet performs external health checks using:
- **HTTP probe**: HTTP GET request expecting 200-399 response
- **TCP Socket probe**: Requires successful TCP connection
- **Exec probe**: Command execution expecting exit code 0
- **gRPC probe**: Uses gRPC health checks

Configuration parameters:
- **initialDelaySeconds**: Delay before first check
- **periodSeconds**: Interval between checks
- **timeoutSeconds**: Maximum probe duration
- **failureThreshold**: Failed checks before unhealthy status

Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-liveness-check
spec:
  containers:
  - image: k8spatterns/random-generator:1.0
    name: random-generator
    env:
    - name: DELAY_STARTUP
      value: "20"
    ports:
    - containerPort: 8080
      protocol: TCP
    livenessProbe:
      httpGet:                  
        path: /actuator/health
        port: 8080
      initialDelaySeconds: 30   
```

### Readiness Probes
- Uses same methods as liveness probes (HTTP, TCP, Exec, gRPC)
- Failed checks remove container from service endpoint
- No container restart on failure

Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-readiness-check
spec:
  containers:
  - image: k8spatterns/random-generator:1.0
    name: random-generator
    readinessProbe:
      exec:
        command: [ "stat", "/var/run/random-generator-ready" ]
```

### Custom Pod Readiness Gates
- Enables additional Pod-level readiness conditions
- Useful for external dependencies like load balancers

Example:
```yaml
apiVersion: v1
kind: Pod
spec:
  readinessGates:
  - conditionType: "k8spatterns.io/load-balancer-ready"
status:
  conditions:
  - type: "k8spatterns.io/load-balancer-ready"
    status: "False"
  - type: Ready
    status: "False"
```

### Startup Probes
- Designed for applications with long startup times
- Uses same format as liveness probes with different timing parameters

Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-startup-check
spec:
  containers:
  - image: quay.io/wildfly/wildfly
    name: wildfly
    startupProbe:
      exec:
        command: [ "stat", "/opt/jboss/wildfly/standalone/tmp/startup-marker" ]
      initialDelaySeconds: 60
      periodSeconds: 60
      failureThreshold: 15
    livenessProbe:
      httpGet:
        path: /health
        port: 9990
        periodSeconds: 10
        failureThreshold: 3
```

## Best Practices
- Log significant events to stdout/stderr
- Log termination reasons to /dev/termination-log
- Integrate with tracing and metrics libraries (OpenTracing, Prometheus)
