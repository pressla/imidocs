# Kubectl Common Commands Cheatsheet

| Command | Description | Example |
|---------|-------------|---------|
| `kubectl get services -n <namespace>` | Lists services in a namespace (omit -n for current namespace) | `kubectl get services -n kube-system` |
| `kubectl get namespaces` | Lists all namespaces in the cluster | `kubectl get namespaces` |
| `kubectl get pods -n <namespace>` | Lists pods in a namespace (omit -n for current namespace) | `kubectl get pods -n default` |
| `kubectl get pods -o wide` | Lists pods with additional details including node name and IP | `kubectl get pods -o wide` |
| `kubectl get pods --watch` | Watch real-time changes to pods | `kubectl get pods --watch` |
| `kubectl get ingress -n <namespace>` | Lists ingress resources in a namespace (omit -n for current namespace) | `kubectl get ingress -n default` |
| `kubectl describe pod <pod-name>` | Shows detailed information about a specific pod | `kubectl describe pod nginx-pod` |
| `kubectl describe service <service-name>` | Shows detailed information about a specific service | `kubectl describe service my-service` |
| `kubectl logs <pod-name>` | Shows logs for a specific pod | `kubectl logs nginx-pod` |
| `kubectl logs -f <pod-name>` | Follows/streams logs for a specific pod | `kubectl logs -f nginx-pod` |
| `kubectl logs <pod-name> -c <container-name>` | Shows logs for a specific container in a pod | `kubectl logs nginx-pod -c nginx` |
| `kubectl exec <pod-name> -- env` | Lists all environment variables in a pod | `kubectl exec nginx-pod -- env` |
| `kubectl apply -f <file>` | Creates/updates resources defined in a file | `kubectl apply -f deployment.yaml` |
| `kubectl apply -f <directory>` | Creates/updates resources defined in all files in a directory | `kubectl apply -f ./configs` |
| `kubectl cluster-info` | Displays cluster information | `kubectl cluster-info` |
| `kubectl cluster-info dump` | Dumps cluster state for debugging | `kubectl cluster-info dump` |
| `kubectl rollout restart deployment <deployment-name>` | Restarts all pods in a deployment | `kubectl rollout restart deployment nginx-deployment` |
| `kubectl rollout status deployment <deployment-name>` | Shows the status of a deployment rollout | `kubectl rollout status deployment nginx-deployment` |
| `kubectl delete pod <pod-name> -n <namespace>` | Deletes a pod in a namespace (omit -n for current namespace) | `kubectl delete pod nginx-pod -n default` |
| `kubectl delete deployment <deployment-name>` | Deletes a deployment and its pods | `kubectl delete deployment nginx-deployment` |
| `kubectl delete service <service-name>` | Deletes a service | `kubectl delete service my-service` |
| `kubectl delete -f <file>` | Deletes resources defined in a file | `kubectl delete -f deployment.yaml` |
| `kubectl delete -l key=value` | Deletes resources matching a label | `kubectl delete pods -l app=nginx` |
| `kubectl delete all --all -n <namespace>` | Deletes all resources in a namespace | `kubectl delete all --all -n test-namespace` |
