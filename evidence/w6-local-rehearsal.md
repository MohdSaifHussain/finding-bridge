# W6 local rehearsal (STEP-06, 2026-08-25, before the first push)

Director's instruction: rehearse the container locally so CI's first run is
a confirmation, not a discovery. Docker Desktop was started for it
(Docker version 29.7.2). Every command below was run on this machine;
outputs quoted from the scratch captures `w6-rehearsal-*.txt`.

## 1. Base digest, first half of the measured-not-remembered pair

```
$ docker pull python:3.12-slim@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
Status: Image is up to date for python@sha256:3ecf5ebe...
$ docker image inspect <pin> --format 'RepoDigests={{.RepoDigests}} os/arch={{.Os}}/{{.Architecture}}'
RepoDigests=[python@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d] os/arch=linux/amd64
$ docker pull python:3.12-slim   (the floating tag, today)
[python@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d]
```

The digest the registry API returned on 2026-08-25T07:15:05Z, the digest
this machine's pull resolved, and the digest the floating tag resolved to
the same day are one value. CI's read-back step (container.yml) is the
second half, on the runner that pulls.

## 2. Build: two findings before CI ever ran

**F-7, the lock was incomplete on Python 3.12.** First build failed inside
the image: `ERROR: In --require-hashes mode, all requirements must have
their versions pinned with ==. These do not: typing-extensions>=4.4.0
... (from referencing==0.37.0)`. The lock's versions were resolved in a
Python 3.14 venv, where `referencing` has no such dependency; the 3.12
image exposed the conditional one. Fixed: `typing-extensions==4.16.0`
pinned for every Python (tools/lock.py PINS, 12 packages, 280 hashes);
dry-run in the 3.12 image passes for both LF and CRLF copies of the file.
Along the way the working copy was found to carry CRLF (autocrlf); pip
tolerated it (measured: CRLF dry-run exit 0), so `.gitattributes` forcing
LF on machine-parsed files is hardening, not the fix, and says so.

**F-8, the image could not run the human gate.** First smoke: `unseal`
inside the container refused with `identity-missing: git is not
available`. The gate takes identity from `git config` (D-011) and never
falls back, and the slim base has no git. Fixed: git installed in the
runtime stage (image 53,270,166 to 88,050,644 bytes), the operator mounts
a gitconfig read-only; documented in the Dockerfile and the SOP.

Final build: `sha256:f54f85f48cce4998ced8040a3c2546d44bcd977ed86bcb57a4af1ca9d0b25a5d`,
`user=fb entrypoint=[finding-bridge]`.

## 3. Layer scan: the first scan was blind, and its control said so

The shell scan (`tar -tf` over the saved archive, grep for token shapes)
reported "no key-shaped file in any layer" while its own positive control
reported `SCAN BLIND`: Git Bash's tar took `C:` for a remote host and the
OCI blobs are gzip, which grep cannot read. That is the rule-5 discipline
paying for itself: a scan whose positive control fails proves nothing,
and it was not believed. Replaced by `tools/layer_scan.py` (tarfile +
gzip, keyring JSON SHAPE markers, name markers, selftest). Its first
candidate run flagged the tool's own `sealing.py` for carrying the field
name `"ref_key"`: a precision defect, fixed by matching the JSON shape
(name, colon, quoted 20+ char value), which source code does not have.

```
$ python tools/layer_scan.py --selftest
LAYER SCAN SELFTEST: ok (planted keyring found by name and by marker)
$ python tools/layer_scan.py planted.tar        (a `docker save` of FROM scratch + COPY fb.key)
LAYER SCAN: KEY MATERIAL FOUND (1 layers)
  6d298603139f: key-shaped file fb.key
[exit 1]
$ python tools/layer_scan.py planted2.tar       (a REAL keyring copied in as /opt/notakey.txt)
LAYER SCAN: KEY MATERIAL FOUND (1 layers)
  a7f22924b29d: keyring-shaped JSON inside opt/notakey.txt
[exit 1]
$ python tools/layer_scan.py image.tar          (the candidate)
LAYER SCAN: CLEAN (10 layers; no key-shaped file, no keyring marker)
[exit 0]
```

## 4. Smoke row, with the key and a gitconfig mounted from outside

```
$ run ingest-garak in/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
$ run list            (three candidates, safe metadata previews, one duplicate marked)
$ run confirm fb-0194cd19e0a7fec1
confirmed fb-0194cd19e0a7fec1 by smoke-operator <smoke@example.invalid>
$ run verify
chain verifies clean
$ run emit-markdown store/packet.md
wrote store/packet.md
$ run unseal sealed/34db864a73f9a56a
unseal-not-explicit: unseal of 'sealed/34db864a73f9a56a' requires explicit=True (charter: unsealing is always explicit and logged)
-- explicit unseal, not captured into out.txt:
SENTINEL-HARM-7001 synthetic harmful response stand-in, not real model output
no sealed sentinel on stdout across ingest/list/confirm/verify/emit/refused-unseal
```

`fb.key` was created in the mounted folder, outside the image.

## Limits

Single machine, linux/amd64 via Docker Desktop; the arm64 manifest in the
same index was not exercised. The GHCR push and the package's visibility
are CI-only and are verified after the first run.
