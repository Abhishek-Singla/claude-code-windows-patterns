# Pattern 2: Temporary task for CLI logins

**Problem.** A command-line tool (a cloud CLI, for example) is signed in inside your own interactive Windows session. A process started by an automation tool or an agent runs in a different context and cannot see that login, so the same command fails with an authentication error even though it works in your terminal.

**Idea.** Register a one-shot scheduled task that runs *as you, in your interactive session*, point it at the command, wait for it, read its log, then unregister the task. The agent never handles your credentials; it only asks Windows to run a command in the session where the login already exists.

```
register task (current user, interactive)  ->  start  ->  poll until finished or timeout  ->  read log  ->  unregister (always)
```

## Rules
1. **Always unregister**, even on failure or timeout (`try/finally`). A leftover task is a standing way to run commands.
2. **Always set a timeout.** A task can sit in "Queued" if no interactive session is available. Stop waiting and report it instead of hanging.
3. **Log to a file** and print the tail, so the result is visible to the caller.
4. **Show the exact command before running it** and keep it to a single, reviewed command. Do not accept a command from untrusted text.
5. **Use it only when needed.** If the tool supports a service account or token you have already provisioned for automation, prefer that.
6. **Never pass secrets on the command line**; they end up in task definitions and logs.

## Alternative
If the task is a one-off, simply ask the person to run the command in their own terminal and paste the result. That is the safest option when the login is personal.

## Example
[run_in_user_session.ps1](../examples/temp-task/run_in_user_session.ps1)
