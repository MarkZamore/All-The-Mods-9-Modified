$ErrorActionPreference = 'Stop'
try {
    $diagnosticRoot = Get-Item -LiteralPath $PSScriptRoot
    $minecraftRoot = $null
    while ($null -ne $diagnosticRoot) {
        if (($diagnosticRoot.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'Aliased or reparse paths are not supported.'
        }
        if ((Test-Path -LiteralPath (Join-Path $diagnosticRoot.FullName 'Launcher/JavaRuntimes') -PathType Container) -and
            (Test-Path -LiteralPath (Join-Path $diagnosticRoot.FullName 'Personal/Instances') -PathType Container)) {
            $minecraftRoot = $diagnosticRoot.FullName
            break
        }
        $diagnosticRoot = $diagnosticRoot.Parent
    }
    if ($null -eq $minecraftRoot) { throw 'Place this helper inside the portable Minecraft folder, then run it again.' }
    $diagnosticJava = Join-Path $minecraftRoot 'Launcher/JavaRuntimes/runtime/windows-x64/java-17/bin/java.exe'
    $diagnosticJar = Join-Path $PSScriptRoot 'recipe-exception-observer.jar'
    if (!(Test-Path -LiteralPath $diagnosticJava -PathType Leaf)) { throw 'The portable full Java 17 runtime is not installed yet. Start the game through the launcher first.' }
    if (!(Test-Path -LiteralPath $diagnosticJar -PathType Leaf)) { throw 'The diagnostic observer JAR is missing beside this helper.' }
    $diagnosticModules = & $diagnosticJava --list-modules
    if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the portable Java runtime.' }
    foreach ($diagnosticModule in @('jdk.jdi', 'jdk.attach', 'jdk.jdwp.agent')) {
        if (!($diagnosticModules -match ('^' + [regex]::Escape($diagnosticModule) + '@'))) { throw ('Portable Java is missing module ' + $diagnosticModule) }
    }
    Write-Host 'Finding the updated game. Wait for OBSERVER_READY before repeating the connection.'
    & $diagnosticJava --add-modules jdk.jdi,jdk.attach -jar $diagnosticJar --discover --minecraft-root $minecraftRoot
    if ($LASTEXITCODE -ne 0) { throw ('Diagnostic helper stopped with code ' + $LASTEXITCODE + '. Start the updated game first; keep only one matching game open.') }
    Write-Host 'Diagnostics finished. Send the normal game report through the launcher.'
} catch {
    Write-Host ('Diagnostics were not started: ' + $_.Exception.Message) -ForegroundColor Red
}
Read-Host 'Press Enter to close'
