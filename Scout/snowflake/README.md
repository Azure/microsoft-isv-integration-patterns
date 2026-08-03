# Snowflake plugin for Microsoft Scout

This marketplace installs the `snowflake-cortex-code` plugin directly from
[Snowflake-Labs/snowflake-ai-kit](https://github.com/Snowflake-Labs/snowflake-ai-kit).
The Snowflake plugin is not copied into this repository.

## Prerequisites

- Microsoft Scout Desktop for Windows.
- Git and access to the public GitHub repositories.
- [Snowflake Cortex Code CLI (CoCo)](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli)
  installed and available as `cortex` on your `PATH`.
- A configured Snowflake connection. Follow the
  [Snowflake AI Kit prerequisites](https://github.com/Snowflake-Labs/snowflake-ai-kit#prerequisites)
  to install the required Snowflake tooling and configure the connection.

Verify the Cortex Code CLI installation before installing the plugin:

```powershell
cortex --version
```

## Install

Run from this directory in PowerShell:

```powershell
.\install.ps1
```

The script locates the Copilot CLI bundled with Microsoft Scout, points it at
Scout's private runtime directory (`~/.scout/copilot`), and installs
`snowflake-cortex-code` from this marketplace. It creates directory junctions
under `~/.scout/m-skills` so the upstream skills appear in Scout's Skills UI.
Restart Scout after it completes.

Scout resolves the manifest's remote source and installs
`plugins/cortex-code` from the `main` branch of the Snowflake repository. The
provider source is downloaded into Scout's plugin cache, not this repository.

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
& $copilot plugin uninstall "snowflake-cortex-code@microsoft-isv-integration-patterns"
```

Restart Scout afterward. Uninstalling does not change the upstream repository or
your Snowflake configuration.

## Source and support

- [Snowflake AI Kit source](https://github.com/Snowflake-Labs/snowflake-ai-kit)
- [Plugin marketplace documentation](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
- [Snowflake AI Kit issues](https://github.com/Snowflake-Labs/snowflake-ai-kit/issues)

The upstream plugin is maintained and licensed by Snowflake. Review its license
and security guidance before installation.
