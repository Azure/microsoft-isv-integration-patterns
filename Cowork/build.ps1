[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "plugin.config.json"),
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "dist"),
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"
$templatePath = Join-Path $PSScriptRoot "manifest.template.json"
$configTemplatePath = Join-Path $PSScriptRoot "plugin.config.template.json"
$runtimeSkillPath = Join-Path $PSScriptRoot "skills\data-platform-analytics"

function Read-RequiredValue {
    param([string]$Prompt, [string]$DefaultValue)

    $displayPrompt = if ($DefaultValue) { "$Prompt [$DefaultValue]" } else { $Prompt }
    $value = Read-Host $displayPrompt
    if ([string]::IsNullOrWhiteSpace($value)) {
        $value = $DefaultValue
    }
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "$Prompt is required."
    }
    return $value
}

function Read-ConnectorConfig {
    param([string]$Provider, [object]$Defaults)

    $enabledInput = Read-RequiredValue "$Provider connector enabled (yes/no)" $(if ($Defaults.enabled) { "yes" } else { "no" })
    $enabled = $enabledInput -match "^(?i:y|yes)$"
    $connector = [ordered]@{
        enabled = $enabled
        id = $Defaults.id
        displayName = $Defaults.displayName
        description = $Defaults.description
        mcpServerUrl = $Defaults.mcpServerUrl
    }
    if (-not $enabled) {
        return $connector
    }

    $connector.mcpServerUrl = Read-RequiredValue "$Provider remote MCP HTTPS URL" $Defaults.mcpServerUrl
    $useOAuth = Read-RequiredValue "$Provider uses an OAuth Plugin Vault reference (yes/no)" "yes"
    if ($useOAuth -match "^(?i:y|yes)$") {
        $connector.authorization = [ordered]@{
            type = "OAuthPluginVault"
            referenceId = Read-RequiredValue "$Provider OAuth Plugin Vault reference ID" $Defaults.authorization.referenceId
        }
    }
    return $connector
}

function New-InteractiveConfig {
    $defaults = Get-Content -Raw $configTemplatePath | ConvertFrom-Json
    $appId = Read-RequiredValue "Microsoft 365 app ID (GUID)" ([guid]::NewGuid().ToString())
    $config = [ordered]@{
        '$schema' = "./plugin.config.schema.json"
        app = [ordered]@{
            id = $appId
            version = Read-RequiredValue "App version" $defaults.app.version
            developerName = Read-RequiredValue "Developer or organization name" $defaults.app.developerName
            websiteUrl = Read-RequiredValue "Developer website HTTPS URL" $defaults.app.websiteUrl
            privacyUrl = Read-RequiredValue "Privacy policy HTTPS URL" $defaults.app.privacyUrl
            termsOfUseUrl = Read-RequiredValue "Terms of use HTTPS URL" $defaults.app.termsOfUseUrl
            shortName = Read-RequiredValue "Short app name (30 characters maximum)" $defaults.app.shortName
            fullName = Read-RequiredValue "Full app name" $defaults.app.fullName
            shortDescription = Read-RequiredValue "Short description (80 characters maximum)" $defaults.app.shortDescription
            fullDescription = Read-RequiredValue "Full description" $defaults.app.fullDescription
            accentColor = Read-RequiredValue "Accent color (#RRGGBB)" $defaults.app.accentColor
            colorIconPath = Read-RequiredValue "Path to 192x192 color PNG" $defaults.app.colorIconPath
            outlineIconPath = Read-RequiredValue "Path to 32x32 outline PNG" $defaults.app.outlineIconPath
        }
        connectors = [ordered]@{
            snowflake = Read-ConnectorConfig "Snowflake" $defaults.connectors.snowflake
            databricks = Read-ConnectorConfig "Databricks" $defaults.connectors.databricks
        }
    }
    $config | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 $ConfigPath
    Write-Host "Saved non-secret configuration to $ConfigPath."
}

function Assert-HttpsUrl {
    param([string]$Name, [string]$Value)

    $uri = $null
    if (-not [uri]::TryCreate($Value, [UriKind]::Absolute, [ref]$uri) -or $uri.Scheme -ne "https") {
        throw "$Name must be an absolute HTTPS URL."
    }
    if (-not [string]::IsNullOrEmpty($uri.UserInfo)) {
        throw "$Name must not contain user information or credentials."
    }
    return $uri
}

function Assert-AllowedProperties {
    param([string]$Name, [object]$Value, [string[]]$AllowedProperties)

    if ($null -eq $Value) {
        throw "$Name must be a JSON object."
    }
    foreach ($property in $Value.PSObject.Properties.Name) {
        if ($property -notin $AllowedProperties) {
            throw "$Name contains unsupported property '$property'."
        }
    }
}

function Assert-String {
    param([string]$Name, [object]$Value)

    if ($Value -isnot [string] -or [string]::IsNullOrWhiteSpace($Value)) {
        throw "$Name must be a non-empty string."
    }
}

function Assert-Length {
    param([string]$Name, [string]$Value, [int]$Maximum)

    if ([string]::IsNullOrWhiteSpace($Value) -or $Value.Length -gt $Maximum) {
        throw "$Name must contain between 1 and $Maximum characters."
    }
}

if ($Interactive) {
    New-InteractiveConfig
}
elseif (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
    throw "Configuration not found at $ConfigPath. Copy plugin.config.template.json or rerun with -Interactive."
}

$resolvedConfigPath = (Resolve-Path -LiteralPath $ConfigPath).Path
$configDirectory = Split-Path -Parent $resolvedConfigPath
$config = Get-Content -Raw $resolvedConfigPath | ConvertFrom-Json

$appProperties = @(
    "id",
    "version",
    "developerName",
    "websiteUrl",
    "privacyUrl",
    "termsOfUseUrl",
    "shortName",
    "fullName",
    "shortDescription",
    "fullDescription",
    "accentColor",
    "colorIconPath",
    "outlineIconPath"
)
Assert-AllowedProperties "configuration" $config @('$schema', 'app', 'connectors')
Assert-AllowedProperties "app" $config.app $appProperties
Assert-AllowedProperties "connectors" $config.connectors @('snowflake', 'databricks')

foreach ($property in $appProperties) {
    Assert-String "app.$property" $config.app.$property
}

$appGuid = [guid]::Empty
if (-not [guid]::TryParse($config.app.id, [ref]$appGuid) -or $appGuid -eq [guid]::Empty) {
    throw "app.id must be a non-empty GUID."
}
if ($config.app.version -notmatch "^\d+\.\d+\.\d+$") {
    throw "app.version must use major.minor.patch numeric format."
}
Assert-Length "app.shortName" $config.app.shortName 30
Assert-Length "app.fullName" $config.app.fullName 100
Assert-Length "app.shortDescription" $config.app.shortDescription 80
Assert-Length "app.fullDescription" $config.app.fullDescription 4000
if ($config.app.accentColor -notmatch "^#[0-9A-Fa-f]{6}$") {
    throw "app.accentColor must use #RRGGBB format."
}

$domains = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($urlProperty in @("websiteUrl", "privacyUrl", "termsOfUseUrl")) {
    $uri = Assert-HttpsUrl "app.$urlProperty" $config.app.$urlProperty
    [void]$domains.Add($uri.Host)
}

$agentConnectors = @()
foreach ($provider in @("snowflake", "databricks")) {
    $connector = $config.connectors.$provider
    Assert-AllowedProperties "connectors.$provider" $connector @(
        'enabled',
        'id',
        'displayName',
        'description',
        'mcpServerUrl',
        'authorization'
    )
    if ($connector.enabled -isnot [bool]) {
        throw "connectors.$provider.enabled must be a JSON boolean."
    }
    if (-not $connector.enabled) {
        continue
    }
    foreach ($property in @("id", "displayName", "description", "mcpServerUrl")) {
        Assert-String "connectors.$provider.$property" $connector.$property
    }
    if ($connector.id -notmatch "^[a-z][a-z0-9-]{0,63}$") {
        throw "connectors.$provider.id must start with a lowercase letter and contain only lowercase letters, digits, or hyphens."
    }
    Assert-Length "connectors.$provider.displayName" $connector.displayName 64
    Assert-Length "connectors.$provider.description" $connector.description 200
    $mcpUri = Assert-HttpsUrl "connectors.$provider.mcpServerUrl" $connector.mcpServerUrl
    [void]$domains.Add($mcpUri.Host)

    $remoteMcpServer = [ordered]@{
        mcpServerUrl = $connector.mcpServerUrl
    }
    if ($null -ne $connector.authorization) {
        Assert-AllowedProperties "connectors.$provider.authorization" $connector.authorization @('type', 'referenceId')
        Assert-String "connectors.$provider.authorization.type" $connector.authorization.type
        Assert-String "connectors.$provider.authorization.referenceId" $connector.authorization.referenceId
        if ($connector.authorization.type -ne "OAuthPluginVault" -or
            [string]::IsNullOrWhiteSpace($connector.authorization.referenceId)) {
            throw "connectors.$provider.authorization requires type OAuthPluginVault and a referenceId."
        }
        $remoteMcpServer.authorization = [ordered]@{
            type = "OAuthPluginVault"
            referenceId = $connector.authorization.referenceId
        }
    }
    $agentConnectors += [ordered]@{
        id = $connector.id
        displayName = $connector.displayName
        description = $connector.description
        toolSource = [ordered]@{
            remoteMcpServer = $remoteMcpServer
        }
    }
}
if ($agentConnectors.Count -eq 0) {
    throw "Enable at least one Snowflake or Databricks connector."
}

$colorIconPath = Join-Path $configDirectory $config.app.colorIconPath
$outlineIconPath = Join-Path $configDirectory $config.app.outlineIconPath
foreach ($icon in @($colorIconPath, $outlineIconPath)) {
    if (-not (Test-Path -LiteralPath $icon -PathType Leaf) -or [IO.Path]::GetExtension($icon) -ne ".png") {
        throw "Icon not found or not a PNG file: $icon"
    }
}
if (-not (Test-Path -LiteralPath $runtimeSkillPath -PathType Container)) {
    throw "Runtime skill not found at $runtimeSkillPath."
}

$manifest = Get-Content -Raw $templatePath | ConvertFrom-Json
$manifest.version = $config.app.version
$manifest.id = $config.app.id
$manifest.developer.name = $config.app.developerName
$manifest.developer.websiteUrl = $config.app.websiteUrl
$manifest.developer.privacyUrl = $config.app.privacyUrl
$manifest.developer.termsOfUseUrl = $config.app.termsOfUseUrl
$manifest.name.short = $config.app.shortName
$manifest.name.full = $config.app.fullName
$manifest.description.short = $config.app.shortDescription
$manifest.description.full = $config.app.fullDescription
$manifest.accentColor = $config.app.accentColor
$manifest.agentConnectors = $agentConnectors
$manifest.validDomains = @($domains | Sort-Object)

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$stagingDirectory = Join-Path $OutputDirectory ".cowork-package-staging"
if (Test-Path -LiteralPath $stagingDirectory) {
    Remove-Item -LiteralPath $stagingDirectory -Recurse -Force
}
New-Item -ItemType Directory -Path $stagingDirectory | Out-Null

try {
    $manifest | ConvertTo-Json -Depth 20 | Set-Content -Encoding utf8 (Join-Path $stagingDirectory "manifest.json")
    Copy-Item -LiteralPath $colorIconPath -Destination (Join-Path $stagingDirectory "color.png")
    Copy-Item -LiteralPath $outlineIconPath -Destination (Join-Path $stagingDirectory "outline.png")
    $packageSkillPath = Join-Path $stagingDirectory "skills\data-platform-analytics"
    New-Item -ItemType Directory -Path $packageSkillPath -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $runtimeSkillPath "SKILL.md") -Destination $packageSkillPath

    $safeName = $config.app.shortName -replace "[^A-Za-z0-9.-]", "-"
    $packagePath = Join-Path $OutputDirectory "$safeName-$($config.app.version).zip"
    if (Test-Path -LiteralPath $packagePath) {
        Remove-Item -LiteralPath $packagePath -Force
    }
    Compress-Archive -Path (Join-Path $stagingDirectory "*") -DestinationPath $packagePath
    Write-Host "Created Cowork app package: $packagePath"
}
finally {
    if (Test-Path -LiteralPath $stagingDirectory) {
        Remove-Item -LiteralPath $stagingDirectory -Recurse -Force
    }
}
