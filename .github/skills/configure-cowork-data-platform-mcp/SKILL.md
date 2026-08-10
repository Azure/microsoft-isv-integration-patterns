---
name: configure-cowork-data-platform-mcp
description: Configure, build, and prepare tenant installation of the Cowork custom MCP app package for one or more Snowflake, Databricks, and MongoDB MCP connections. Use when a customer asks to create, configure, package, install, or update the Cowork data platform MCP plugin.
---

# Configure the Cowork Data Platform MCP Plugin

Work from `Cowork`. Never request passwords, client secrets, access
tokens, refresh tokens, or private keys.

## Gather inputs

Ask one focused question at a time and reuse values already supplied. Collect:

1. Provider selection: Snowflake, Databricks, MongoDB, or any combination.
2. The number of MCP connector entries for each selected provider. Treat each
   environment, account, workspace, cluster, or deployment as a separate entry.
3. For every entry, collect a unique lowercase connector ID, a customer-facing
   display name, and a description that clearly identifies its environment.
4. Microsoft 365 app ID, or permission to generate a new GUID.
5. Publisher name, HTTPS website, privacy, and terms URLs.
6. App names, descriptions, accent color, and paths to the required PNG icons.
7. For each connector entry, the remote MCP HTTPS endpoint.
8. Whether each endpoint uses an existing `OAuthPluginVault` connection. If so,
   collect only its reference ID, never OAuth credentials.

Explain that the endpoint and OAuth vault connection must already exist and be
approved by the tenant administrator.

Before building, summarize every connector as provider, unique ID, display name,
environment, endpoint hostname, and authorization mode. Resolve duplicate IDs
or ambiguous display names with the user.

## Build

Prefer interactive generation:

```powershell
.\build.ps1 -Interactive
```

For automation, copy `plugin.config.template.json` to the gitignored
`plugin.config.json`, update the non-secret values, and run:

```powershell
.\build.ps1
```

Do not replace the JSON template itself with tenant-specific values. If the
build fails, fix the reported field or missing icon; do not bypass validation.

## Install

1. Inspect the generated ZIP and verify `manifest.json`, `color.png`,
   `outline.png`, and `skills/data-platform-analytics/SKILL.md` are at the
   package root.
2. Give the generated package path to the user.
3. Direct a tenant administrator to upload the package through the Microsoft
   365 admin center integrated-app workflow and complete any required
   connector/OAuth approval.
4. Have an allowed pilot user open Cowork, confirm the skill is visible, and
   run a read-only metadata query against each enabled provider.

Never claim installation is complete until the tenant upload and pilot query
have succeeded.

## Scope

This skill guides the customer through configuration, validation, packaging,
and verification. It does not provision remote MCP servers, create provider
identities, create OAuth Plugin Vault connections, grant tenant consent, or
upload the package on behalf of an administrator. Clearly identify the owner
and prerequisite for each incomplete external step instead of implying the
workflow is fully automated.

## Update

Increment `app.version`, rebuild, and have the tenant administrator upload the
new package. Keep `app.id` unchanged for an update.
