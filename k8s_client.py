from typing import List
import click
from kubernetes import client, config
from printer import ResourceInfo

class K8sClient:
    def __init__(self):
        try:
            config.load_kube_config()
        except Exception:
            config.load_incluster_config()
        self.api = client.AppsV1Api()

    def _get_argocd_managed_status(self, labels: dict) -> bool:
        return (labels or {}).get('argocd.argoproj.io/instance') is not None

    def get_all_resources(self, resource_type: str) -> List[ResourceInfo]:
        resources = []
        try:
            if resource_type == 'deployment':
                items = self.api.list_deployment_for_all_namespaces().items
            elif resource_type == 'statefulset':
                items = self.api.list_stateful_set_for_all_namespaces().items
            elif resource_type == 'daemonset':
                items = self.api.list_daemon_set_for_all_namespaces().items
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")

            for item in items:
                is_argocd_managed = self._get_argocd_managed_status(item.metadata.labels)
                resources.append(ResourceInfo(
                    name=item.metadata.name,
                    namespace=item.metadata.namespace,
                    is_argocd_managed=is_argocd_managed,
                    resource_type=resource_type
                ))
        except Exception as e:
            click.echo(f"Error fetching {resource_type}s: {e}", err=True)
            raise
        return resources
