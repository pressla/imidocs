# Behavioral Patterns

The patterns in this category are focused on the communications and interactions between the Pods and the managing platform. Depending on the type of managing controller used, a Pod may run until completion or be scheduled to run periodically. It can run as a daemon or ensure uniqueness guarantees to its replicas. There are different ways to run a Pod on Kubernetes, and picking the right Pod-management primitives requires understanding their behavior.

In the following chapters, we explore the patterns:

- Chapter 7, "Batch Job", describes how to isolate an atomic unit of work and run it until completion.
- Chapter 8, "Periodic Job", allows the execution of a unit of work to be triggered by a temporal event.
- Chapter 9, "Daemon Service", allows you to run infrastructure-focused Pods on specific nodes, before application Pods are placed.
- Chapter 10, "Singleton Service", ensures that only one instance of a service is active at a time and still remains highly available.
- Chapter 11, "Stateless Service", describes the building blocks used for managing identical application instances.
- Chapter 12, "Stateful Service", is all about how to create and manage distributed stateful applications with Kubernetes.
- Chapter 13, "Service Discovery", explains how client services can discover and consume the instances of providing services.
- Chapter 14, "Self Awareness", describes mechanisms for introspection and metadata injection into applications.
