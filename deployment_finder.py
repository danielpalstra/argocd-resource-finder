#!/usr/bin/env python3

import click
from printer import ResourcePrinter
from k8s_client import K8sClient


@click.group()
def cli():
    """Tool for finding Kubernetes deployments based on ArgoCD management status."""
    pass

def get_resources(resource_type: str, managed: bool):
    """Generic function to get and print resources"""
    try:
        k8s_client = K8sClient()
        resources = k8s_client.get_all_resources(resource_type)
        printer = ResourcePrinter()
        printer.print_resources(resources, managed)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged deployments')
def list_deployments(managed: bool):
    """List deployments based on their ArgoCD management status."""
    get_resources('deployment', managed)

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged statefulsets')
def list_statefulsets(managed: bool):
    """List statefulsets based on their ArgoCD management status."""
    get_resources('statefulset', managed)

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged daemonsets')
def list_daemonsets(managed: bool):
    """List daemonsets based on their ArgoCD management status."""
    get_resources('daemonset', managed)

if __name__ == '__main__':
    cli()
