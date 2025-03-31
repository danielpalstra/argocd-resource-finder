#!/usr/bin/env python3

import click
from printer import ResourcePrinter
from html_printer import HTMLPrinter
from k8s_client import K8sClient


@click.group()
def cli():
    """Tool for finding Kubernetes deployments based on ArgoCD management status."""
    pass

def get_resources(resource_type: str, managed: bool, output_format: str = 'text', output_file: str = None):
    """Generic function to get and print resources"""
    try:
        k8s_client = K8sClient()
        resources = k8s_client.get_all_resources(resource_type)
        if output_format == 'html' and output_file:
            printer = HTMLPrinter()
            printer.print_resources(resources, managed, output_file)
        else:
            printer = ResourcePrinter()
            printer.print_resources(resources, managed)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged deployments')
@click.option('--output', '-o', type=click.Choice(['text', 'html']), default='text',
              help='Output format (text or html)')
@click.option('--output-file', '-f', type=str,
              help='Output file for HTML format')
def list_deployments(managed: bool, output: str, output_file: str):
    """List deployments based on their ArgoCD management status."""
    if output == 'html' and not output_file:
        raise click.UsageError('--output-file is required when using HTML output')
    get_resources('deployment', managed, output, output_file)

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged statefulsets')
@click.option('--output', '-o', type=click.Choice(['text', 'html']), default='text',
              help='Output format (text or html)')
@click.option('--output-file', '-f', type=str,
              help='Output file for HTML format')
def list_statefulsets(managed: bool, output: str, output_file: str):
    """List statefulsets based on their ArgoCD management status."""
    if output == 'html' and not output_file:
        raise click.UsageError('--output-file is required when using HTML output')
    get_resources('statefulset', managed, output, output_file)

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged daemonsets')
@click.option('--output', '-o', type=click.Choice(['text', 'html']), default='text',
              help='Output format (text or html)')
@click.option('--output-file', '-f', type=str,
              help='Output file for HTML format')
def list_daemonsets(managed: bool, output: str, output_file: str):
    """List daemonsets based on their ArgoCD management status."""
    if output == 'html' and not output_file:
        raise click.UsageError('--output-file is required when using HTML output')
    get_resources('daemonset', managed, output, output_file)

@cli.command()
@click.option('--managed/--unmanaged', default=False,
              help='Show ArgoCD managed/unmanaged resources')
@click.option('--output', '-o', type=click.Choice(['text', 'html']), default='text',
              help='Output format (text or html)')
@click.option('--output-file', '-f', type=str,
              help='Output file for HTML format')
def list_all(managed: bool, output: str, output_file: str):
    """List all resources (deployments, statefulsets, and daemonsets) based on their ArgoCD management status."""
    if output == 'html' and not output_file:
        raise click.UsageError('--output-file is required when using HTML output')
    
    k8s_client = K8sClient()
    all_resources = []
    
    for resource_type in ['deployment', 'statefulset', 'daemonset']:
        try:
            resources = k8s_client.get_all_resources(resource_type)
            all_resources.extend(resources)
        except Exception as e:
            click.echo(f"Error fetching {resource_type}s: {e}", err=True)
    
    if output == 'html' and output_file:
        printer = HTMLPrinter()
        printer.print_resources(all_resources, managed, output_file)
    else:
        printer = ResourcePrinter()
        printer.print_resources(all_resources, managed)

if __name__ == '__main__':
    cli()
