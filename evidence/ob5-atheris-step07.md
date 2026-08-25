# OB-5: the coverage-guided run (STEP-07 P2, 2026-08-25)

Run: https://github.com/MohdSaifHussain/finding-bridge/actions/runs/32846272639
(fuzz.yml, workflow_dispatch, ubuntu-latest, Atheris 3.1.0 on Python
3.12, budget 30 minutes stated in the workflow and in the log). Harness:
tools/fuzz_atheris.py (first byte selects garak / transcript-text /
transcript-file; governed error classes are expected; anything else is a
crash artifact). Seeds: the synthetic fixtures only, no real data on the
runner.

libFuzzer's own final lines, from the uploaded run artifact:

```
#12	INITED cov: 170 ft: 285 corp: 7/4597b exec/s: 0 rss: 43Mb
stat::number_of_executed_units: 8101169
stat::average_exec_per_sec:     4498
stat::new_units_added:          3888
stat::slowest_unit_time_sec:    0
stat::peak_rss_mb:              59
atheris exit 0
crash artifacts: 0
```

8,101,169 executions at 4,498/s; coverage 216 edges, 1,067 features;
corpus grown from the seeds to 169 units; peak RSS 59 MB; zero crash
artifacts; exit 0.

What it does not prove: inputs outside the reached coverage; the harness
selects three entry points and caps inputs at 200,000 bytes (the 10 MiB
boundary is a separate check); one run, one Python. Together with the
structured pass (evidence/ob5-fuzz-step06.md: 11,063 inputs, eight
families, zero escapes) it is the evidence the D-082 narrowing asked for:
one coverage-guided run on the Linux runner, green, report read.

Disposition proposed to the director: OB-5 DISCHARGED on this evidence,
with the workflow kept for the audit cadence (re-run per phase close).
