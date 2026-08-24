"""Canonical schema loading and validation with format ASSERTION enabled.

Per ruling D-020: JSON Schema 2020-12 makes `format` annotation-only by
default (Validation spec section 7: implementations "MUST provide options to
enable and disable such evaluation and MUST be disabled by default"; section
7.2.1), and python-jsonschema's date-time check "requires the
rfc3339-validator package... Without it, validation succeeds silently"
(sources fetched 2026-08-24:
https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-00,
https://python-jsonschema.readthedocs.io/en/stable/validate/). A provenance
timestamp nothing checks is a silence-shaped failure, so every validator this
project uses goes through this module, with the format checker on.

Honest limit: the schema file is resolved relative to the repo tree, which
holds for the editable install this project uses (charter: pip install -e .);
a wheel install would need the schema packaged as data. Carried in the phase
outcome.
"""

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

REASON_SCHEMA_INVALID = "schema-invalid"

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "finding.schema.json"


class SchemaValidationError(Exception):
    """Raised when a finding fails canonical-schema validation."""

    def __init__(self, detail: str):
        self.reason_code = REASON_SCHEMA_INVALID
        self.detail = detail
        super().__init__(f"{REASON_SCHEMA_INVALID}: {detail}")


@lru_cache(maxsize=1)
def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def validate_finding(finding: dict) -> None:
    """Validate a finding against the canonical schema, formats asserted.

    Raises SchemaValidationError (reason code schema-invalid) on failure.
    """
    try:
        _validator().validate(finding)
    except ValidationError as exc:
        # D-036: ValidationError.message embeds the offending instance value,
        # and instance values can be untrusted source content. The detail
        # names the path and the failed keyword, never the value.
        raise SchemaValidationError(
            f"at {exc.json_path}: fails '{exc.validator}' (offending value withheld per D-036)"
        ) from exc
