from typing import List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from printer.console import ResourceInfo

class HTMLPrinter:
    def __init__(self):
        template_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.template = self.env.get_template('resources.html')

    def print_resources(self, resources: List[ResourceInfo], managed: bool = None, output_file: str = None):
        """Print resources to an HTML file.
        
        Args:
            resources: List of ResourceInfo objects
            managed: Whether to show managed or unmanaged resources
            output_file: Path to the output HTML file
        """
        filtered_resources = resources if managed is None else [r for r in resources if r.is_argocd_managed == managed]
        
        html_content = self.template.render(
            resources=filtered_resources,
            managed=managed
        )
        
        with open(output_file, 'w') as f:
            f.write(html_content)
