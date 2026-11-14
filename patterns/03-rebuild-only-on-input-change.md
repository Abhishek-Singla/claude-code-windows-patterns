# Pattern 3: Rebuild only when inputs change

**Problem.** A daily job merges, verifies and rebuilds reports for many months of data. Most months never change, yet every run reprocesses them. That wastes time, risks timeouts, and rewrites outputs that people may have open.

**Idea.** Fingerprint the *input* files of each unit of work (for example, each month). Store the fingerprint after a successful build. On the next run, rebuild a unit only if its fingerprint differs.

```
inputs -> fingerprint -> same as stored? -> yes: skip (and say so)
                                         -> no : rebuild, verify, then store the new fingerprint
```

## Rules
1. **Fingerprint inputs, not outputs.** Names plus sizes plus modification times are cheap and usually enough; add content hashes (`--hash`) when files can change without changing size or time.
2. **Store the fingerprint only after the rebuild and its verification succeed.** Otherwise a failed run would be skipped forever.
3. **A new, missing or removed input counts as a change.**
4. **Say what was skipped.** Log "unchanged, skipped" per unit so a quiet run is distinguishable from a broken one.
5. **Provide a force flag** for the cases where you do want a rebuild.
6. **Late files must be seen.** If sources can arrive days late, keep the lookback window long enough that a late file changes the fingerprint of the month it belongs to.
7. **Do not rewrite derived reports on a skipped unit**, so files someone has open or edited by hand are not overwritten.

## Example
[fingerprint.py](../examples/fingerprint/fingerprint.py)

```bash
python fingerprint.py check  --state state/2026-01.json --files "inputs/2026-01/*.csv" || rebuild_month_2026_01
python fingerprint.py update --state state/2026-01.json --files "inputs/2026-01/*.csv"   # after the rebuild passes
```
`check` exits 0 when nothing changed (skip) and 1 when a rebuild is needed.
