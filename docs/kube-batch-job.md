# Batch Job

The Batch Job pattern is suited for managing isolated atomic units of work. It is based on the Job resource, which runs short-lived Pods reliably until completion on a distributed environment.

## Problem

The main primitive in Kubernetes for managing and running containers is the Pod. There are different ways of creating Pods with varying characteristics:

**Bare Pod**  
It is possible to create a Pod manually to run containers. However, when the node such a Pod is running on fails, the Pod is not restarted. Running Pods this way is discouraged except for development or testing purposes. This mechanism is also known as unmanaged or naked Pods.

**ReplicaSet**  
This controller is used for creating and managing the lifecycle of Pods expected to run continuously (e.g., to run a web server container). It maintains a stable set of replica Pods running at any given time and guarantees the availability of a specified number of identical Pods. ReplicaSets are described in detail in Chapter 11, "Stateless Service".

**DaemonSet**  
This controller runs a single Pod on every node and is used for managing platform capabilities such as monitoring, log aggregation, storage containers, and others. See Chapter 9, "Daemon Service", for a more detailed discussion.

A common aspect of these Pods is that they represent long-running processes that are not meant to stop after a certain time. However, in some cases there is a need to perform a predefined finite unit of work reliably and then shut down the container. For this task, Kubernetes provides the Job resource.

## Solution

A Kubernetes Job is similar to a ReplicaSet as it creates one or more Pods and ensures they run successfully. However, the difference is that, once the expected number of Pods terminate successfully, the Job is considered complete, and no additional Pods are started.

### Example Job Specification

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: random-generator
spec:
  completions: 5                 # Job should run five Pods to completion, which all must succeed
  parallelism: 2                 # Two Pods can run in parallel
  ttlSecondsAfterFinished: 300   # Keep Pods for five minutes (300 seconds) before garbage-collecting them
  template:
    metadata:
      name: random-generator
    spec:
      restartPolicy: OnFailure   # Specifying the restartPolicy is mandatory for a Job
      containers:
      - image: k8spatterns/random-generator:1.0
        name: random-generator
        command: [ "java", "RandomRunner", "/numbers.txt", "10000" ]
```

One crucial difference between the Job and the ReplicaSet definition is the `.spec.template.spec.restartPolicy`. The default value for a ReplicaSet is Always, which makes sense for long-running processes that must always be kept running. The value Always is not allowed for a Job, and the only possible options are OnFailure or Never.

### Benefits of Using Jobs Over Bare Pods

1. A Job is not an ephemeral in-memory task but a persisted one that survives cluster restarts.

2. When a Job is completed, it is not deleted but is kept for tracking purposes. The Pods that are created as part of the Job are also not deleted but are available for examination (e.g., to check the container logs).

3. A Job may need to be performed multiple times. Using the `.spec.completions` field, it is possible to specify how many times a Pod should complete successfully before the Job itself is done.

4. When a Job has to be completed multiple times, it can also be scaled and executed by starting multiple Pods at the same time using the `.spec.parallelism` field.

5. A Job can be suspended by setting the field `.spec.suspend` to true. In this case, all active Pods are deleted and restarted if the Job is resumed.

6. If the node fails or when the Pod is evicted for some reason while still running, the scheduler places the Pod on a new healthy node and reruns it.

### Types of Jobs

Based on the completions and parallelism parameters, there are the following types of Jobs:

**Single Pod Jobs**  
- Leave out both `.spec.completions` and `.spec.parallelism` or set them to their default values of 1
- Starts only one Pod and is completed when the single Pod terminates successfully

**Fixed Completion Count Jobs**  
- Set `.spec.completions` to the number of completions needed
- Can set `.spec.parallelism` or leave it unset (defaults to 1)
- Completed after the `.spec.completions` number of Pods has completed successfully

**Work Queue Jobs**  
- Leave `.spec.completions` unset
- Set `.spec.parallelism` to a number greater than one
- Completed when at least one Pod has terminated successfully and all other Pods have terminated
- Requires Pods to coordinate among themselves

**Indexed Jobs**  
- Similar to Work queue Jobs but without needing an external work queue
- Uses fixed completion count and `.spec.completionMode` set to Indexed
- Each Pod gets an index from 0 to `.spec.completions - 1`
- Index available through annotation or JOB_COMPLETION_INDEX environment variable

### Example Indexed Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: file-split
spec:
  completionMode: Indexed     # Enable indexed completion mode
  completions: 5              # Run five Pods in parallel to completion
  parallelism: 5
  template:
    metadata:
      name: file-split
    spec:
      containers:
      - image: alpine
        name: split
        command:              # Execute shell script to process file ranges
        - "sh"
        - "-c"
        - |
          start=$(expr $JOB_COMPLETION_INDEX \* 10000)      
          end=$(expr $JOB_COMPLETION_INDEX \* 10000 + 10000)
          awk "NR>=$start && NR<$end" /logs/random.log \    
              > /logs/random-$JOB_COMPLETION_INDEX.txt
        volumeMounts:         # Mount input data from external volume
        - mountPath: /logs    
          name: log-volume
      restartPolicy: OnFailure
```

## Discussion

The Job abstraction is a basic but fundamental primitive that other primitives such as CronJobs are based on. Jobs help turn isolated work units into a reliable and scalable unit of execution. However, a Job doesn't dictate how you should map individually processable work items into Jobs or Pods. That is something you have to determine after considering the pros and cons of each option:

**One Job per work item**  
- Has overhead of creating Kubernetes Jobs
- Platform has to manage large number of Jobs consuming resources
- Useful when each work item is a complex task that needs independent tracking

**One Job for all work items**  
- Right for large number of work items that don't need independent tracking
- Work items managed from within application via batch framework

The Job primitive provides only the minimum basics for scheduling work items. Any complex implementation has to combine the Job primitive with a batch application framework (e.g., Spring Batch, JBeret) to achieve the desired outcome.

Not all services must run all the time. Using Jobs can run Pods only when needed and only for the duration of the task execution. Jobs are scheduled on nodes that have the required capacity, satisfy Pod placement policies, and take into account other container dependency considerations. Using Jobs for short-lived tasks rather than long-running abstractions saves resources for other workloads on the platform.

## More Information

- [Batch Job Example](https://github.com/k8spatterns/examples/tree/main/behavioural/BatchJob)
- [Jobs Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Parallel Processing Using Expansions](https://kubernetes.io/docs/tasks/job/parallel-processing-expansion/)
- [Coarse Parallel Processing Using a Work Queue](https://kubernetes.io/docs/tasks/job/coarse-parallel-processing-work-queue/)
- [Fine Parallel Processing Using a Work Queue](https://kubernetes.io/docs/tasks/job/fine-parallel-processing-work-queue/)
- [Indexed Job for Parallel Processing](https://kubernetes.io/docs/tasks/job/indexed-parallel-processing-static/)
- [Spring Batch on Kubernetes](https://spring.io/blog/2018/12/10/spring-batch-on-kubernetes)
- [JBeret Introduction](https://jberet.gitbooks.io/jberet-user-guide/content/)
