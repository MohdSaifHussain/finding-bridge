"""Governed output writing, shared by every emitter (S3-CLOSE-1, D-044).

The fifth instance of the exception-escapes-as-traceback class arrived on
the EXIT side: emit-markdown crashed raw on a missing parent directory
while emit-sarif silently created it. Ruling: the emitters agree - an
output path the user named is intent, not accident, so parents are
created; and a genuinely unwritable destination refuses with
output-unwritable, location-not-value as always (D-036).
"""

from pathlib import Path

REASON_OUTPUT_UNWRITABLE = "output-unwritable"


class OutputError(Exception):
    """Raised when an emit destination cannot be written; reason_code is
    machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def write_text_output(path: Path, text: str) -> None:
    """Write an emitted artifact, creating parents, refusing governed."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise OutputError(
            REASON_OUTPUT_UNWRITABLE,
            f"{path.name}: destination not writable ({type(exc).__name__})",
        ) from exc
