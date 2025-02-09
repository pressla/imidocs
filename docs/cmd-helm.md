# Helm Commands Guide

This guide demonstrates common Helm commands using `grafana/grafana` as an example.

## Adding a Helm Repository

To add a Helm repository:

```bash
# Add the Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts

# Update the repository to fetch the latest charts
helm repo update
```

## Searching for Chart Versions

To search for available versions of a chart:

```bash
# List all available versions of Grafana
helm search repo grafana/grafana --versions

# Example output:
# NAME            VERSION    APP VERSION    DESCRIPTION
# grafana/grafana 6.58.8    10.1.5         The leading tool for querying and visualizing t...
# grafana/grafana 6.58.7    10.1.5         The leading tool for querying and visualizing t...
# grafana/grafana 6.58.6    10.1.4         The leading tool for querying and visualizing t...
```

## Pulling Charts

To download and extract a chart in one command:

```bash
# Pull and automatically extract a specific version of Grafana chart
helm pull grafana/grafana --version 6.58.8 --untar

# This will create a 'grafana' directory containing the chart files
# You can examine or modify these files before installation
```

## Installing Charts

There are several ways to install a Helm chart:

### Basic Installation

```bash
# Install with default values
helm install my-grafana grafana/grafana
```

### Installation with Custom Values

```bash
# Install with custom values file
helm install my-grafana grafana/grafana -f custom-values.yaml

# Install with specific version
helm install my-grafana grafana/grafana --version 6.58.8

# Install with set values
helm install my-grafana grafana/grafana \
  --set service.type=NodePort \
  --set persistence.enabled=true \
  --set persistence.size=10Gi
```

### Useful Installation Options

- `--namespace`: Install in a specific namespace
- `--create-namespace`: Create the namespace if it doesn't exist
- `--dry-run`: Simulate the installation
- `--debug`: Enable verbose output

Example with multiple options:

```bash
helm install my-grafana grafana/grafana \
  --namespace monitoring \
  --create-namespace \
  --set persistence.enabled=true \
  --set adminPassword=admin123 \
  --version 6.58.8
```

## Additional Useful Commands

```bash
# List installed releases
helm list --all-namespaces

# Get release status
helm status my-grafana

# Uninstall a release
helm uninstall my-grafana

# Get release values
helm get values my-grafana

# Upgrade a release
helm upgrade my-grafana grafana/grafana --reuse-values --version 6.58.9
```
