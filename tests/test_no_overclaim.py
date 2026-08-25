"""W1b: the never-overclaim check (D-042 as a test, skill rule 14).

User-facing docs may not claim features that do not ship. The banned
phrase list is recorded in DECISIONS D-046. Marketing drift fails here.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
USER_DOCS = [
    p
    for p in [
        REPO / "README.md",
        REPO / "docs" / "USAGE.md",
        REPO / "SOP.md",
        REPO / "docs" / "STANDARDS.md",
        REPO / "docs" / "showcase" / "README.md",
        REPO / "CHANGELOG.md",
        REPO / "SECURITY.md",
        *sorted(REPO.glob("examples/*/README.md")),
    ]
    if p.exists()
]
# D-073: the wording law governs every artifact the launch arc produces, so
# every user-facing document that exists is scanned; a doc that does not
# exist yet (CHANGELOG, SECURITY) joins the list the day it lands.

# D-073: a QUOTED standard may carry a banned phrase under three conditions,
# all three checked mechanically: (a) verbatim inside quotation marks;
# (b) attributed to its source by name within ATTRIBUTION_WINDOW chars before
# the opening quote; (c) immediately followed (within NARROWING_WINDOW chars
# after the closing quote) by our narrower claim. Bare unquoted use stays
# banned everywhere forever.
ATTRIBUTION = re.compile(r"\b(NIST|OWASP|MITRE|SAIF|Google|Guide|AI 600-1|RMF)\b")
NARROWING = re.compile(
    r"tamper[- ]evident|narrower|this tool's claim|our claim|not claimed|does not claim",
    re.IGNORECASE,
)
ATTRIBUTION_WINDOW = 400
NARROWING_WINDOW = 300


def quoted_and_narrowed(text: str, start: int, end: int) -> bool:
    """True when the match at [start, end) satisfies all three D-073 conditions."""
    open_q = text.rfind('"', 0, start)
    close_q = text.find('"', end)
    if open_q == -1 or close_q == -1:
        return False
    if text.count('"', open_q + 1, start) or text.count('"', end, close_q):
        return False  # a quote boundary lies between the match and the marks
    before = text[max(0, open_q - ATTRIBUTION_WINDOW) : open_q]
    after = text[close_q : close_q + NARROWING_WINDOW]
    return bool(ATTRIBUTION.search(before)) and bool(NARROWING.search(after))


# D-046 banned phrases. Each is a claim the tool does not ship. The
# pattern is case-insensitive. Where a doc must MENTION a banned idea to
# deny it, it must use the allowed wording in ALLOWED_CONTEXTS.
BANNED = {
    r"grey[- ]?scal(e|ed|ing) summary": "semantic summary is not shipped (D-042)",
    r"gray[- ]?scal(e|ed|ing) summary": "semantic summary is not shipped (D-042)",
    r"safe grey(ed)?[- ]?out summary": "the exact pitch phrase D-042 banned",
    r"summar(y|ises|izes) the (harmful )?content": "the preview does not summarize content",
    r"AI[- ]powered": "no AI runs in this pipeline",
    r"tamper[- ]proof": "the chain is tamper-EVIDENT, not tamper-proof",
    r"unbreakable|bulletproof|military[- ]grade": "unearned security claim",
    r"guarantees? (safety|security)": "no such guarantee is made",
    r"fully automat(ed|ic)": "the human gate is mandatory by design",
    r"no human (review|confirmation) (needed|required)": "the gate is mandatory",
    r"publish(es|ed)? to (PyPI|GitHub)": "no publishing exists",
    r"cross[- ]store (correlation|matching)": "ids are store-local (D-028)",
    r"detects? (all|every) ": "no completeness claim is made",
}


def doc_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flat(text: str) -> str:
    """Collapse whitespace. A required sentence must count as present even
    when the doc wraps it across lines; line wrapping is formatting, not
    meaning. (Found by this check failing on a wrapped sentence.)"""
    return re.sub(r"\s+", " ", text)


@pytest.mark.parametrize("doc", USER_DOCS, ids=lambda p: p.name)
def test_user_docs_contain_no_banned_claim(doc: Path):
    text = flat(doc_text(doc))
    hits = []
    for pattern, why in BANNED.items():
        for found in re.finditer(pattern, text, re.IGNORECASE):
            if quoted_and_narrowed(text, found.start(), found.end()):
                continue  # D-073 exemption, all three conditions held
            hits.append(f"{doc.name}: '{found.group(0)}' - {why}")
    assert not hits, "banned claims found in user docs:\n" + "\n".join(hits)


def test_check_detects_a_planted_overclaim(tmp_path: Path):
    """The check proves it can fail (skill rule 5). A planted overclaim in
    a doc-shaped file must be caught by the same patterns."""
    planted = tmp_path / "PLANTED.md"
    planted.write_text(
        "finding-bridge shows a safe greyed-out summary of the harmful "
        "content and is tamper-proof.",
        encoding="utf-8",
    )
    text = doc_text(planted)
    caught = [p for p in BANNED if re.search(p, text, re.IGNORECASE)]
    assert len(caught) >= 2, f"planted overclaims not caught: {caught}"


def test_required_statements_present():
    """The other direction: docs must STATE the things D-042 requires."""
    readme = flat(doc_text(USER_DOCS[0]))
    usage = flat(doc_text(USER_DOCS[1]))
    assert "safe metadata preview" in readme.lower(), "D-042's ruled wording must appear"
    for name, text in (("README", readme), ("USAGE", usage)):
        assert "do not defend against an attacker" in text, f"{name}: OB-4 bound must be stated"
    assert "no ai" in usage.lower(), "the no-AI guarantee must be stated"


# --- W1 defect (director's docs read): install commands must be REAL ---

INSTALL_MUST_NOT_APPEAR = [
    # pip cannot hash-check a source-directory install; this exact line was
    # in the README and FAILED when the director questioned it (D-048).
    r"pip install -e \. -c constraints\.txt",
]


@pytest.mark.parametrize("doc", USER_DOCS, ids=lambda p: p.name)
def test_docs_contain_no_known_broken_command(doc: Path):
    text = flat(doc_text(doc))
    for pattern in INSTALL_MUST_NOT_APPEAR:
        assert not re.search(pattern, text), f"{doc.name} shows a command known to fail: {pattern}"


def test_install_docs_explain_the_wheel_route():
    """Both INSTALL docs must tell the user why the verified route needs a
    wheel (README and USAGE; the D-073 widening scans the others for claims,
    not for install text)."""
    for doc in (REPO / "README.md", REPO / "docs" / "USAGE.md"):
        text = flat(doc_text(doc)).lower()
        assert "python -m build --wheel" in text, f"{doc.name}: wheel route missing"
        assert "hash-check" in text or "hash verification" in text, (
            f"{doc.name}: the reason for the wheel route must be stated"
        )


# --- D-073 controls: the exemption admits exactly the three-condition shape ---

QUOTE_OK = (
    'NIST AI 600-1 MS-2.8-003 says "provide a tamper-proof history of the content". '
    "This tool's claim is narrower: tamper-evident, bounded by OB-4."
)


def test_quoted_attributed_narrowed_phrase_is_exempt():
    m = re.search(r"tamper[- ]proof", QUOTE_OK)
    assert quoted_and_narrowed(QUOTE_OK, m.start(), m.end())


@pytest.mark.parametrize(
    "text",
    [
        "the chain gives a tamper-proof history",  # bare
        'someone said "a tamper-proof history" and we agree.',  # quoted only
        'NIST says "a tamper-proof history".',  # not narrowed
        "NIST says a tamper-proof history. Our claim is narrower.",  # not quoted
    ],
)
def test_exemption_refuses_every_shape_missing_a_condition(text):
    m = re.search(r"tamper[- ]proof", text)
    assert not quoted_and_narrowed(text, m.start(), m.end())
