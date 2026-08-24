"""Human-gate identity resolution (D7, FULL tier).

Ruling D-011: confirmed_by is `git config user.name` + email. Director's D7
condition: if either is missing or empty, the gate refuses with its own
reason code and confirms nothing. It NEVER falls back to a default, an OS
username, or a placeholder. Writing of confirmed_by/confirmed_at/
attestation_hash happens only inside core/provenance.confirm; this module
only resolves the identity string.
"""

import subprocess

REASON_IDENTITY_MISSING = "identity-missing"


class GateError(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _git_config(key: str) -> str:
    try:
        result = subprocess.run(["git", "config", key], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise GateError(REASON_IDENTITY_MISSING, "git is not available") from exc
    return result.stdout.strip()


def get_git_identity() -> str:
    """The confirming human's identity, from git config only (D-011)."""
    name = _git_config("user.name")
    email = _git_config("user.email")
    if not name or not email:
        raise GateError(
            REASON_IDENTITY_MISSING,
            "git config user.name and user.email must both be set; the gate "
            "never falls back to a default identity",
        )
    return f"{name} <{email}>"
