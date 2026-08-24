"""Permanent RFC 8785 vector suite (DEV-6 condition 2).

These vectors come from the RFC's own text (fetched 2026-08-24,
https://www.rfc-editor.org/rfc/rfc8785: Appendix B number samples given as
IEEE 754 bit patterns, and the section 3.2.3 rules), NOT from the library,
so they detect a behavioural change from ANY source: the rfc8785 package,
our code, or a Python version. They run forever, not once at adoption.
"""

import struct

import pytest
import rfc8785

from finding_bridge.core import dedup
from finding_bridge.core import provenance as prov

# RFC 8785 Appendix B: IEEE 754 double bit pattern -> required serialization.
RFC_NUMBER_VECTORS = [
    ("0000000000000000", "0"),  # zero
    ("8000000000000000", "0"),  # minus zero serializes as 0
    ("44b52d02c7e14af6", "1e+23"),
    ("3eb0c6f7a0b5ed8d", "0.000001"),
    ("41b3de4355555555", "333333333.3333333"),
]


@pytest.mark.parametrize("bits,expected", RFC_NUMBER_VECTORS)
def test_rfc_appendix_b_number_vectors(bits: str, expected: str):
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    assert rfc8785.dumps(value).decode("utf-8") == expected


def test_section_3_2_3_number_forms():
    """1E30 -> 1e+30, 4.50 -> 4.5, 2e-3 -> 0.002 (spec example values)."""
    assert rfc8785.dumps(1e30) == b"1e+30"
    assert rfc8785.dumps(4.50) == b"4.5"
    assert rfc8785.dumps(2e-3) == b"0.002"


def test_property_sort_is_utf16_code_units():
    """Spec: names sort as arrays of UTF-16 code units. A supplementary-
    plane key (high surrogate 0xD800) therefore sorts BEFORE U+E000 - the
    exact divergence DEV-2 named against Python's code-point sort, now
    resolved to the standard."""
    out = rfc8785.dumps({"": 1, "\U00010000": 2}).decode("utf-8")
    assert out.index("\U00010000") < out.index("")


def test_non_ascii_values_stay_raw_utf8():
    assert "é中\U0001f600".encode() in rfc8785.dumps({"k": "é中\U0001f600"})


def test_non_string_keys_raise_and_nothing_relies_on_leniency():
    """DEV-6 condition 4: the library raises on non-string keys instead of
    converting (the behaviour we want). Our hash inputs originate from JSON
    parsing or literal string-keyed dicts, so no code path relied on the
    old json.dumps leniency; this test guards that it stays true."""
    with pytest.raises(rfc8785.CanonicalizationError):
        rfc8785.dumps({1: "x"})


# --- our actual value space (DEV-6 condition 4) ---


def test_value_space_nulls_nested_floats_and_unicode():
    finding = {
        "severity": {"score": 6.0, "rationale": None},
        "reproduction": {"environment": {"note": "café 中\U0001f600", "n": None}},
        "harm_flags": [],
    }
    out = rfc8785.dumps(finding)
    assert b'"score":6' in out, "integral float serializes as integer per ECMA-262"
    assert b"null" in out
    assert "café".encode() in out


def test_integral_float_score_hashes_like_int():
    """Behavioural note from adoption, pinned: severity.score 6 and 6.0 now
    canonicalize identically (old form distinguished '6' from '6.0')."""
    a = {"severity": {"score": 6}}
    b = {"severity": {"score": 6.0}}
    assert prov.content_hash(a) == prov.content_hash(b)
    assert dedup.dedup_key({"id": "x", **a}) == dedup.dedup_key({"id": "x", **b})
