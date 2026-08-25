"""F-15 (STEP-07 P1): code-scanning alerts render only when the artifact URI
is repository-relative. GitHub's SARIF support doc (fetched 2026-08-25):
"Code scanning interprets results that are reported with relative paths
as relative to the root of the repository analyzed", with `%SRCROOT%` as
the uriBaseId convention and `originalUriBaseIds` declaring it.

Captured RED before the fix: no way to express a repository-relative
artifact path; the URI was the bare artifact name beside the SARIF, so
GitHub ingested 1 result and rendered 0 alerts (D-086 F6).
"""

import json
from pathlib import Path

from finding_bridge import cli, pipeline
from finding_bridge.adapters.out import sarif
from finding_bridge.core import provenance as prov

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def _confirmed() -> dict:
    f = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    if f["provenance"]["confirmed_by"] is None:
        f = prov.confirm(prov.stamp(f), "T <t@x.invalid>")
    return f


def test_repository_relative_uri_with_srcroot_when_base_given():
    log = sarif.render_sarif([_confirmed()], "findings.fb.jsonl", uri_base="out/dir")
    run = log["runs"][0]
    loc = run["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]
    assert loc["uri"] == "out/dir/findings.fb.jsonl"
    assert loc["uriBaseId"] == "%SRCROOT%"
    assert run["artifacts"][0]["location"]["uri"] == "out/dir/findings.fb.jsonl"
    assert run["artifacts"][0]["location"]["uriBaseId"] == "%SRCROOT%"
    assert "%SRCROOT%" in run["originalUriBaseIds"]
    # DEV-4: the disambiguation survives (the location is the RECORD, not a defect)
    assert run["properties"]["locationSemantics"] == sarif.LOCATION_SEMANTICS
    assert run["results"][0]["properties"]["locationSemantics"] == sarif.LOCATION_SEMANTICS


def test_no_base_keeps_the_sarif_relative_shape():
    log = sarif.render_sarif([_confirmed()], "findings.fb.jsonl")
    loc = log["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]
    assert loc["uri"] == "findings.fb.jsonl"
    assert "uriBaseId" not in loc
    assert "originalUriBaseIds" not in log["runs"][0]


def test_base_is_normalised_never_absolute_or_dot_dot():
    for bad in ("/abs/path", "C:/abs", "../up", "a/../b"):
        try:
            sarif.render_sarif([_confirmed()], "f.jsonl", uri_base=bad)
        except sarif.SarifAdapterError as exc:
            assert exc.reason_code == "invalid-uri-base"
        else:
            raise AssertionError(f"accepted {bad!r}")
    log = sarif.render_sarif([_confirmed()], "f.jsonl", uri_base="./x\\y/")
    assert log["runs"][0]["artifacts"][0]["location"]["uri"] == "x/y/f.jsonl"


def test_cli_flag_reaches_the_sarif(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store, key = repo / ".fb-store", tmp_path / "k" / "fb.key"
    ws = pipeline.Workspace(store, key, repo)
    ws.ingest_garak(FIXTURES / "garak.synthetic.hitlog.jsonl")
    ws.confirm(ws.list_candidates()[0]["id"], "T <t@x.invalid>")
    out = tmp_path / "o" / "findings.sarif"
    rc = cli.main(
        [
            "--store",
            str(store),
            "--key",
            str(key),
            "emit-sarif",
            str(out),
            "--artifact-uri-base",
            "examples/x/output",
        ]
    )
    assert rc == 0
    log = json.loads(out.read_text(encoding="utf-8"))
    loc = log["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]
    assert loc["uri"] == "examples/x/output/findings.fb.jsonl"
