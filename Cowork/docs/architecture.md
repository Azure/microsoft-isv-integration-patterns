# Architecture

## Components

```text
Microsoft 365 tenant
  |
  +-- Cowork
       |
       +-- Custom app manifest
       |    +-- Data Platform Analytics skill
       |    +-- Snowflake agent connector (optional)
       |    +-- Databricks agent connector (optional)
       |
       +-- OAuth Plugin Vault reference (when configured)
              |
              +-- Organization-approved remote MCP endpoint
                       |
                       +-- Snowflake or Databricks authorization and tools
```

The app package contains metadata, connector endpoint URLs, OAuth vault
reference IDs, icons, and the skill. It contains no provider credentials.

This architecture targets the Cowork preview manifest extensions demonstrated
by the supplied example packages. The public Microsoft 365 Copilot
declarative-agent model uses separate declarative-agent and plugin manifests;
see [Primary-source research](research.md) before targeting a non-preview
channel.

## Build-time flow

1. The operator creates a tenant-specific `plugin.config.json`.
2. `build.ps1` validates app metadata, HTTPS URLs, connector settings, and
   local PNG paths.
3. The builder converts enabled provider entries into `agentConnectors`.
4. Hosts from publisher and MCP URLs become `validDomains`.
5. The builder stages the manifest, icons, and skill and creates a root-level
   ZIP package.

`manifest.template.json` is intentionally generic. Tenant values belong in the
gitignored configuration, not in the reusable template.

## Runtime flow

1. A user invokes the included data-platform skill in Cowork.
2. The skill identifies the intended provider and target environment.
3. Cowork discovers tools from the selected remote MCP connector.
4. The connection uses its tenant-approved authorization configuration.
5. The remote server enforces provider identity, role, workspace, warehouse,
   catalog, and data-policy controls.
6. Tool results return to Cowork for presentation to the user.

The app manifest does not replace Snowflake or Databricks authorization.
Least-privilege provider roles and endpoint-side tool controls remain the
primary enforcement boundary.

## Scout Desktop path

Scout installation is independent from the Cowork package and lives in the
top-level `Scout` directory. The provider installers register
`.github/plugin/marketplace.json` with Scout's bundled Copilot CLI and install
skills from official provider repositories. Directory junctions expose those
installed skills to Scout's Skills UI.

This repository does not vendor the provider plugins, and updating the Cowork
package does not update Scout plugins. Marketplace entries pin provider source
to reviewed immutable commit SHAs.
