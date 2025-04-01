# ArgoCD Deployment Finder

A tool to find Kubernetes deployments based on their ArgoCD management status.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

To find deployments not managed by ArgoCD:
```bash
python deployment_finder.py list-deployments --unmanaged
```

To find deployments managed by ArgoCD:
```bash
python deployment_finder.py list-deployments --managed
```

Note: The tool requires access to a Kubernetes cluster and will use your current kubeconfig context.

## Docker

### Build

Build the Docker image

```bash

docker build -t argocd-deployment-finder .
```

### Run

Use the kubeconfig from the custom-contexts directory in the container

```bash
docker run --rm -it -e KUBECONFIG=/root/.kube/custom-contexts/nerd.yaml -v $HOME/.kube/custom-contexts:/root/.kube/custom-contexts:ro argocd-deployment-finder list-all
```
