"""CLI wiring only (charter section 5.2). Every operation is a Workspace,
gate, or adapter call; refusals exit nonzero and print the reason code."""

import argparse
import json
import sys
from pathlib import Path

from finding_bridge import gate, pipeline
from finding_bridge.adapters.in_.garak import GarakAdapterError
from finding_bridge.adapters.out import markdown
from finding_bridge.core.dedup import DedupError
from finding_bridge.core.provenance import ProvenanceError
from finding_bridge.core.schema import SchemaValidationError
from finding_bridge.core.sealing import SealingError

DEFAULT_STORE = ".fb-store"
DEFAULT_KEY = Path.home() / ".finding-bridge" / "fb.key"


def _workspace(args) -> pipeline.Workspace:
    return pipeline.Workspace(Path(args.store), Path(args.key), Path.cwd())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fb", description="finding-bridge")
    parser.add_argument("--store", default=DEFAULT_STORE, help="workspace directory")
    parser.add_argument("--key", default=str(DEFAULT_KEY), help="sealing key path (outside repo)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest-garak", help="ingest a garak hitlog JSONL")
    p.add_argument("hitlog")
    sub.add_parser("list", help="list candidate findings")
    p = sub.add_parser("confirm", help="confirm a candidate (human gate)")
    p.add_argument("finding_id")
    p = sub.add_parser("reject", help="reject a candidate")
    p.add_argument("finding_id")
    sub.add_parser("verify", help="verify the confirmed ledger chain + head")
    p = sub.add_parser("emit-markdown", help="emit confirmed findings as a packet")
    p.add_argument("out", nargs="?", help="output file (stdout if omitted)")
    p = sub.add_parser("unseal", help="explicitly unseal one reference (logged)")
    p.add_argument("ref")
    p.add_argument("--explicit", action="store_true", help="required; unsealing is deliberate")

    args = parser.parse_args(argv)
    try:
        ws = _workspace(args)
        if args.command == "ingest-garak":
            print(json.dumps(ws.ingest_garak(Path(args.hitlog))))
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
                Path(args.out).write_text(packet, encoding="utf-8")
                print(f"wrote {args.out}")
            else:
                print(packet)
        elif args.command == "unseal":
            print(ws.store.unseal(args.ref, gate.get_git_identity(), explicit=args.explicit))
    except (
        GarakAdapterError,
        DedupError,
        ProvenanceError,
        SchemaValidationError,
        SealingError,
        gate.GateError,
        pipeline.PipelineError,
        markdown.MarkdownAdapterError,
    ) as exc:
        print(f"{exc.reason_code}: {exc.detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
