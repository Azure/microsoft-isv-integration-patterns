[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("snowflake-cortex-code", "databricks")]
    [string]$PluginName,
    [string]$MarketplaceName = "microsoft-isv-integration-patterns",
    [string]$ScoutHome = (Join-Path $HOME ".scout\copilot"),
    [string]$ScoutSkillsHome = (Join-Path $HOME ".scout\m-skills")
)

$ErrorActionPreference = "Stop"
$copilot = Get-ChildItem `
    "C:\Program Files\Microsoft Scout\resources\app.asar.unpacked\node_modules\@github" `
    -Recurse -Filter copilot.exe -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $copilot) {
    throw "Microsoft Scout's bundled Copilot CLI was not found. Install or update Microsoft Scout first."
}

$previousHome = $env:COPILOT_HOME
$previousCacheHome = $env:COPILOT_CACHE_HOME

try {
    $env:COPILOT_HOME = $ScoutHome
    $env:COPILOT_CACHE_HOME = Join-Path $env:COPILOT_HOME "cache"
    $pluginSkills = Join-Path $env:COPILOT_HOME "installed-plugins\$MarketplaceName\$PluginName\skills"
    $ownedSkillLinks = @()

    if (Test-Path -LiteralPath $pluginSkills -PathType Container) {
        $pluginSkillsRoot = (Resolve-Path -LiteralPath $pluginSkills).Path.TrimEnd("\") + "\"
        $ownedSkillLinks = @(Get-ChildItem -LiteralPath $ScoutSkillsHome -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.LinkType } |
            Where-Object {
                $targets = @($_.Target)
                $targets | Where-Object {
                    $_ -and $_.StartsWith($pluginSkillsRoot, [StringComparison]::OrdinalIgnoreCase)
                }
            })
    }

    & $copilot plugin uninstall "$PluginName@$MarketplaceName"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to uninstall $PluginName."
    }
    foreach ($link in $ownedSkillLinks) {
        if (Test-Path -LiteralPath $link.FullName) {
            Remove-Item -LiteralPath $link.FullName -Force
        }
    }
    Write-Host "Removed $PluginName and its Scout skill junctions. Restart Microsoft Scout."
}
finally {
    $env:COPILOT_HOME = $previousHome
    $env:COPILOT_CACHE_HOME = $previousCacheHome
}
