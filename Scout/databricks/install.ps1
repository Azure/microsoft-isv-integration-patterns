[CmdletBinding()]
param(
    [string]$MarketplaceSource = "https://github.com/Azure/microsoft-isv-integration-patterns",
    [string]$ScoutHome = (Join-Path $HOME ".scout\copilot"),
    [string]$ScoutSkillsHome = (Join-Path $HOME ".scout\m-skills")
)

$ErrorActionPreference = "Stop"
$marketplaceName = "microsoft-isv-integration-patterns"
$pluginName = "databricks"
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

    $marketplaces = & $copilot plugin marketplace list 2>&1 | Out-String
    if ($marketplaces -match [regex]::Escape($marketplaceName)) {
        & $copilot plugin marketplace update $marketplaceName
    }
    else {
        & $copilot plugin marketplace add $MarketplaceSource
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to register or update the Scout plugin marketplace."
    }

    $plugins = & $copilot plugin list 2>&1 | Out-String
    if ($plugins -match [regex]::Escape($pluginName)) {
        & $copilot plugin update "$pluginName@$marketplaceName"
    }
    else {
        & $copilot plugin install "$pluginName@$marketplaceName"
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install or update $pluginName."
    }

    $pluginSkills = Join-Path $env:COPILOT_HOME "installed-plugins\$marketplaceName\$pluginName\skills"
    if (-not (Test-Path $pluginSkills)) {
        throw "Installed plugin skills were not found at $pluginSkills."
    }

    New-Item -ItemType Directory -Path $ScoutSkillsHome -Force | Out-Null
    $skillDirectories = Get-ChildItem $pluginSkills -Directory
    foreach ($skillDirectory in $skillDirectories) {
        $link = Join-Path $ScoutSkillsHome $skillDirectory.Name
        if (Test-Path $link) {
            $existing = Get-Item $link -Force
            if ($existing.LinkType -and $existing.Target -contains $skillDirectory.FullName) {
                continue
            }
            throw "Refusing to replace existing Scout skill: $link"
        }
        New-Item -ItemType Junction -Path $link -Target $skillDirectory.FullName | Out-Null
    }

    & $copilot plugin list
    Write-Host "Registered $($skillDirectories.Count) skills. Restart Microsoft Scout to refresh the Skills UI."
}
finally {
    $env:COPILOT_HOME = $previousHome
    $env:COPILOT_CACHE_HOME = $previousCacheHome
}