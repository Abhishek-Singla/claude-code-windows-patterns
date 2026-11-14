# Claude Code automation patterns on Windows

Four small, reusable patterns from running recurring, Claude-assisted work on a Windows machine with Task Scheduler. Each pattern has a short write-up and a generic example you can run. All paths, names and values here are placeholders.

| Pattern | Problem it solves | Example |
|---|---|---|
| [1. Routine mirror](patterns/01-routine-mirror.md) | Keep prompts and scripts of scheduled routines versioned in Git, safely | [sync_routines.ps1](examples/routine-mirror/sync_routines.ps1), [secret_scan.py](examples/routine-mirror/secret_scan.py) |
| [2. Temporary task for CLI logins](patterns/02-temp-task-for-cli-login.md) | A command needs a login that exists only in your interactive session | [run_in_user_session.ps1](examples/temp-task/run_in_user_session.ps1) |
| [3. Rebuild only when inputs change](patterns/03-rebuild-only-on-input-change.md) | Heavy daily jobs redo work that nothing has changed | [fingerprint.py](examples/fingerprint/fingerprint.py) |
| [4. Verification markers](patterns/04-verification-markers.md) | A failed check must be visible without anyone reading logs | [verify_marker.py](examples/markers/verify_marker.py) |

Run the tests with `python -m unittest discover tests` (Python 3.10+, standard library only). The PowerShell examples need Windows PowerShell 5.1 or later.

## Principles behind all four
- **Skip, don't destroy.** If an input is missing, skip that step and say so; never delete the last good output.
- **Scan before you publish.** Anything copied to a public place passes an automated secret and path check first.
- **Leave evidence.** Every automated step leaves a small file or log line that a person or another job can check.
- **Idempotent.** Running twice gives the same result as running once.

By [Abhishek Singla](https://www.linkedin.com/in/abhishek-singla-pm)
