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

def test_list_deployments_show_all_by_default(cli_runner, mock_k8s_client):
    # Setup mock resources
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.return_value = [
        ResourceInfo("dep1", "ns1", True, "deployment", "app1"),
        ResourceInfo("dep2", "ns2", False, "deployment", "Not ArgoCD Managed"),
    ]

    # Test showing all resources (default)
    result = cli_runner.invoke(cli, ['list-deployments'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "dep2" in result.output
    assert "ns1" in result.output
    assert "ns2" in result.output
    assert "app1" in result.output
    assert "Not ArgoCD Managed" in result.output

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
        ResourceInfo("dep1", "ns1", False, "deployment", "Not ArgoCD Managed"),
        ResourceInfo("dep2", "ns2", True, "deployment", "app2"),
    ]

    # Test unmanaged resources
    result = cli_runner.invoke(cli, ['list-deployments', '--unmanaged'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "dep2" not in result.output
    assert "Not ArgoCD Managed" in result.output

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
    assert result.exit_code == 0  # Should not exit with error
    assert "API Error" in result.output

def test_list_deployments_mixed_resources(cli_runner, mock_k8s_client):
    # Setup mock with mixed resources
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.return_value = [
        ResourceInfo("dep1", "ns1", True, "deployment", "app1"),
        ResourceInfo("dep2", "ns2", False, "deployment", "Not ArgoCD Managed"),
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

def test_list_all_show_all_by_default(cli_runner, mock_k8s_client):
    # Setup mock with mixed resource types
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.side_effect = [
        # Deployments
        [
            ResourceInfo("dep1", "ns1", True, "deployment", "app1"),
            ResourceInfo("dep2", "ns2", False, "deployment", "Not ArgoCD Managed"),
        ],
        # StatefulSets
        [
            ResourceInfo("sts1", "ns1", True, "statefulset", "app2"),
        ],
        # DaemonSets
        [
            ResourceInfo("ds1", "ns3", False, "daemonset", "Not ArgoCD Managed"),
        ]
    ]

    # Test showing all resources (default)
    result = cli_runner.invoke(cli, ['list-all'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "dep2" in result.output
    assert "sts1" in result.output
    assert "ds1" in result.output

def test_list_all_resources(cli_runner, mock_k8s_client):
    # Setup mock with mixed resource types
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.side_effect = [
        # Deployments
        [
            ResourceInfo("dep1", "ns1", True, "deployment", "app1"),
            ResourceInfo("dep2", "ns2", False, "deployment", "Not ArgoCD Managed"),
        ],
        # StatefulSets
        [
            ResourceInfo("sts1", "ns1", True, "statefulset", "app2"),
        ],
        # DaemonSets
        [
            ResourceInfo("ds1", "ns3", False, "daemonset", "Not ArgoCD Managed"),
        ]
    ]

    # Test managed resources
    result = cli_runner.invoke(cli, ['list-all', '--managed'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "sts1" in result.output
    assert "ds1" not in result.output
    assert "dep2" not in result.output

    # Test unmanaged resources
    result = cli_runner.invoke(cli, ['list-all', '--unmanaged'])
    assert result.exit_code == 0
    assert "dep2" in result.output
    assert "ds1" in result.output
    assert "dep1" not in result.output
    assert "sts1" not in result.output

def test_list_all_with_api_error(cli_runner, mock_k8s_client):
    # Setup mock to raise an exception for one resource type
    mock_instance = mock_k8s_client.return_value
    mock_instance.get_all_resources.side_effect = [
        # Deployments succeed
        [ResourceInfo("dep1", "ns1", True, "deployment", "app1")],
        # StatefulSets fail
        Exception("API Error for StatefulSets"),
        # DaemonSets succeed
        [ResourceInfo("ds1", "ns3", True, "daemonset", "app3")]
    ]

    # Test that we continue even if one resource type fails
    result = cli_runner.invoke(cli, ['list-all'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "ds1" in result.output
    assert "API Error for StatefulSets" in result.output

    # Test with managed filter
    result = cli_runner.invoke(cli, ['list-all', '--managed'])
    assert result.exit_code == 0
    assert "dep1" in result.output
    assert "ds1" in result.output
    
    # Test with unmanaged filter
    result = cli_runner.invoke(cli, ['list-all', '--unmanaged'])
    assert result.exit_code == 0
    assert "dep1" not in result.output
    assert "ds1" not in result.output
