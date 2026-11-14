# Pattern 4: Verification markers

**Problem.** A nightly job can fail quietly. Nobody reads its log, so a bad output sits there until someone uses it.

**Idea.** After every build, run an independent check. If it fails, write a small marker file (`VERIFY_FAILED.txt`) next to the output, listing what is wrong. If it passes, remove the marker. Anything else (a logon alert, a morning check, a dashboard, another job) only has to ask: *does a marker file exist?*

```
build -> independent check -> fail: write VERIFY_FAILED.txt (with reasons)
                           -> pass: delete VERIFY_FAILED.txt
alert / reviewer: any VERIFY_FAILED.txt anywhere?  -> investigate
```

## Rules
1. **Verify independently.** The check recomputes totals from the original inputs; it does not reuse the build code or trust its intermediate files.
2. **The marker explains itself.** List the specific mismatches, not just "failed".
3. **Fail loudly, clear quietly.** A pass removes the marker, so the presence of a marker always means "currently broken".
4. **Make the check cheap to find.** Alerts look for one file name under one root.
5. **Catch-up must respect markers.** A catch-up job should rebuild a unit whose marker exists, and leave verified units alone.
6. **Some checks are too big to automate.** Say so, and schedule them as a manual weekly or monthly review, not daily.

## Examples
- [verify_marker.py](../examples/markers/verify_marker.py): wraps any check command and writes or clears the marker.
- A complete worked example with real merge, dedupe and check scripts on synthetic data is in the companion repo `reconciliation-demo`.
