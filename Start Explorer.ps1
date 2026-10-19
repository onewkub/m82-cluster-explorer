$ErrorActionPreference = 'Stop'
$explorerLauncher = Get-Command py -ErrorAction SilentlyContinue
$explorerArgs = @('-3', 'server.py')
if (-not $explorerLauncher) {
    $explorerLauncher = Get-Command python -ErrorAction SilentlyContinue
    $explorerArgs = @('server.py')
}
if (-not $explorerLauncher) {
    throw 'Install Python 3, then run python server.py from this folder.'
}
Start-Process -FilePath $explorerLauncher.Source -ArgumentList $explorerArgs -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
