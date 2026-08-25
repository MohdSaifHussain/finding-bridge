"""The two caged capabilities: severity rationale, taxonomy mapping.

Both return SUGGESTIONS. Neither writes anything into a finding; the
caller (the human gate) presents them and a person accepts or rejects.

Source, fetched 2026-08-25:
https://platform.claude.com/docs/en/api/messages - the Messages API takes
model, max_tokens and messages; the python SDK reads ANTHROPIC_API_KEY
from the environment; failures raise APIConnectionError, RateLimitError,
APIStatusError, all under APIError.

Model pinning (contract W2d): the model id lives in config, never in
code. There is no default model literal here to drift.
"""

import hashlib
import json
import os

from finding_bridge.core.provenance import canonical_dumps, utc_now_iso

REASON_AI_KEY_MISSING = "ai-key-missing"
REASON_AI_UNAVAILABLE = "ai-unavailable"

MAX_TOKENS = 1024

RATIONALE_SYSTEM = (
    "You are helping an AI red-team analyst draft a SEVERITY RATIONALE for "
    "a finding. You are shown only metadata and a safe preview; the actual "
    "harmful content is sealed and you will not see it. Write two or three "
    "sentences of plain prose explaining what would drive severity up or "
    "down under an LLM-adapted rubric (exploitability, impact scope, data "
    "sensitivity, effort). Do not assign a score. Do not invent details "
    "that are not in the metadata you were given."
)

TAXONOMY_SYSTEM = (
    "You are suggesting taxonomy mappings for an AI red-team finding, from "
    "metadata and a safe preview only; the harmful content is sealed. "
    'Reply with a JSON object: {"owasp_llm": [...], "saif": [...]}, '
    "each a list of identifier strings you believe apply, possibly empty. "
    "Suggest nothing you cannot justify from the metadata shown."
)


class AiUnavailable(Exception):
    """The AI path could not run. NEVER fatal to the pipeline: callers
    degrade to the no-ai behaviour. Location-not-value per D-036."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _client(model: str):
    """Build a client, refusing governed when the key or SDK is absent."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise AiUnavailable(
            REASON_AI_KEY_MISSING,
            "ANTHROPIC_API_KEY is not set; --ai suggestions are unavailable "
            "and the deterministic pipeline is unaffected",
        )
    if not model:
        raise AiUnavailable(
            REASON_AI_UNAVAILABLE,
            "no model id configured; the model is pinned in config, never in code",
        )
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise AiUnavailable(
            REASON_AI_UNAVAILABLE,
            "the optional 'anthropic' package is not installed; install the "
            "'ai' extra to enable suggestions",
        ) from exc
    return Anthropic()


def safe_context(finding: dict) -> dict:
    """EXACTLY what the AI is allowed to see (contract W2c).

    Preview and metadata. No sealed content, no sealed references (a ref
    is a keyed digest and useless to a model, but sending one would still
    widen the surface for no benefit), no provenance identities.

    reproduction.steps is DELIBERATELY EXCLUDED, found by the sentinel
    control while this was written: steps are adapter-authored prose, and
    an adapter is free to put probe text in them. Today's two adapters do
    not, but "today's adapters do not" is not a guarantee, and the signal
    the AI would gain is already carried by harm_flags (which name the
    detector) and source_tool. Charter: prefer less exposure.
    """
    return {
        "source_tool": finding.get("source_tool"),
        "target_model": finding.get("target_model"),
        "harm_flags": finding.get("harm_flags"),
        "preview": finding.get("preview"),
    }


def _ai_provenance(system: str, payload: dict, response_text: str, model: str) -> dict:
    """Hash the prompt and the response into an auditable note (W2d).

    The suggestion carries the hashes, not the texts: a later reader can
    prove which prompt produced which suggestion, without the record
    growing a copy of everything the model was told.
    """
    prompt_bytes = canonical_dumps([system, payload])
    return {
        "model": model,
        "at": utc_now_iso(),
        "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
    }


def _ask(system: str, payload: dict, model: str) -> tuple[str, dict]:
    client = _client(model)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": json.dumps(payload, sort_keys=True)}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
    except AiUnavailable:
        raise
    except Exception as exc:  # SDK errors and anything else the call raises
        raise AiUnavailable(
            REASON_AI_UNAVAILABLE,
            f"the suggestion call did not complete ({type(exc).__name__}); "
            "the deterministic pipeline is unaffected",
        ) from exc
    return text, _ai_provenance(system, payload, text, model)


def suggest_severity_rationale(finding: dict, model: str) -> dict:
    """A prose severity rationale, labeled suggested. Writes nothing."""
    payload = safe_context(finding)
    text, provenance = _ask(RATIONALE_SYSTEM, payload, model)
    return {
        "kind": "severity_rationale",
        "status": "suggested",
        "value": text.strip(),
        "ai_provenance": provenance,
    }


def suggest_taxonomy(finding: dict, model: str) -> dict:
    """Taxonomy mappings, labeled suggested. Writes nothing.

    A reply that is not the requested JSON shape yields an EMPTY
    suggestion rather than a guess: the charter forbids inventing taxonomy
    tags, and that applies to salvaging a malformed model reply too.
    """
    payload = safe_context(finding)
    text, provenance = _ask(TAXONOMY_SYSTEM, payload, model)
    owasp: list[str] = []
    saif: list[str] = []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            owasp = [str(x) for x in parsed.get("owasp_llm", []) if isinstance(x, str)]
            saif = [str(x) for x in parsed.get("saif", []) if isinstance(x, str)]
    except json.JSONDecodeError:
        pass
    return {
        "kind": "taxonomy",
        "status": "suggested",
        "value": {"owasp_llm": owasp, "saif": saif},
        "ai_provenance": provenance,
    }
