[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("snowflake-cortex-code", "databricks")]
    [string]$PluginName,
    [string]$MarketplaceSource = "https://github.com/Azure/microsoft-isv-integration-patterns",
    [string]$ScoutHome = (Join-Path $HOME ".scout\copilot"),
    [string]$ScoutSkillsHome = (Join-Path $HOME ".scout\m-skills")
)

$ErrorActionPreference = "Stop"
$marketplaceName = "microsoft-isv-integration-patterns"
$copilot = Get-ChildItem `
    "C:\Program Files\Microsoft Scout\resources\app.asar.unpacked\node_modules\@github" `
    -Recurse -Filter copilot.exe -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $copilot) {
    throw "Microsoft Scout's bundled Copilot CLI was not found. Install or update Microsoft Scout first."
}

function Get-MarketplaceSourceDescriptor {
    param([string]$Source)

    if ($Source -match "^https://github\.com/(?<repo>[^/]+/[^/]+?)(?:\.git)?/?$") {
        return "GitHub: $($Matches.repo)"
    }
    if ($Source -match "^(?<repo>[^/\\]+/[^/\\]+)$") {
        return "GitHub: $($Matches.repo)"
    }
    if (Test-Path -LiteralPath $Source -PathType Container) {
        return "Local: $((Resolve-Path -LiteralPath $Source).Path)"
    }
    throw "MarketplaceSource must be an owner/repository GitHub source, a GitHub repository URL, or an existing local directory."
}

$previousHome = $env:COPILOT_HOME
$previousCacheHome = $env:COPILOT_CACHE_HOME
$gitConfigIndex = if ($env:GIT_CONFIG_COUNT -match "^\d+$") { [int]$env:GIT_CONFIG_COUNT } else { 0 }
$gitConfigKeyName = "GIT_CONFIG_KEY_$gitConfigIndex"
$gitConfigValueName = "GIT_CONFIG_VALUE_$gitConfigIndex"
$previousGitConfigCount = $env:GIT_CONFIG_COUNT
$previousGitConfigKey = [Environment]::GetEnvironmentVariable($gitConfigKeyName, "Process")
$previousGitConfigValue = [Environment]::GetEnvironmentVariable($gitConfigValueName, "Process")

try {
    $env:COPILOT_HOME = $ScoutHome
    $env:COPILOT_CACHE_HOME = Join-Path $env:COPILOT_HOME "cache"
    if ($env:OS -eq "Windows_NT") {
        $env:GIT_CONFIG_COUNT = $gitConfigIndex + 1
        [Environment]::SetEnvironmentVariable($gitConfigKeyName, "core.longpaths", "Process")
        [Environment]::SetEnvironmentVariable($gitConfigValueName, "true", "Process")
    }
    $expectedSource = Get-MarketplaceSourceDescriptor $MarketplaceSource

    $marketplaces = & $copilot plugin marketplace list 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to list Scout plugin marketplaces."
    }
    $marketplaceLine = $marketplaces -split "\r?\n" |
        Where-Object { $_ -match "\b$([regex]::Escape($marketplaceName))\b.*\((?<source>[^)]+)\)\s*$" } |
        Select-Object -First 1

    if ($marketplaceLine) {
        [void]($marketplaceLine -match "\((?<source>[^)]+)\)\s*$")
        $registeredSource = $Matches.source
        if (-not [string]::Equals($registeredSource, $expectedSource, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Marketplace '$marketplaceName' is registered from '$registeredSource', not '$expectedSource'. Remove or explicitly migrate the existing marketplace before installing."
        }
        & $copilot plugin marketplace update $marketplaceName
    }
    else {
        & $copilot plugin marketplace add $MarketplaceSource
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to register or update the Scout plugin marketplace."
    }

    $plugins = & $copilot plugin list 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to list installed Scout plugins."
    }
    $qualifiedPluginName = "$PluginName@$marketplaceName"
    if ($plugins -match "(?m)^\s*[^A-Za-z0-9]*$([regex]::Escape($qualifiedPluginName))(?:\s|\(|$)") {
        & $copilot plugin update "$PluginName@$marketplaceName"
    }
    else {
        & $copilot plugin install "$PluginName@$marketplaceName"
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install or update $PluginName."
    }

    $pluginSkills = Join-Path $env:COPILOT_HOME "installed-plugins\$marketplaceName\$PluginName\skills"
    if (-not (Test-Path -LiteralPath $pluginSkills -PathType Container)) {
        throw "Installed plugin skills were not found at $pluginSkills."
    }

    New-Item -ItemType Directory -Path $ScoutSkillsHome -Force | Out-Null
    $pluginSkillsRoot = (Resolve-Path -LiteralPath $pluginSkills).Path.TrimEnd("\") + "\"
    $skillDirectories = @(Get-ChildItem -LiteralPath $pluginSkills -Directory)
    $currentTargets = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($skillDirectory in $skillDirectories) {
        [void]$currentTargets.Add($skillDirectory.FullName)
    }

    Get-ChildItem -LiteralPath $ScoutSkillsHome -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.LinkType } |
        ForEach-Object {
            $pluginOwnedTargets = @($_.Target) |
                Where-Object { $_ -and $_.StartsWith($pluginSkillsRoot, [StringComparison]::OrdinalIgnoreCase) }
            if ($pluginOwnedTargets -and -not ($pluginOwnedTargets | Where-Object { $currentTargets.Contains($_) })) {
                Remove-Item -LiteralPath $_.FullName -Force
            }
        }

    foreach ($skillDirectory in $skillDirectories) {
        $link = Join-Path $ScoutSkillsHome $skillDirectory.Name
        if (Test-Path -LiteralPath $link) {
            $existing = Get-Item -LiteralPath $link -Force
            if ($existing.LinkType -and @($existing.Target) -contains $skillDirectory.FullName) {
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
    $env:GIT_CONFIG_COUNT = $previousGitConfigCount
    [Environment]::SetEnvironmentVariable($gitConfigKeyName, $previousGitConfigKey, "Process")
    [Environment]::SetEnvironmentVariable($gitConfigValueName, $previousGitConfigValue, "Process")
}
