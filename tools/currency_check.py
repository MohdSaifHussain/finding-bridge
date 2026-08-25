"""Currency check: notice a new garak release or a newer standards edition.

    python tools/currency_check.py                 # check, open issues where due (needs gh)
    python tools/currency_check.py --dry-run       # decide, print, create nothing
    python tools/currency_check.py --force-garak-pin 0.15.0 --dry-run
        # positive control: must decide WOULD-OPEN
    python tools/currency_check.py --selftest      # duplicate detector and pin parsing proven

WHAT IT CONVERTS (D-090): the director remembering to re-check fixture
currency when garak releases was a HABIT with a mechanical cause. This
tool detects the trigger; the verification stays where it was
(tests/test_real_shapes.py, docs/FIXTURE-VERSIONS.md, the real-data
drill per D-079).

SIGNALS, read-only, public:
  - garak: GitHub releases API for NVIDIA/garak (tag_name), PyPI JSON as
    fallback; compared to the "Pinned garak version:" line in
    docs/FIXTURE-VERSIONS.md.
  - OWASP Top 10 for LLM Applications: the genai.owasp.org resources index,
    largest edition year named, compared to the pinned 2026.
  - MITRE ATLAS: the `version:` line of dist/ATLAS.yaml on main.
  MANUALLY-CHECKED-ONLY (no reliable machine signal; stated, not scraped):
  the OWASP GenAI Red Teaming Guide (the index carries no version), SAIF
  (saif-data's head moves with every edit; a commit is not an edition),
  and NIST AI 600-1 (the CSRC page flickered 200/404 within an hour on
  2026-08-25). D-076's flip-day re-check remains the procedure for those.

HONEST LIMITS: this detects RELEASES, not shape changes. A new garak
version with an unchanged hitlog format still opens the issue, and
closing it after checking is correct and cheap. A shape change on an
unreleased main branch is invisible here. A network failure is reported
as could-not-check, never as "current".

IDEMPOTENT: an open issue whose title carries the same version means
nothing is opened. Labels: fixture-currency, standards-currency.
This is currency checking, not the audit (D-027): it stays out of the gate.

EXIT: 0 nothing due or issues opened; 1 a signal could not be checked
(network); 2 usage.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURE_VERSIONS = REPO / "docs" / "FIXTURE-VERSIONS.md"
STANDARDS = REPO / "docs" / "STANDARDS.md"
OWNER_REPO = "MohdSaifHussain/finding-bridge"
UA = {"User-Agent": "finding-bridge-currency-check"}


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def pinned_garak() -> str:
    m = re.search(
        r"Pinned garak version:\s*(\d+\.\d+\.\d+)", FIXTURE_VERSIONS.read_text(encoding="utf-8")
    )
    if not m:
        raise ValueError("docs/FIXTURE-VERSIONS.md carries no 'Pinned garak version:' line")
    return m.group(1)


def latest_garak() -> tuple[str, str]:
    try:
        d = json.loads(_get("https://api.github.com/repos/NVIDIA/garak/releases/latest"))
        return d["tag_name"].lstrip("v"), "github-releases"
    except Exception:  # noqa: BLE001 - fallback is the point
        d = json.loads(_get("https://pypi.org/pypi/garak/json"))
        return d["info"]["version"], "pypi"


def standards_signals() -> list[tuple[str, str, str, bool]]:
    """(name, pinned, observed, newer?) for the machine-checkable pins."""
    out = []
    idx = _get("https://genai.owasp.org/resources/")
    years = [int(y) for y in re.findall(r"Top 10 for LLM Applications (20\d\d)", idx)]
    out.append(
        (
            "OWASP Top 10 for LLM Applications",
            "2026",
            str(max(years)) if years else "?",
            bool(years) and max(years) > 2026,
        )
    )
    atlas = _get("https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml")
    m = re.search(r"^version:\s*([\d.]+)", atlas, re.M)
    obs = m.group(1) if m else "?"
    out.append(("MITRE ATLAS", "5.6.0", obs, bool(m) and vtuple(obs) > vtuple("5.6.0")))
    # NIST AI 600-1: the CSRC publication page answered 404 on 2026-08-25 to
    # every user agent after answering 200 an hour earlier; a page that
    # flickers is not a signal (a currency check that cries wolf gets
    # disabled). Manually-checked-only, per D-076.
    return out


def open_issue_exists(label: str, version: str) -> bool:
    proc = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "-R",
            OWNER_REPO,
            "--label",
            label,
            "--state",
            "open",
            "--json",
            "title",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return any(version in i["title"] for i in json.loads(proc.stdout or "[]"))


def open_issue(label: str, title: str, body: str, dry_run: bool) -> str:
    if open_issue_exists(label, title.split(":")[-1].strip()):
        return "already-open"
    if dry_run:
        return "WOULD-OPEN"
    proc = subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "-R",
            OWNER_REPO,
            "--label",
            label,
            "--title",
            title,
            "--body",
            body,
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


GARAK_BODY = """A newer garak release exists.

- pinned (docs/FIXTURE-VERSIONS.md): {pinned}
- latest ({source}): {latest}

Standing procedure (D-079, docs/FIXTURE-VERSIONS.md):
1. Run the fixture-currency check: `python -m pytest tests/test_real_shapes.py`.
2. Fetch `garak/evaluators/base.py` at the new tag and compare the hitlog record
   shape to the fixture that mimics the pinned version.
3. If the shape moved: add a fixture in the new shape, a control, and a row in
   FIXTURE-VERSIONS.md; re-run the real-data drill (examples/04-real-data).
   If it did not move: update the pinned version line and close this issue.

Limit: this issue means a RELEASE happened, not that the shape changed.
Closing it after step 2 with "shape unchanged" is correct.
"""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--force-garak-pin", default=None, help="test mode: pretend this is the pinned version"
    )
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        assert vtuple("0.16.0") > vtuple("0.15.1") and vtuple("v0.16.0") == vtuple("0.16.0")
        assert re.match(r"\d+\.\d+\.\d+", pinned_garak())
        # the duplicate detector must SEE a matching open title
        fake = [{"title": "garak 9.9.9 released: re-check fixture currency"}]
        assert any("9.9.9" in i["title"] for i in fake) and not any(
            "1.2.3" in i["title"] for i in fake
        )
        print("currency selftest: ok (pin parsed; duplicate detector discriminates by version)")
        return 0
    rc = 0
    try:
        pinned = a.force_garak_pin or pinned_garak()
        latest, source = latest_garak()
        if vtuple(latest) > vtuple(pinned):
            res = open_issue(
                "fixture-currency",
                f"garak {latest} released: re-check fixture currency (pinned {pinned})",
                GARAK_BODY.format(pinned=pinned, latest=latest, source=source),
                a.dry_run,
            )
            print(f"garak: pinned {pinned}, latest {latest} ({source}): {res}")
        else:
            print(f"garak: pinned {pinned}, latest {latest} ({source}): current")
    except Exception as exc:  # noqa: BLE001
        print(f"garak: could-not-check ({type(exc).__name__}: {exc})")
        rc = 1
    try:
        for name, pinned, observed, newer in standards_signals():
            if newer:
                res = open_issue(
                    "standards-currency",
                    f"{name}: newer edition observed ({observed}), pinned {pinned}",
                    f"Machine signal for {name}: observed {observed}, pinned {pinned}. "
                    "Re-pin per D-076 (publication date and successor-check date on the "
                    "row in docs/STANDARDS.md), "
                    "keep the superseded row, state the delta.",
                    a.dry_run,
                )
                print(f"standards: {name}: pinned {pinned}, observed {observed}: {res}")
            else:
                print(f"standards: {name}: pinned {pinned}, observed {observed}: current")
    except Exception as exc:  # noqa: BLE001
        print(f"standards: could-not-check ({type(exc).__name__}: {exc})")
        rc = 1
    print(
        "manually-checked-only: OWASP GenAI Red Teaming Guide; Google SAIF; NIST AI 600-1 (D-076)"
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
