# Lessons (project-local; the ones ruled worth keeping)

Each entry names the incident that produced it. A lesson that recurs
without its check becoming a tool goes back to the director (skill rule
14).

1. **Read a traceback's PATH before reading its stack.** (STEP-03 stop
   one, S3-3: a `FileNotFoundError: 'S:\\'` looked like a product crash
   and was a broken test-harness chain - `$SM` unset after a failed `&&`
   link, MSYS mangling `/s` into drive `S:`. The product was never
   exercised.) Ruled a keeper by the director: it will recur.
2. **A stale observation reported as a prediction is neither.** (STEP-02
   close, D-040.2: "7 tests" was an observed count from before two
   configs existed.) Predictions say how they were obtained; observations
   say when.
3. **A sequencing temptation is a PROV entry, not a later confession.**
   (STEP-03, S3-1/D-043.) The register exists for the moment of
   temptation.
