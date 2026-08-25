# Fixture shape currency (D-079 b)

The synthetic garak fixture certified the wrong object for two phases: a
Message shape the real tool no longer writes (finding F-12, the
wrong-object measurement class at the fixture layer). fixture_scan.py
checks harm conformance; nothing checked SHAPE currency against the live
tool. This table (kept in docs/, because fixture_scan rightly refuses prose in the fixtures folder) is that check's first half: every garak fixture names
the tool version whose output it mimics and the source it was verified
against. The second half is the real-data drill (examples/04-real-data),
whose re-run refreshes this table. tests/test_real_shapes.py fails if a
garak fixture is missing from it.

| Fixture | Mimics | Verified against | Date |
|---|---|---|---|
| garak.synthetic.hitlog.jsonl | garak pre-0.16 flat Message shape (`prompt`/`output` carry `text` at the top level) | `garak/evaluators/base.py` on `main`, 2026-08-24; real 0.16.0 output no longer has this shape | 2026-08-24 |
| garak.hostile.hitlog.jsonl | same flat shape, hostile numbers (S2-1) | as above | 2026-08-24 |
| garak.v0_16_0.synthetic.hitlog.jsonl | garak 0.16.0 Conversation shape (`prompt.turns[].content` is a Message with text, lang, data_path, data_type, data_checksum, notes; `output` a Message) | the real hitlog of the 2026-08-25 run (699 records, all this shape) and `garak/evaluators/base.py` at tag v0.16.0 | 2026-08-25 |
