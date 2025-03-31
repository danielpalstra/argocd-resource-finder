import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from deployment_finder import cli
from printer import ResourceInfo

@pytest.fixture
def mock_k8s_client():
    with patch('deployment_finder.K8sClient') as mock:
        yield mock

@pytest.fixture
def cli_runner():
    return CliRunner()

def test_list_deployments_with_managed_resources(cli_runner, mock_k8s_client):
    # Setup mock resources
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.return_value = [
        ResourceInfo("dep1", "ns1", True, "deployment", "app1"),
        ResourceInfo("dep2", "ns2", True, "deployment", "app2"),
    ]

    # Test managed resources
    result = cli_runner.invoke(cli, ['list-deployments', '--managed'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "dep2" in result.output
    assert "ns1" in result.output
    assert "app1" in result.output

def test_list_deployments_with_unmanaged_resources(cli_runner, mock_k8s_client):
    # Setup mock resources
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.return_value = [
        ResourceInfo("dep1", "ns1", False, "deployment", "N/A"),
        ResourceInfo("dep2", "ns2", True, "deployment", "app2"),
    ]

    # Test unmanaged resources
    result = cli_runner.invoke(cli, ['list-deployments', '--unmanaged'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "dep2" not in result.output
    assert "N/A" in result.output

def test_list_deployments_with_no_resources(cli_runner, mock_k8s_client):
    # Setup mock with empty resources
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.return_value = []

    # Test with no resources
    result = cli_runner.invoke(cli, ['list-deployments', '--managed'])
    assert result.exit_code == 0
    assert "No managed resources found" in result.output

def test_list_deployments_with_api_error(cli_runner, mock_k8s_client):
    # Setup mock to raise an exception
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.side_effect = Exception("API Error")

    # Test error handling
    result = cli_runner.invoke(cli, ['list-deployments', '--managed'])
    assert result.exit_code != 0
    assert "API Error" in result.output

def test_list_deployments_mixed_resources(cli_runner, mock_k8s_client):
    # Setup mock with mixed resources
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.return_value = [
        ResourceInfo("dep1", "ns1", True, "deployment", "app1"),
        ResourceInfo("dep2", "ns2", False, "deployment", "N/A"),
        ResourceInfo("dep3", "ns3", True, "deployment", "app3"),
        ResourceInfo("dep4", "ns4", False, "deployment", ""),
    ]

    # Test managed resources
    result = cli_runner.invoke(cli, ['list-deployments', '--managed'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "dep3" in result.output
    assert "dep2" not in result.output
    assert "dep4" not in result.output

    # Test unmanaged resources
    result = cli_runner.invoke(cli, ['list-deployments', '--unmanaged'])
    assert result.exit_code == 0
    assert "dep2" in result.output
    assert "dep4" in result.output
    assert "dep1" not in result.output
    assert "dep3" not in result.output
