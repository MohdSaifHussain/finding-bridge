"""D-060's mechanical half: no verify path compares digests inline.

The helper (provenance.digests_match) closes the comparison-weakening
class for code that USES it. This test finds code that bypasses it, by
walking the AST rather than grepping text, so a bypass cannot hide behind
formatting.
"""

import ast
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from finding_bridge.core import provenance as prov

CORE = Path(__file__).resolve().parent.parent / "src" / "finding_bridge" / "core"

# Names that hold a digest. A comparison between two of these with == or
# != is the class this rule exists to prevent.
DIGEST_NAMES = {
    "content_hash",
    "attestation_hash",
    "head_hash",
    "prev_hash",
    "expected_prev",
    "recomputed",
    "stored",
    "attestation",
    "expected",
    "digest",
}

# The helper itself and its stated exception must be allowed to compare.
ALLOWED_FUNCTIONS = {"digests_match", "_prev_link_ok"}


def digest_ish(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return node.id in DIGEST_NAMES
    if isinstance(node, ast.Attribute):
        return node.attr in DIGEST_NAMES
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return node.slice.value in DIGEST_NAMES
    if isinstance(node, ast.Call):
        # record.get("content_hash") and friends
        for arg in node.args:
            if isinstance(arg, ast.Constant) and arg.value in DIGEST_NAMES:
                return True
    return False


def inline_digest_comparisons(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef) or func.name in ALLOWED_FUNCTIONS:
            continue
        for node in ast.walk(func):
            if not isinstance(node, ast.Compare):
                continue
            if not any(isinstance(op, ast.Eq | ast.NotEq) for op in node.ops):
                continue
            operands = [node.left, *node.comparators]
            if sum(digest_ish(o) for o in operands) >= 2:
                offenders.append(
                    f"{path.name}:{node.lineno} in {func.name}(): "
                    "digests compared inline; use digests_match()"
                )
    return offenders


@pytest.mark.parametrize("path", sorted(CORE.glob("*.py")), ids=lambda p: p.name)
def test_no_inline_digest_comparison_in_core(path: Path):
    offenders = inline_digest_comparisons(path)
    assert not offenders, "\n".join(offenders)


def test_the_bypass_check_can_fail(tmp_path: Path):
    """The check proves it can fail (skill rule 5): a planted bypass in a
    file of the same shape must be caught."""
    planted = tmp_path / "planted.py"
    planted.write_text(
        "def verify(stored, recomputed):\n    if stored != recomputed:\n        return False\n",
        encoding="utf-8",
    )
    assert inline_digest_comparisons(planted), "a planted inline comparison was not caught"


# --- the both-orderings property, tested ONCE, against the helper ---


@settings(deadline=None, max_examples=200)
@given(
    a=st.text(alphabet="0123456789abcdef", min_size=64, max_size=64),
    b=st.text(alphabet="0123456789abcdef", min_size=64, max_size=64),
)
def test_digests_match_is_true_exactly_when_equal(a: str, b: str):
    """Property: the helper is true iff the digests are equal, in BOTH
    orderings. A weakened comparison (< or >) fails this for the half of
    generated pairs on its losing side - which is exactly the class that
    escaped three hand-written verify paths."""
    assert prov.digests_match(a, b) == (a == b)
    assert prov.digests_match(b, a) == (a == b)


def test_digests_match_treats_none_as_no_claim():
    assert prov.digests_match(None, None) is False
    assert prov.digests_match("a" * 64, None) is False
    assert prov.digests_match(None, "a" * 64) is False


def test_prev_link_allows_both_absent_only():
    assert prov._prev_link_ok(None, None) is True
    assert prov._prev_link_ok("a" * 64, None) is False
    assert prov._prev_link_ok("a" * 64, "a" * 64) is True
