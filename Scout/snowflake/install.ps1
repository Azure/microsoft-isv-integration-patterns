[CmdletBinding()]
param(
    [string]$MarketplaceSource = "https://github.com/Azure/microsoft-isv-integration-patterns",
    [string]$ScoutHome = (Join-Path $HOME ".scout\copilot"),
    [string]$ScoutSkillsHome = (Join-Path $HOME ".scout\m-skills")
)

$arguments = @{} + $PSBoundParameters
$arguments.PluginName = "snowflake-cortex-code"
& (Join-Path $PSScriptRoot "..\install.ps1") @arguments