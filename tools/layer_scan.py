"""Layer scan: prove no key material is in a container image (STEP-06 W6).

    docker save <image> -o image.tar
    python tools/layer_scan.py image.tar      # 0 clean, 1 key material found, 2 could not run
    python tools/layer_scan.py --selftest     # a planted keyring MUST be found

WHAT IT LOOKS FOR, in every layer of a `docker save` archive (OCI layout,
blobs plain or gzip):
  - key-shaped FILE NAMES: fb.key, *.key, exposure_log.jsonl;
  - keyring JSON MARKERS in any file's bytes: "ref_key", "encryption_keys",
    "keyring_version" (the three fields of this tool's key file).

WHY A TOOL AND NOT A GREP: the first local scan (2026-08-25) grepped the
outer tar with shell tar and reported "no key material" while its own
positive control reported SCAN BLIND: Git Bash's tar took `C:` for a
remote host, and the OCI blobs are gzip, which grep cannot read. A scan
that cannot see a planted key proves nothing, so the positive control is
built in (--selftest plants one and must find it) and CI runs it before
the real scan.

WHAT A PASS DOES NOT PROVE: that no secret of any other shape is present.
It proves the named shapes are absent. Fernet tokens are not matched by
shape alone (44 base64url chars ending '=' collide with ordinary base64
in stdlib data); the keyring's field names are the discriminating signal.
"""

from __future__ import annotations

import gzip
import io
import re
import sys
import tarfile
import tempfile
from pathlib import Path

EXIT_CLEAN, EXIT_FOUND, EXIT_COULD_NOT_RUN = 0, 1, 2
NAME_RE = re.compile(r"(^|/)(fb\.key|[^/]*\.key|exposure_log\.jsonl)$")
# The keyring's JSON SHAPE, not its field names: the tool's own source
# carries the names (sealing.py builds the dict), and the first candidate
# scan flagged it. A key file has the name, a colon, and a quoted value
# or a list of quoted values; source code does not.
MARKERS = (
    re.compile(rb'"ref_key"\s*:\s*"[A-Za-z0-9_=-]{20,}"'),
    re.compile(rb'"encryption_keys"\s*:\s*\[\s*"[A-Za-z0-9_=-]{20,}"'),
    re.compile(rb'"keyring_version"\s*:\s*\d'),
)


def _open_layer(raw: bytes) -> tarfile.TarFile | None:
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    try:
        return tarfile.open(fileobj=io.BytesIO(raw))
    except tarfile.TarError:
        return None


def scan(archive: Path) -> tuple[list[str], int]:
    """Return (problems, layers_scanned)."""
    problems: list[str] = []
    layers = 0
    with tarfile.open(archive) as outer:
        for member in outer.getmembers():
            if not member.isfile() or not member.name.startswith("blobs/"):
                continue
            raw = outer.extractfile(member).read()
            layer = _open_layer(raw)
            if layer is None:
                continue  # config / manifest JSON blobs
            layers += 1
            for m in layer.getmembers():
                if NAME_RE.search(m.name):
                    problems.append(f"{member.name[-12:]}: key-shaped file {m.name}")
                if m.isfile() and m.size <= 1_000_000:
                    data = layer.extractfile(m).read()
                    for marker in MARKERS:
                        if marker.search(data):
                            problems.append(
                                f"{member.name[-12:]}: keyring-shaped JSON inside {m.name}"
                            )
                            break
    return problems, layers


def _plant(tmp: Path) -> Path:
    """Build a docker-save-shaped archive holding one gzip layer with a keyring."""
    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w") as t:
        payload = (
            b'{"keyring_version": 1, "ref_key": "' + b"A" * 44 + b'", '
            b'"encryption_keys": ["' + b"B" * 44 + b'"]}'
        )
        info = tarfile.TarInfo("home/fb/key/fb.key")
        info.size = len(payload)
        t.addfile(info, io.BytesIO(payload))
    blob = gzip.compress(inner.getvalue())
    out = tmp / "planted.tar"
    with tarfile.open(out, mode="w") as outer:
        info = tarfile.TarInfo("blobs/sha256/planted")
        info.size = len(blob)
        outer.addfile(info, io.BytesIO(blob))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "usage: layer_scan.py <docker-save.tar> | --selftest; there is no override",
            file=sys.stderr,
        )
        return EXIT_COULD_NOT_RUN
    if argv[1] == "--selftest":
        with tempfile.TemporaryDirectory() as d:
            problems, layers = scan(_plant(Path(d)))
        if layers != 1 or len(problems) < 2:
            print(f"LAYER SCAN SELFTEST: BLIND ({layers} layers, {problems})")
            return EXIT_COULD_NOT_RUN
        print("LAYER SCAN SELFTEST: ok (planted keyring found by name and by marker)")
        return EXIT_CLEAN
    archive = Path(argv[1])
    if not archive.is_file():
        print(f"could-not-run: {archive} is not a file", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        problems, layers = scan(archive)
    except (tarfile.TarError, OSError, EOFError) as exc:
        print(f"could-not-run: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if layers == 0:
        print("could-not-run: no layers found (is this a docker save archive?)", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if problems:
        print(f"LAYER SCAN: KEY MATERIAL FOUND ({layers} layers)")
        for p in problems:
            print(f"  {p}")
        return EXIT_FOUND
    print(f"LAYER SCAN: CLEAN ({layers} layers; no key-shaped file, no keyring marker)")
    return EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
