"""R-10 / contract 3.1: the suite scrubs key-bearing env vars and proves it.

The scrub itself lives in tests/conftest.py (autouse, session-scoped). These
tests prove the guard sees a leaked variable (negative control) and that the
pipeline's environment is clean after the scrub (positive control).
"""

import os

from conftest import KEY_ENV_MARKERS, visible_key_vars


def test_no_key_bearing_env_vars_visible():
    """Positive control: after the autouse scrub, nothing key-bearing is
    visible to any code under test."""
    assert visible_key_vars() == []


def test_guard_detects_injected_key():
    """Negative control: the guard can fail; it is not vacuously green."""
    os.environ["FAKE_SERVICE_API_KEY"] = "dummy"
    try:
        assert "FAKE_SERVICE_API_KEY" in visible_key_vars()
    finally:
        del os.environ["FAKE_SERVICE_API_KEY"]


def test_markers_cover_known_providers():
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        assert any(marker in name for marker in KEY_ENV_MARKERS)
