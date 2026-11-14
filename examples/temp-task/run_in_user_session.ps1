<#
.SYNOPSIS
  Run ONE command in the current user's interactive session via a temporary scheduled task.
.EXAMPLE
  .\run_in_user_session.ps1 -Command "gcloud storage ls gs://example-bucket/" -TimeoutSeconds 120
#>
param(
    [Parameter(Mandatory = $true)][string]$Command,
    [int]$TimeoutSeconds = 120
)
$ErrorActionPreference = "Stop"
$name = "TempUserSessionTask-" + [guid]::NewGuid().ToString("N").Substring(0, 8)
$log = Join-Path $env:TEMP "$name.log"
$me = "$env:USERDOMAIN\$env:USERNAME"

Write-Host "Command to run as ${me}: $Command"
try {
    $inner = "& { $Command } *> '$log'"
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"$inner`""
    $principal = New-ScheduledTaskPrincipal -UserId $me -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $name -Action $action -Principal $principal | Out-Null
    Start-ScheduledTask -TaskName $name

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        Start-Sleep -Seconds 2
        $state = (Get-ScheduledTask -TaskName $name).State
    } while ($state -ne "Ready" -and (Get-Date) -lt $deadline)

    if ($state -ne "Ready") {
        Write-Warning "Timed out after $TimeoutSeconds s (task state: $state). It may be queued because no interactive session is available."
        Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    }
    $info = Get-ScheduledTaskInfo -TaskName $name
    "Last task result: $($info.LastTaskResult)"
    if (Test-Path $log) { "--- output (tail) ---"; Get-Content $log -Tail 40 }
}
finally {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
    Remove-Item $log -ErrorAction SilentlyContinue
}
