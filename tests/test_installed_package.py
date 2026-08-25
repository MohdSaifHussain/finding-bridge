"""W2c control: prove which copy of the package the tests import.

In the fresh-venv proof the suite must run against the INSTALLED package
(site-packages), not the source tree. This test reports the truth either
way and asserts only when FB_EXPECT_INSTALLED=1 is set, so it is a
control in the venv run and a fact-printer in the normal run.
"""

import os

import finding_bridge


def test_import_location_is_as_expected():
    location = finding_bridge.__file__
    expect_installed = os.environ.get("FB_EXPECT_INSTALLED") == "1"
    print(f"finding_bridge imported from: {location}")
    if expect_installed:
        assert "site-packages" in location.replace("\\", "/"), (
            f"expected the installed package, imported {location}"
        )


def test_package_data_ships_with_install():
    """The W2b fix: schema + field map must load from wherever the package
    lives, including a wheel install."""
    from finding_bridge.core.schema import load_field_map, load_schema

    assert load_schema()["$schema"].endswith("2020-12/schema")
    assert load_field_map()["canonical_schema_version"] == "0.5.0"
