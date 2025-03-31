from typing import List
import click
from dataclasses import dataclass

@dataclass
class ResourceInfo:
    name: str
    namespace: str
    is_argocd_managed: bool
    resource_type: str
    label_value: str

class ResourcePrinter:
    @staticmethod
    def print_resources(resources: List[ResourceInfo], show_managed: bool = False):
        filtered_resources = [r for r in resources if r.is_argocd_managed == show_managed]
        
        if not filtered_resources:
            status = "managed" if show_managed else "unmanaged"
            click.echo(f"No {status} resources found.")
            return

        click.echo(f"{'TYPE':<15} {'NAMESPACE':<20} {'NAME':<40} {'LABEL VALUE':<20}")
        click.echo("-" * 95)
        for resource in filtered_resources:
            click.echo(f"{resource.resource_type:<15} {resource.namespace:<20} {resource.name:<40} {resource.label_value:<20}")
