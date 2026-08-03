# Databricks plugin for Microsoft Scout

This marketplace installs the `databricks` plugin directly from
[databricks/databricks-agent-skills](https://github.com/databricks/databricks-agent-skills).
The Databricks plugin is not copied into this repository.

## Prerequisites

- Microsoft Scout Desktop for Windows.
- Git and access to the public GitHub repositories.
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install)
  version 0.205 or later installed and available as `databricks` on your
  `PATH`.
- A Databricks workspace and
  [Databricks CLI authentication](https://docs.databricks.com/aws/en/dev-tools/cli/authentication)
  configured for the skills you use. See the
  [Databricks Agent Skills documentation](https://github.com/databricks/databricks-agent-skills)
  for any additional requirements.

Verify the Databricks CLI installation before installing the plugin:

```powershell
databricks version
```

## Install

Run from this directory in PowerShell:

```powershell
.\install.ps1
```

The script locates the Copilot CLI bundled with Microsoft Scout, points it at
Scout's private runtime directory (`~/.scout/copilot`), and installs
`databricks` from this marketplace. It creates directory junctions under
`~/.scout/m-skills` so the upstream skills appear in Scout's Skills UI. Restart
Scout after it completes.

Scout resolves the manifest's remote source and installs
`plugins/databricks/copilot` from the `main` branch of the Databricks
repository. The installation is pinned to the exact upstream commit resolved at
install time. The provider source is downloaded into Scout's plugin cache, not
this repository.

## Update

Run the same command again:

```powershell
.\install.ps1
```

The script refreshes the marketplace and updates an existing installation.

Updates are explicit; upstream changes do not alter an installed plugin until
you select **Update** in Scout.

## Uninstall

```powershell
$env:COPILOT_HOME = Join-Path $HOME ".scout\copilot"
$copilot = Get-ChildItem "C:\Program Files\Microsoft Scout\resources\app.asar.unpacked\node_modules\@github" -Recurse -Filter copilot.exe | Select-Object -First 1 -ExpandProperty FullName
& $copilot plugin uninstall "databricks@microsoft-isv-integration-patterns"
```

Restart Scout afterward. Uninstalling does not change the upstream repository or
your Databricks configuration.

## Source and support

- [Databricks Agent Skills source](https://github.com/databricks/databricks-agent-skills)
- [Plugin marketplace documentation](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
- [Databricks Agent Skills issues](https://github.com/databricks/databricks-agent-skills/issues)

The upstream plugin is maintained and licensed by Databricks. Review its
license and security guidance before installation.
