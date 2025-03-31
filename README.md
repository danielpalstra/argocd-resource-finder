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
