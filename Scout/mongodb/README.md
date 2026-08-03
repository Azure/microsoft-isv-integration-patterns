# MongoDB plugin for Microsoft Scout

This marketplace installs the official `mongodb-atlas` plugin directly from
[mongodb/agent-skills](https://github.com/mongodb/agent-skills). The MongoDB
plugin is not copied into this repository.

The plugin includes MongoDB skills for schema design, natural-language queries,
query optimization, Search and Vector Search, Atlas Stream Processing, and
connection guidance. It connects to the MongoDB-hosted Atlas MCP server.

## Prerequisites

- Microsoft Scout Desktop for Windows.
- Git and access to the public GitHub repositories.
- A [MongoDB Atlas account](https://www.mongodb.com/cloud/atlas/register).
- Browser access to complete Atlas OAuth authentication. The first request that
  uses the hosted MCP server prompts you to sign in.

See the [MongoDB Agent Skills documentation](https://www.mongodb.com/docs/agent-skills/)
and [MongoDB MCP Server documentation](https://www.mongodb.com/docs/mcp-server/get-started/)
for current requirements and supported capabilities.

## Install

Run from this directory in PowerShell:

```powershell
.\install.ps1
```

The script locates the Copilot CLI bundled with Microsoft Scout, points it at
Scout's private runtime directory (`~/.scout/copilot`), and installs
`mongodb-atlas` from this marketplace. It creates directory junctions under
`~/.scout/m-skills` so the upstream skills appear in Scout's Skills UI. Restart
Scout after it completes.

Scout resolves the manifest's remote source and installs
`plugins/mongodb-atlas` from the `main` branch of the MongoDB repository. The
provider source is downloaded into Scout's plugin cache, not this repository.

The Atlas plugin uses MongoDB's hosted MCP server with OAuth. For MongoDB
Community, Enterprise Advanced, or another self-managed deployment, use the
upstream [`mongodb` plugin instructions](https://github.com/mongodb/agent-skills/blob/main/README.community.md)
instead.

## Update

Run the same command again:

```powershell
.\install.ps1
```

The script refreshes the marketplace and updates an existing installation.

Updates are explicit; upstream changes do not alter an installed plugin until
you run the installer again.

## Uninstall

```powershell
$env:COPILOT_HOME = Join-Path $HOME ".scout\copilot"
$copilot = Get-ChildItem "C:\Program Files\Microsoft Scout\resources\app.asar.unpacked\node_modules\@github" -Recurse -Filter copilot.exe | Select-Object -First 1 -ExpandProperty FullName
& $copilot plugin uninstall "mongodb-atlas@microsoft-isv-integration-patterns"
```

Restart Scout afterward. Uninstalling does not change your MongoDB Atlas
account or database configuration.

## Source and support

- [MongoDB Agent Skills source](https://github.com/mongodb/agent-skills)
- [MongoDB Agent Skills documentation](https://www.mongodb.com/docs/agent-skills/)
- [MongoDB MCP Server documentation](https://www.mongodb.com/docs/mcp-server/get-started/)
- [Plugin marketplace documentation](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
- [MongoDB Agent Skills issues](https://github.com/mongodb/agent-skills/issues)

The upstream plugin is maintained and licensed by MongoDB. Review its license
and security guidance before installation.
