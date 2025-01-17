## Purpose

The purpose of this document is to describe the additional system requirements and steps to deploy the Single-Node RKE2 Kubernetes Distribution.

## Pre-requisites for Single-Node Installation

The prerequisites and pre-deployment phases are describe in the [RKE2 Pre-Deployment & Installation Guide (Single & Multi Node)](<../../cx/4.3/rke2-pre-deployment-installation-guide-single-mu-1>). Please complete the steps before proceeding with Single-Node Installation.
Quick Links
Installation Steps
Customize the RKE2 Deployment for your Environment
Click here to see customization steps.....
Below given options can also be used for customized environment setup:

| Option | Switch | Default | Description |
| --- | --- | --- | --- |
| Default POD IP Assignment Range |  |  |  |

| "10.42.0.0/16" | IPv4/IPv6 network CIDRs to use for pod IPs |  |  |
| --- | --- | --- | --- |
| Default Service IP Assignment Range | service-cidr value | "10.43.0.0/16" | IPv4/IPv6 network CIDRs to use for service IPs |

![image](../__theme/images/common/note-macro-icon--625ed763b7218abfc3ad.svg)
cluster-cidr and service-cidr are independently evaluated. Decide wisely well before the the cluster deployment. This option is not configurable once the cluster is deployed and workload is running.

### Step 1: Enable Customization for Ingress-Nginx

This step is required for the Nginx Ingress Controller to allow customized configurations:
1. Create the destination folder
```bash
mkdir -p  /var/lib/rancher/rke2/server/manifests/
```

2. Generate the ingress-nginx controller config file so that the RKE2 server bootstraps it accordingly.
```bash
cat<<EOF| tee /var/lib/rancher/rke2/server/manifests/rke2-ingress-nginx-config.yaml
```

    ---
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: rke2-ingress-nginx
  namespace: kube-system
  spec:
    valuesContent: |-
    controller:
      metrics:
        service:
          annotations:
            prometheus.io/scrape: "true"
            prometheus.io/port: "10254"
            config:
              use-forwarded-headers: "true"
              allowSnippetAnnotations: "true"
```

    EOF

### Step 2: Download the RKE2 binaries and start Installation

1. Run the below command on the master node. RKE2 will be installed on the master node.
```bash
curl -sfL https://get.rke2.io |INSTALL_RKE2_TYPE=server  sh -
```

2. Enable the rke2-server service
```bash
systemctl enable rke2-server.service
```

3. Start the service
```bash
systemctl start rke2-server.service
```

![image](../__theme/images/common/note-macro-icon--625ed763b7218abfc3ad.svg)
RKE2 server requires 10-15 minutes (at least) to bootstrap completely You can check the status of the RKE2 Server using` systemctl status rke2-server`; once it reports as running, please proceed with the rest of the steps as given below.
4. By default, RKE2 deploys all the binaries in `/var/lib/rancher/rke2/bin` path. Add this path to the system's default PATH for kubectl utility to work appropriately.
```bash
export PATH=$PATH:/var/lib/rancher/rke2/bin
```

```bash
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
```

5. Also, append these lines into the current user's `.bashrc` file
```bash
echo "export PATH=$PATH:/var/lib/rancher/rke2/bin" >> $HOME/.bashrc
```

```bash
echo "export KUBECONFIG=/etc/rancher/rke2/rke2.yaml"  >> $HOME/.bashrc
```

6. and source your `~/.bashrc`
```bash
source ~/.bashrc
```

### Step 3: Bash Completion for kubectl

1. Install bash-completion package
```bash
yum install bash-completion -y
```

```bash
2\. Set-up autocomplete in bash into the current shell, `bash-completion `package should be installed first.
```

```bash
source <(kubectl completion bash)
```

```bash
echo "source <(kubectl completion bash)" >> ~/.bashrc
```

3. Also, add alias for short notation of kubectl
```bash
echo "alias k=kubectl"  >> ~/.bashrc
```

```bash
echo "complete -o default -F __start_kubectl k"  >> ~/.bashrc
```

4. and source your `~/.bashrc`
```bash
source ~/.bashrc
```

### Step 4: Install helm

1. Add this command in ~/.bashrc file.
```bash
echo "export KUBECONFIG=/etc/rancher/rke2/rke2.yaml" >> ~/.bashrc
```

2. run this in the command prompt.
```bash
source ~/.bashrc
```

3. Helm is a super tool to deploy external components. In order to install helm on cluster, execute the following command:
```bash
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3|bash
```

```bash
cd /usr/local/bin
```

```bash
mkdir -p $HOME/bin && cp ./helm $HOME/bin/helm && export PATH=$HOME/bin:$PATH
```

4. Move to the root
```bash
cd /root
```

### Step 5: Enable bash completion for helm

```bash
1\. Generate the scripts for help bash completion
```

```bash
helm completion bash > /etc/bash_completion.d/helm
```

2. Either re-login or run this command to enable the helm bash completion instantly.
```bash
source <(helm completion bash)
```

## Step 6: Clone the CIM Repo

Use the following command for CIM Repo:
```bash
git clone -b <branch-name>  https://efcx:RecRpsuH34yqp56YRFUb@gitlab.expertflow.com/cim/cim-solution.git
```

and replace the branch name with actual release.

### Step 7: Storage for RKE2 Single-Node Installation

The recommended storage option for RKE2 Single-Node Installation is to use OpenEBS. The details of deployment of OpenEBS can be found in this [document](<../../cx/4.3/openebs-local-storage-solution>).

### Step 8: CIM Deployment on Kubernetes

Please follow the steps in the document, [Expertflow CX Deployment on Kubernetes](<../../cx/4.3/expertflow-cx-deployment-on-kubernetes>) to deploy Expertflow CX Solution.