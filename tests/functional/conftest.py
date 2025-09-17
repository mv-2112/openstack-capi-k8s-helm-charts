# SPDX-FileCopyrightText: 2025 - Canonical Ltd
# SPDX-License-Identifier: Apache-2.0

import secrets
import string
from pathlib import Path

import pytest

from . import utils


def pytest_addoption(parser):
    parser.addoption(
        "--helm-repo-path",
        action="store",
        help="Helm repo path that hosts openstack-cluster",
    )
    parser.addoption(
        "--openstack-cluster-chart-version",
        action="store",
        help="openstack-cluster chart version",
        default="0.1.0",
    )


@pytest.fixture(scope="session")
def helm_repo_path(request) -> str:
    return request.config.getoption("helm_repo_path")


@pytest.fixture(scope="session")
def openstack_cluster_chart_version(request) -> str:
    return request.config.getoption("openstack_cluster_chart_version")


@pytest.fixture(scope="session")
def unique_id() -> str:
    """Unique id to use as suffix

    This ID is used as suffix for namespace, cluster name, keypair,
    application credential to identify them easily in the deployed
    environment.
    """
    length = 8
    # Use ascii_lowercase to follow k8s naming convention for release names etc
    random_string = "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )
    return random_string


@pytest.fixture(scope="session")
def config_path(tmp_path_factory) -> Path:
    """Temporary directory to place all generated files."""
    path = tmp_path_factory.mktemp("config")
    return path


@pytest.fixture(scope="session")
def value_overrides(config_path, unique_id) -> dict:
    """Return values yaml to create cluster."""
    return utils.generate_values(config_path, unique_id)


@pytest.fixture(scope="session")
def setup():
    """Add tags to image."""
    # Add property tags to image
    cmd = [
        "openstack",
        "image",
        "set",
        "ubuntu",
        "--os-distro",
        "ubuntu",
        "--os-version",
        "24.04",
        "--property",
        "kube_version=v1.32.6",
    ]
    utils.run_openstack_command(utils.CLOUD_ADMIN, cmd, capture_output=False)
