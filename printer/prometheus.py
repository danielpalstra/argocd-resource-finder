from typing import List, Optional, Dict
from collections import defaultdict
from pathlib import Path
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from printer.console import ResourceInfo

class PrometheusMetricsPrinter:
    def __init__(self):
        """Initialize the Prometheus metrics printer."""
        self.registry = CollectorRegistry()
        
        # Create a gauge metric for ArgoCD managed resources
        self.argocd_resource_managed = Gauge(
            'argocd_resource_managed',
            'Whether a resource is managed by ArgoCD (1) or not (0)',
            ['name', 'namespace', 'type'],
            registry=self.registry
        )
        
        # Create gauge metrics for namespace totals
        self.argocd_namespace_managed_total = Gauge(
            'argocd_namespace_managed_total',
            'Total number of resources managed by ArgoCD in a namespace',
            ['namespace'],
            registry=self.registry
        )
        
        self.argocd_namespace_unmanaged_total = Gauge(
            'argocd_namespace_unmanaged_total',
            'Total number of resources not managed by ArgoCD in a namespace',
            ['namespace'],
            registry=self.registry
        )

    def _reset_metrics(self):
        """Reset all metrics before updating."""
        self.argocd_resource_managed._metrics.clear()
        self.argocd_namespace_managed_total._metrics.clear()
        self.argocd_namespace_unmanaged_total._metrics.clear()
    
    def _calculate_namespace_totals(self, resources: List[ResourceInfo]) -> Dict[str, Dict[str, int]]:
        """Calculate the total number of managed and unmanaged resources per namespace.
        
        Args:
            resources: List of ResourceInfo objects
            
        Returns:
            Dictionary with namespace as key and counts as value
        """
        namespace_totals = defaultdict(lambda: {'managed': 0, 'unmanaged': 0})
        
        for resource in resources:
            if resource.is_argocd_managed:
                namespace_totals[resource.namespace]['managed'] += 1
            else:
                namespace_totals[resource.namespace]['unmanaged'] += 1
                
        return namespace_totals
    
    def _create_resource_metrics(self, resources: List[ResourceInfo]):
        """Create metrics for individual resources.
        
        Args:
            resources: List of ResourceInfo objects
        """
        for resource in resources:
            self.argocd_resource_managed.labels(
                name=resource.name,
                namespace=resource.namespace,
                type=resource.resource_type
            ).set(1 if resource.is_argocd_managed else 0)
    
    def _create_namespace_total_metrics(self, namespace_totals: Dict[str, Dict[str, int]]):
        """Create metrics for namespace totals.
        
        Args:
            namespace_totals: Dictionary with namespace totals
        """
        for namespace, counts in namespace_totals.items():
            self.argocd_namespace_managed_total.labels(namespace=namespace).set(counts['managed'])
            self.argocd_namespace_unmanaged_total.labels(namespace=namespace).set(counts['unmanaged'])
    
    def print_resources(self, resources: List[ResourceInfo], managed: Optional[bool] = None, output_file: Optional[str] = None):
        """Generate Prometheus metrics for resources.
        
        Args:
            resources: List of ResourceInfo objects
            managed: Whether to show managed or unmanaged resources
            output_file: Path to the output metrics file
            
        Returns:
            String containing the generated metrics
        """
        # Filter resources if managed flag is provided
        filtered_resources = resources if managed is None else [r for r in resources if r.is_argocd_managed == managed]
        
        # Reset all metrics before updating
        self._reset_metrics()
        
        # Calculate namespace totals
        namespace_totals = self._calculate_namespace_totals(filtered_resources)
        
        # Create metrics
        self._create_resource_metrics(filtered_resources)
        self._create_namespace_total_metrics(namespace_totals)
        
        # Generate metrics output
        metrics_output = generate_latest(self.registry).decode('utf-8')
        
        # Write to file if output_file is provided
        if output_file:
            with open(output_file, 'w') as f:
                f.write(metrics_output)
            
        return metrics_output
