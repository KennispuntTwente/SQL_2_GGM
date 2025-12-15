"""Repo-wide pytest configuration.

This file applies to all tests in the repository (including package-level
`*/tests` folders). It is intentionally minimal and focuses on integration-test
hygiene.
"""

from __future__ import annotations

import os

import pytest


# Make shared fixtures/helpers from tests.integration_utils available everywhere.
pytest_plugins = ["tests.integration_utils"]


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db_containers_session():
    """Clean up ggmpilot test DB containers before and after the session.

    CI failures due to "port is already allocated" or inability to start new
    containers are often caused by leftover `*-docker-db-*` containers/volumes
    from previous runs. This cleanup is best-effort and only runs when:

    - Docker is reachable, and
    - either `RUN_SLOW_TESTS` is enabled or we are in CI.

    To opt out locally, set `GGMPILOT_KEEP_TEST_CONTAINERS=1`.
    """

    from tests.integration_utils import (
        cleanup_all_test_db_containers,
        docker_running,
        slow_tests_enabled,
    )

    # In pytest-xdist, this session fixture would run in every worker process.
    # Only run the global cleanup in the master/controller process to avoid
    # workers deleting containers used by other workers.
    if os.getenv("PYTEST_XDIST_WORKER"):
        yield
        return

    if _truthy_env("GGMPILOT_KEEP_TEST_CONTAINERS"):
        yield
        return

    should_cleanup = docker_running() and (slow_tests_enabled() or _truthy_env("CI"))
    if should_cleanup:
        cleanup_all_test_db_containers()

    yield

    if should_cleanup:
        cleanup_all_test_db_containers()
