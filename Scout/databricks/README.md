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

Scout resolves the manifest's remote source and installs the latest commit from
the `main` branch of the Databricks repository. The provider source is
downloaded into Scout's plugin cache, not this repository.

## Update

Run the same command again:

```powershell
.\install.ps1
```

The script refreshes the marketplace and updates an existing installation to
the latest available `main` branch commit. This intentionally follows upstream
changes without requiring a SHA update in this repository.

## Uninstall

From the `Scout` directory:

```powershell
.\uninstall.ps1 -PluginName databricks
```

The script removes only skill junctions owned by this plugin before
uninstalling it. Restart Scout afterward. Uninstalling does not change the
upstream repository or your Databricks configuration.

## Source and support

- [Databricks Agent Skills source](https://github.com/databricks/databricks-agent-skills)
- [Plugin marketplace documentation](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
- [Databricks Agent Skills issues](https://github.com/databricks/databricks-agent-skills/issues)

The upstream plugin is maintained and licensed by Databricks. Review its
license and security guidance before installation.
