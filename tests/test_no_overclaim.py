"""W1b: the never-overclaim check (D-042 as a test, skill rule 14).

User-facing docs may not claim features that do not ship. The banned
phrase list is recorded in DECISIONS D-046. Marketing drift fails here.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
USER_DOCS = [REPO / "README.md", REPO / "docs" / "USAGE.md"]

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
        found = re.search(pattern, text, re.IGNORECASE)
        if found:
            line = text[: found.start()].count("\n") + 1
            hits.append(f"{doc.name}:{line}: '{found.group(0)}' - {why}")
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
