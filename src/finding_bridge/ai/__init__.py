"""Optional, caged AI (charter rule 2). Imported ONLY behind --ai.

Charter rule 2, restated because this package is the thing it governs:
AI may ONLY draft prose - severity rationale and taxonomy-mapping
SUGGESTIONS. It may never create, edit, score, hash, seal, or otherwise
alter a finding's evidence or provenance. Every field it touches is
labeled `suggested` and requires a human's acceptance at the gate before
it is part of a confirmed finding.

Three structural guarantees, not promises:

1. NOTHING in the deterministic pipeline imports this package. A test
   (tests/test_ai_caged.py) tracks module imports through a full pipeline
   run and fails if `finding_bridge.ai` appears. The zero-key suite is
   untouched by this package's existence.
2. The AI is handed the PREVIEW and METADATA of a finding, never its
   sealed content. Unsealed text reaches it only if the operator unsealed
   it first through the existing explicit, logged path and passed it in
   deliberately.
3. Failure NEVER blocks the deterministic pipeline. A missing key or an
   unreachable API produces a governed refusal (`ai-key-missing`,
   `ai-unavailable`) and the run continues exactly as it would with no
   --ai flag at all.

The anthropic SDK is an OPTIONAL dependency: this package installs and
the whole suite runs without it.
"""

from finding_bridge.ai.suggest import (
    REASON_AI_KEY_MISSING,
    REASON_AI_UNAVAILABLE,
    AiUnavailable,
    suggest_severity_rationale,
    suggest_taxonomy,
)

__all__ = [
    "REASON_AI_KEY_MISSING",
    "REASON_AI_UNAVAILABLE",
    "AiUnavailable",
    "suggest_severity_rationale",
    "suggest_taxonomy",
]
