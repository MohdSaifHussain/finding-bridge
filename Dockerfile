# finding-bridge container (STEP-06 W6). Multi-stage: the builder makes the
# wheel; the runtime installs only that wheel, hash-checked, and runs as a
# non-root user with `finding-bridge` as the entrypoint.
#
# BASE IMAGE, DIGEST-PINNED. python:3.12-slim resolved to the OCI image
# index below on 2026-08-25T07:15:05Z, read back from Docker Hub's registry
# API (docker-content-digest header of /v2/library/python/manifests/3.12-slim;
# the local Docker daemon was not running, so the pull-side read-back is
# the CI build, which fails if the digest does not match). Both stages use
# the same pinned base so Dependabot's docker ecosystem sees one line to bump.
#
# THE KEY IS NEVER IN THE IMAGE. Nothing here copies, generates, or bakes a
# sealing key. The key file is mounted at run time (see container.yml's
# smoke row and SOP.md section 1). The layer scan in container.yml proves
# it: no *.key, no fb.key, no Fernet-shaped token in any layer.

FROM python:3.14-slim@sha256:cae66f2ef0ec51a9891263eeee7f987dacf0a9879e8aa9353d5606e0530619a5 AS builder
WORKDIR /src
COPY pyproject.toml constraints.txt LICENSE NOTICE README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir --upgrade pip build \
 && python -m build --wheel --outdir /wheels

FROM python:3.14-slim@sha256:cae66f2ef0ec51a9891263eeee7f987dacf0a9879e8aa9353d5606e0530619a5 AS runtime
LABEL org.opencontainers.image.title="finding-bridge" \
      org.opencontainers.image.description="Turn AI red-team tool output into standard, sealed, provenance-stamped findings" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.source="https://github.com/MohdSaifHussain/finding-bridge"
# git is REQUIRED at run time: the human gate records confirmed_by from
# `git config user.name/email` (D-011) and never falls back to a default.
# Without it, confirm and unseal refuse with identity-missing (F-8, found by
# the local W6 smoke). Mount your gitconfig read-only:
#   -v "$HOME/.gitconfig:/home/fb/.gitconfig:ro"
RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*
RUN groupadd --system fb && useradd --system --gid fb --create-home --home-dir /home/fb fb
COPY --from=builder /wheels /wheels
COPY constraints.txt /tmp/constraints.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/constraints.txt \
 && python -m pip install --no-cache-dir --no-deps /wheels/finding_bridge-*.whl \
 && python -m pip check \
 && rm -rf /wheels /tmp/constraints.txt
USER fb
WORKDIR /work
# The store and key are mounted; nothing is persisted inside the image.
#   docker run --rm -v "$PWD/store:/work/store" -v "$PWD/key:/home/fb/key" \
#     -v "$HOME/.gitconfig:/home/fb/.gitconfig:ro" \
#     ghcr.io/mohdsaifhussain/finding-bridge --store /work/store --key /home/fb/key/fb.key list
ENTRYPOINT ["finding-bridge"]
CMD ["--help"]
