# Pattern 1: Routine mirror

**Problem.** Scheduled routines (prompts, scripts, task definitions) live in scattered local folders. If the machine is wiped or a script is edited badly, there is no history and no backup.

**Idea.** A small config lists each routine and the files that define it. A scheduled job copies those files into a clone of a Git repo, scans them for secrets and local paths, and commits and pushes only if something changed.

```
routines.json  ->  copy sources into mirror/routines/<name>/  ->  secret scan  ->  commit + push (if changed)
```

## Rules that make it safe
1. **Skip a routine when a source is missing.** A moved folder must not wipe the mirrored copy. The script warns and leaves the last good copy in place.
2. **Scan before committing.** The scan blocks key shapes, e-mail addresses, absolute local paths, and file types that should never be public. If the scan fails, nothing is committed.
3. **Allow-list what is copied.** Each routine names the file patterns to include (`*.ps1`, `*.py`, `*.md`), so data files, logs and outputs never come along.
4. **Commit only on change.** No empty commits, so the history shows real edits.
5. **One repo, one folder per routine.** Easier to browse than many repos.
6. **Never push from a machine that blocks it silently.** Check the remote after pushing; a network proxy can reject the push without an error in your scheduler's history.

## Config shape
See [routines.example.json](../examples/routine-mirror/routines.example.json): each routine has a `name`, a `description`, `sources` (files or folders) and `include` patterns.

## Running it on a schedule
Register one scheduled task that runs the script every 10-15 minutes. Because the script only commits when files changed, a short interval is cheap.

## Things to watch
- Keep the mirror clone separate from your working folders.
- Decide up front which file types are banned from the repo (spreadsheets, PDFs, test specs) and enforce it in both `.gitignore` and the scan.
- When a routine is renamed or merged into another, update the config in the same change.
