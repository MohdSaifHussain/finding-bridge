"""CLI wiring only (charter section 5.2). Every operation is a Workspace,
gate, or adapter call; refusals exit nonzero and print the reason code."""

import argparse
import json
import sys
from pathlib import Path

from finding_bridge import gate, pipeline
from finding_bridge.adapters import reading, writing
from finding_bridge.adapters.in_.garak import GarakAdapterError
from finding_bridge.adapters.in_.transcript import TranscriptAdapterError
from finding_bridge.adapters.out import flare_ai, markdown, sarif
from finding_bridge.core.dedup import DedupError
from finding_bridge.core.provenance import ProvenanceError
from finding_bridge.core.schema import SchemaValidationError
from finding_bridge.core.sealing import SealingError

DEFAULT_STORE = ".fb-store"
DEFAULT_KEY = Path.home() / ".finding-bridge" / "fb.key"


def _workspace(args) -> pipeline.Workspace:
    return pipeline.Workspace(Path(args.store), Path(args.key), Path.cwd())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="finding-bridge", description="finding-bridge")
    parser.add_argument("--store", default=DEFAULT_STORE, help="workspace directory")
    parser.add_argument("--key", default=str(DEFAULT_KEY), help="sealing key path (outside repo)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest-garak", help="ingest a garak hitlog JSONL")
    p.add_argument("hitlog")
    p = sub.add_parser(
        "ingest-transcript",
        help="ingest a manual attack transcript (file or '-' for stdin; "
        "10 MiB cap, a configurable cap is addable later)",
    )
    p.add_argument("source", help="transcript file path, or - for stdin")
    p.add_argument("--target-model", default=None)
    p.add_argument("--target-model-version", default=None)
    p.add_argument("--discovered-at", default=None, help="ISO 8601; omit if unknown, never guess")
    sub.add_parser("list", help="list candidate findings")
    p = sub.add_parser("confirm", help="confirm a candidate (human gate)")
    p.add_argument("finding_id")
    p = sub.add_parser("reject", help="reject a candidate")
    p.add_argument("finding_id")
    sub.add_parser("verify", help="verify the confirmed ledger chain + head")
    p = sub.add_parser("emit-markdown", help="emit confirmed findings as a packet")
    p.add_argument("out", nargs="?", help="output file (stdout if omitted)")
    p = sub.add_parser("emit-sarif", help="emit confirmed findings as SARIF 2.1.0")
    p.add_argument("out", help="output .sarif path")
    p.add_argument(
        "--artifact-name",
        default="findings.fb.jsonl",
        help="findings record file written beside the SARIF; SARIF locations point at its lines",
    )
    p = sub.add_parser(
        "emit-flare",
        help="emit confirmed findings as a PROVISIONAL FLARE-AI report set",
    )
    p.add_argument("out", help="output .json path (default name: findings.flare.json)")
    p = sub.add_parser("unseal", help="explicitly unseal one reference (logged)")
    p.add_argument("ref")
    p.add_argument("--explicit", action="store_true", help="required; unsealing is deliberate")

    args = parser.parse_args(argv)
    try:
        ws = _workspace(args)
        if args.command == "ingest-garak":
            print(json.dumps(ws.ingest_garak(Path(args.hitlog))))
        elif args.command == "ingest-transcript":
            text = reading.read_text_capped(args.source)
            metadata = {
                "target_model": args.target_model,
                "target_model_version": args.target_model_version,
                "discovered_at": args.discovered_at,
            }
            print(json.dumps(ws.ingest_transcript(text, metadata)))
        elif args.command == "list":
            for c in ws.list_candidates():
                dup = c["dedup"]["duplicate_of"]
                flag = f" duplicate-of {dup}" if dup else ""
                print(f"{c['id']}  {c['source_tool']}  {c['preview'] or 'no preview'}{flag}")
        elif args.command == "confirm":
            confirmed = ws.confirm(args.finding_id, gate.get_git_identity())
            print(f"confirmed {confirmed['id']} by {confirmed['provenance']['confirmed_by']}")
        elif args.command == "reject":
            rejected = ws.reject(args.finding_id)
            print(f"rejected {rejected['id']}")
        elif args.command == "verify":
            failures = ws.verify()
            if failures:
                for f in failures:
                    print(f"{f['reason_code']}: {f['detail']}", file=sys.stderr)
                return 1
            print("chain verifies clean")
        elif args.command == "emit-markdown":
            packet = markdown.render_packet(ws.confirmed_findings())
            if args.out:
                writing.write_text_output(Path(args.out), packet)
                print(f"wrote {args.out}")
            else:
                print(packet)
        elif args.command == "emit-sarif":
            findings = ws.confirmed_findings()
            log = sarif.render_sarif(findings, args.artifact_name)
            out_path = Path(args.out)
            artifact_path = out_path.parent / args.artifact_name
            writing.write_text_output(artifact_path, sarif.render_findings_artifact(findings))
            writing.write_text_output(
                out_path, json.dumps(log, indent=2, ensure_ascii=False) + "\n"
            )
            print(f"wrote {out_path} and {artifact_path}")
        elif args.command == "emit-flare":
            reports = flare_ai.render_reports(ws.confirmed_findings())
            writing.write_text_output(
                Path(args.out), json.dumps(reports, indent=2, ensure_ascii=False) + "\n"
            )
            print(f"wrote {args.out} (PROVISIONAL mapping; see the provisional block)")
        elif args.command == "unseal":
            print(ws.store.unseal(args.ref, gate.get_git_identity(), explicit=args.explicit))
    except (
        GarakAdapterError,
        TranscriptAdapterError,
        reading.InputError,
        writing.OutputError,
        DedupError,
        ProvenanceError,
        SchemaValidationError,
        SealingError,
        gate.GateError,
        pipeline.PipelineError,
        markdown.MarkdownAdapterError,
        sarif.SarifAdapterError,
        flare_ai.FlareAdapterError,
    ) as exc:
        print(f"{exc.reason_code}: {exc.detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
