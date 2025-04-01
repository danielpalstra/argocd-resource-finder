import os
import pytest
from unittest.mock import patch, MagicMock
from kubernetes.config import ConfigException
from k8s_client import K8sClient
from printer.console import ResourceInfo

def test_init_with_local_config():
    with patch('kubernetes.config.load_kube_config') as mock_local_config:
        client = K8sClient()
        mock_local_config.assert_called_once()

def test_init_with_incluster_config():
    with patch('kubernetes.config.load_kube_config', side_effect=Exception('Local config failed')), \
         patch('kubernetes.config.load_incluster_config') as mock_incluster_config:
        client = K8sClient()
        mock_incluster_config.assert_called_once()

def test_init_with_directory_error():
    with patch('kubernetes.config.load_kube_config', side_effect=IsADirectoryError('[Errno 21] Is a directory: \'/root/.kube/custom-contexts\'')), \
         patch('click.echo') as mock_echo:
        with pytest.raises(SystemExit) as excinfo:
            client = K8sClient()
        assert excinfo.value.code == 1
        mock_echo.assert_called_once_with(
            "Error loading kube config - directory found instead of file: [Errno 21] Is a directory: '/root/.kube/custom-contexts'",
            err=True
        )

def test_init_both_configs_fail():
    with patch('kubernetes.config.load_kube_config', side_effect=Exception('Local config failed')), \
         patch('kubernetes.config.load_incluster_config', side_effect=Exception('Incluster config failed')), \
         patch('click.echo') as mock_echo:
        with pytest.raises(Exception):
            client = K8sClient()
        mock_echo.assert_called_once_with(
            "Failed to load both local and in-cluster config: Local config failed and Incluster config failed",
            err=True
        )

def test_init_with_config_exception():
    with patch('kubernetes.config.load_kube_config', side_effect=ConfigException('Invalid kube-config file. No configuration found.')), \
         patch('kubernetes.config.load_incluster_config', side_effect=Exception('Service host/port is not set.')), \
         patch('click.echo') as mock_echo:
        with pytest.raises(SystemExit) as excinfo:
            client = K8sClient()
        assert excinfo.value.code == 1
        # Check that both error messages were logged
        assert mock_echo.call_count == 2
        mock_echo.assert_any_call(
            "Invalid kube-config file: Invalid kube-config file. No configuration found.",
            err=True
        )
        mock_echo.assert_any_call(
            "Failed to load both local and in-cluster config: Invalid kube-config file. No configuration found. and Service host/port is not set.",
            err=True
        )

@patch('kubernetes.config.load_kube_config')
@patch('kubernetes.config.load_incluster_config')
def test_get_argocd_managed_status(mock_incluster_config, mock_load_kube_config):
    # Mock the Kubernetes client initialization
    client = K8sClient()
    
    # Test with ArgoCD managed resource
    labels = {'argocd.argoproj.io/instance': 'my-app'}
    is_managed, label_value = client._get_argocd_managed_status(labels)
    assert is_managed is True
    assert label_value == 'my-app'

    # Test with non-ArgoCD managed resource
    labels = {'app': 'test'}
    is_managed, label_value = client._get_argocd_managed_status(labels)
    assert is_managed is False
    assert label_value == 'Not ArgoCD Managed'

    # Test with None labels
    is_managed, label_value = client._get_argocd_managed_status(None)
    assert is_managed is False
    assert label_value == 'Not ArgoCD Managed'
