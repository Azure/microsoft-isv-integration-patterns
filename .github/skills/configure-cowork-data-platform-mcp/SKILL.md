---
name: configure-cowork-data-platform-mcp
description: Configure, build, and prepare tenant installation of the Cowork custom MCP app package for Snowflake and Databricks. Use when a user asks to create, configure, package, install, or update the Cowork data platform MCP plugin.
---

# Configure the Cowork Data Platform MCP Plugin

Work from `Cowork`. Never request passwords, client secrets, access
tokens, refresh tokens, or private keys.

## Gather inputs

Ask one focused question at a time and reuse values already supplied. Collect:

1. Provider selection: Snowflake, Databricks, or both.
2. Microsoft 365 app ID, or permission to generate a new GUID.
3. Publisher name, HTTPS website, privacy, and terms URLs.
4. App names, descriptions, accent color, and paths to the required PNG icons.
5. For each enabled provider, the remote MCP HTTPS endpoint.
6. Whether the endpoint uses an existing `OAuthPluginVault` connection. If so,
   collect only its reference ID, never OAuth credentials.

Explain that the endpoint and OAuth vault connection must already exist and be
approved by the tenant administrator.

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

## Update

Increment `app.version`, rebuild, and have the tenant administrator upload the
new package. Keep `app.id` unchanged for an update.
