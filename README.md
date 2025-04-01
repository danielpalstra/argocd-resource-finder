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

## Testing

### Running Tests Locally

To run tests locally, first activate the virtual environment:

```bash
source .venv/bin/activate
```

Then run the tests:

```bash
python -m pytest
```

To generate a code coverage report:

```bash
python -m pytest --cov=./ --cov-report=term
```

### GitHub Actions

This repository includes GitHub Actions workflows for:

1. **Automated Testing**: Runs the test suite on multiple Python versions (3.8, 3.9, 3.10) on every push to main and pull request.

2. **Code Coverage**: Generates a code coverage report and uploads it to Codecov on every push to main and pull request.

3. **Docker Build and Push**: Builds and pushes the Docker image to DockerHub on pushes to main and when tags are created.
