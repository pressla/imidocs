# Periodic Job

The Periodic Job pattern extends the Batch Job pattern by adding a time dimension and allowing the execution of a unit of work to be triggered by a temporal event.

## Problem

In the world of distributed systems and microservices, there is a clear tendency toward real-time and event-driven application interactions using HTTP and lightweight messaging. However, regardless of the latest trends in software development, job scheduling has a long history, and it is still relevant. Periodic jobs are commonly used for automating system maintenance or administrative tasks. They are also relevant to business applications requiring specific tasks to be performed periodically. Typical examples here are business-to-business integration through file transfer, application integration through database polling, sending newsletter emails, and cleaning up and archiving old files.

The traditional way of handling periodic jobs for system maintenance purposes has been to use specialized scheduling software or cron. However, specialized software can be expensive for simple use cases, and cron jobs running on a single server are difficult to maintain and represent a single point of failure. That is why, very often, developers tend to implement solutions that can handle both the scheduling aspect and the business logic that needs to be performed.

For example, in the Java world, libraries such as Quartz, Spring Batch, and custom implementations with the ScheduledThreadPoolExecutor class can run temporal tasks. But similar to cron, the main difficulty with this approach is making the scheduling capability resilient and highly available, which leads to high resource consumption. Also, with this approach, the time-based job scheduler is part of the application, and to make the scheduler highly available, the whole application must be highly available. Typically, that involves running multiple instances of the application and at the same time ensuring that only a single instance is active and schedules jobs—which involves leader election and other distributed systems challenges.

In the end, a simple service that has to copy a few files once a day may end up requiring multiple nodes, a distributed leader election mechanism, and more. Kubernetes CronJob implementation solves all that by allowing scheduling of Job resources using the well-known cron format and letting developers focus only on implementing the work to be performed rather than the temporal scheduling aspect.

## Solution

A CronJob instance is similar to one line of a Unix crontab (cron table) and manages the temporal aspects of a Job. It allows the execution of a Job periodically at a specified point in time.

### Example CronJob Resource

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: random-generator
spec:
  schedule: "*/3 * * * *"  # Cron specification for running every three minutes
  jobTemplate:
    spec:
      template:            # Job template that uses the same specification as a regular Job
        spec:
          containers:
          - image: k8spatterns/random-generator:1.0
            name: random-generator
            command: [ "java", "RandomRunner", "/numbers.txt", "10000" ]
          restartPolicy: OnFailure
```

### Additional CronJob Fields

1. `.spec.schedule`
   - Crontab entry for specifying the Job's schedule
   - Can use shortcuts like @daily or @hourly

2. `.spec.startingDeadlineSeconds`
   - Deadline (in seconds) for starting the Job if it misses scheduled time
   - Don't use fewer than 10 seconds
   - Useful when task is only valid within certain timeframe

3. `.spec.concurrencyPolicy`
   - Manages concurrent executions of Jobs from same CronJob
   - Options:
     - Allow (default): Creates new Jobs even if previous not completed
     - Forbid: Skip next run if current one not completed
     - Replace: Cancel current Job and start new one

4. `.spec.suspend`
   - Suspends subsequent executions without affecting started executions
   - Different from Job's .spec.suspend

5. `.spec.successfulJobsHistoryLimit` and `.spec.failedJobsHistoryLimit`
   - Specify how many completed/failed Jobs to keep for auditing

## Discussion

A CronJob is a simple primitive that adds clustered, cron-like behavior to the existing Job definition. When combined with other primitives such as Pods, container resource isolation, and features like Automated Placement or Health Probe, it becomes a powerful job-scheduling system.

This enables developers to focus solely on the problem domain and implement a containerized application responsible only for the business logic. The scheduling is performed outside the application, as part of the platform with benefits like:
- High availability
- Resiliency
- Capacity management
- Policy-driven Pod placement

Similar to Job implementation, when implementing a CronJob container, your application must consider all corner and failure cases:
- Duplicate runs
- No runs
- Parallel runs
- Cancellations

## More Information

- [Periodic Job Example](https://github.com/k8spatterns/examples/tree/main/behavioural/PeriodicJob)
- [CronJob Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Cron](https://en.wikipedia.org/wiki/Cron)
- [Crontab Specification](https://en.wikipedia.org/wiki/Cron#CRON_expression)
- [Cron Expression Generator](https://www.freeformatter.com/cron-expression-generator-quartz.html)
