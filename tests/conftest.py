"""Shared test infrastructure: key-env scrub + guard (R-10, contract 3.1).

The autouse session fixture removes every key-bearing environment variable
before any test runs, so the whole suite exercises the pipeline exactly as it
must work: with zero API keys (charter rule 1). The guard function lets tests
prove the scrub happened rather than assert it happened.
"""

import os

import pytest

KEY_ENV_MARKERS = ("API_KEY", "APIKEY")


def visible_key_vars() -> list[str]:
    """Names of environment variables that look key-bearing."""
    return sorted(n for n in os.environ if any(m in n.upper() for m in KEY_ENV_MARKERS))


@pytest.fixture(autouse=True, scope="session")
def _scrub_key_env_vars():
    """Contract 3.1: the suite runs with key-bearing env vars scrubbed."""
    removed = {name: os.environ.pop(name) for name in visible_key_vars()}
    yield
    os.environ.update(removed)
