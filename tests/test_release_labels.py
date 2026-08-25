"""W7 release labels: the SARIF driver states facts a test ties to their source.

F-14: canonicalSchemaVersion was a hard-coded "0.4.0" after the schema
moved to 0.5.0; nothing tied it to the schema. Now it reads the schema's
constant, and this test fails if the two ever part. informationUri is
the repository's own URL (OB-7 prepared; resolvable only after the flip).
"""

import json
from pathlib import Path

from finding_bridge import __version__
from finding_bridge.adapters.out import sarif
from finding_bridge.core import provenance as prov
from finding_bridge.core.schema import load_schema

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def _driver() -> dict:
    f = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    if f["provenance"]["confirmed_by"] is None:
        f = prov.confirm(prov.stamp(f), "T <t@x.invalid>")
    return sarif.render_sarif([f], "f.jsonl")["runs"][0]["tool"]["driver"]


def test_sarif_schema_version_label_is_the_schema_constant():
    d = _driver()
    assert (
        d["properties"]["canonicalSchemaVersion"]
        == load_schema()["properties"]["schema_version"]["const"]
    )


def test_sarif_driver_version_and_information_uri():
    d = _driver()
    assert d["version"] == __version__ == "1.0.0"
    assert d["informationUri"] == "https://github.com/MohdSaifHussain/finding-bridge"


def test_pyproject_version_matches_package():
    import tomllib

    py = tomllib.loads(
        (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert py["project"]["version"] == __version__
