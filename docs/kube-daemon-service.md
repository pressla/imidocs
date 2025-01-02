# Daemon Service

The Daemon Service pattern allows you to place and run prioritized, infrastructure-focused Pods on targeted nodes. It is used primarily by administrators to run node-specific Pods to enhance the Kubernetes platform capabilities.

## Problem

The concept of a daemon in software systems exists at many levels:

- At an operating system level, a daemon is a long-running, self-recovering computer program that runs as a background process
- In Unix, daemon names end in d (httpd, named, sshd)
- Other OS terms: services-started tasks, ghost jobs
- JVM has daemon threads that provide supporting services to user threads

Similarly, Kubernetes also has the concept of a DaemonSet. Considering that Kubernetes is a distributed platform spread across multiple nodes and with the primary goal of managing application Pods, a DaemonSet is represented by Pods that run on the cluster nodes and provide some background capabilities for the rest of the cluster.

## Solution

ReplicaSet and its predecessor ReplicationController are control structures responsible for making sure a specific number of Pods are running. These controllers constantly monitor the list of running Pods and make sure the actual number of Pods always matches the desired number. In that regard, a DaemonSet is a similar construct and is responsible for ensuring that a certain number of Pods are always running.

The difference is that the first two run a specific number of Pods, usually driven by the application requirements of high availability and user load, irrespective of the node count. On the other hand, a DaemonSet is not driven by consumer load in deciding how many Pod instances to run and where to run. Its main purpose is to keep running a single Pod on every node or specific nodes.

### Example DaemonSet Resource

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: random-refresher
spec:
  selector:
    matchLabels:
      app: random-refresher
  template:
    metadata:
      labels:
        app: random-refresher
    spec:
      nodeSelector:            # Use only nodes with the label feature set to value hw-rng
        feature: hw-rng
      containers:
      - image: k8spatterns/random-generator:1.0
        name: random-generator
        command: [ "java", "RandomRunner", "/numbers.txt", "10000", "30" ]
        volumeMounts:          # DaemonSets often mount a portion of a node's filesystem
        - mountPath: /host_dev
          name: devices
      volumes:
      - name: devices
        hostPath:              # hostPath for accessing the node directories directly
          path: /dev
```

Given this behavior, the primary candidates for a DaemonSet are usually infrastructure-related processes, such as:
- Cluster storage providers
- Log collectors
- Metric exporters
- kube-proxy

### Key Differences from ReplicaSet

1. **Pod Placement**
   - By default, a DaemonSet places one Pod instance on every node
   - Can be controlled/limited to subset of nodes using nodeSelector or affinity fields

2. **Scheduling**
   - A Pod created by DaemonSet already has nodeName specified
   - Doesn't require Kubernetes scheduler to run containers
   - Can run before scheduler has started
   - Unschedulable field of a node is not respected by DaemonSet controller

3. **Pod Configuration**
   - RestartPolicy can only be Always or left unspecified (defaults to Always)
   - This ensures container restart when liveness probe fails

4. **Priority**
   - Pods managed by DaemonSet are treated with higher priority
   - Descheduler will avoid evicting such Pods
   - Cluster autoscaler manages them separately

### Accessing DaemonSet Pods

There are several ways to reach Pods managed by DaemonSets:

1. **Service**
   - Create a Service with same Pod selector as DaemonSet
   - Use Service to reach daemon Pod load-balanced to random node

2. **DNS**
   - Create headless Service with same Pod selector
   - Retrieve multiple A records from DNS containing all Pod IPs and ports

3. **Node IP with hostPort**
   - Pods can specify hostPort to be reachable via node IP addresses
   - Combination of node IP, hostPort and protocol must be unique

4. **External Push**
   - Application in DaemonSet Pods can push data to external location/service
   - No consumer needs to reach DaemonSet Pods directly

### Static Pods

Another way to run containers similar to DaemonSet is through static Pods:

- Kubelet can get resource definitions from local directory
- Managed by Kubelet only and run on one node only
- API service doesn't observe these Pods
- No controller or health checks performed
- Kubelet watches and restarts them when they crash
- Kubelet scans configured directory for Pod definition changes

While static Pods can be used to run containerized Kubernetes system processes, DaemonSets are better integrated with the platform and are recommended over static Pods.

## Discussion

There are other ways to run daemon processes on every node, but they all have limitations:

- **Static Pods**: Managed by Kubelet but can't be managed through Kubernetes APIs
- **Bare Pods**: Can't survive accidental deletion/termination or node failure
- **Init Scripts**: Require different toolchains for monitoring and management

DaemonSet is somewhere between developer and administrator toolbox, inclining more toward the administrator side. However, it's relevant to application developers as it demonstrates how Kubernetes turns single-node concepts into multinode clustered primitives for managing distributed systems.

## More Information

- [Daemon Service Example](https://github.com/k8spatterns/examples/tree/main/behavioural/DaemonService)
- [DaemonSet Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Perform a Rolling Update on a DaemonSet](https://kubernetes.io/docs/tasks/manage-daemon/update-daemon-set/)
- [DaemonSets and Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/)
- [Create Static Pods](https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/)
