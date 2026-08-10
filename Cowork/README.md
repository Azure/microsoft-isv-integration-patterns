# Cowork data platform custom MCP plugin

This pattern builds a Microsoft 365 app package that exposes approved remote
Snowflake, Databricks, and MongoDB MCP servers to Cowork. Each provider accepts
multiple connector entries, so one package can expose separate customer
accounts, workspaces, clusters, or environments. The package also includes a
runtime skill that guides safe data discovery and analytics.

The repository contains templates only. Tenant endpoints, OAuth vault
references, publisher metadata, and brand assets remain outside source control.

> **Preview compatibility:** This package intentionally follows the
> `agentSkills` and `agentConnectors.remoteMcpServer` pattern in the supplied
> Cowork examples. These extensions are not documented in the current public
> Microsoft 365 app schema. Confirm that the target tenant and upload channel
> are enabled for the Cowork preview. See
> [Primary-source research](docs/research.md).

## Contents

| Path | Purpose |
| --- | --- |
| `plugin.config.template.json` | Copyable, non-secret tenant configuration pattern |
| `plugin.config.schema.json` | JSON Schema for configuration tooling and validation |
| `manifest.template.json` | Microsoft 365 app manifest template |
| `build.ps1` | Interactive and automated package builder |
| `skills/data-platform-analytics/SKILL.md` | Skill included in the generated app package |
| `docs/architecture.md` | Components and trust boundaries |
| `docs/security.md` | Deployment security checklist |
| `docs/troubleshooting.md` | Common build and runtime failures |

## Prerequisites

- Windows PowerShell 5.1 or PowerShell 7.
- A Microsoft 365 tenant that permits custom app upload.
- Access to the Cowork preview that accepts `agentSkills` and
  `agentConnectors`.
- A tenant administrator who can upload and approve the app and its
  connections.
- One or more remote MCP servers:
  - an organization-approved Snowflake MCP endpoint;
  - an organization-approved Databricks MCP endpoint;
  - an organization-approved MongoDB MCP endpoint.
- Existing OAuth Plugin Vault connection reference IDs when the endpoints use
  OAuth. Reference IDs are identifiers, not client secrets or tokens.
- A 192 x 192 pixel full-color PNG icon and a 32 x 32 pixel transparent outline
  PNG icon that meet Microsoft 365 app requirements.

The builder requires HTTPS for publisher and MCP URLs. It does not deploy MCP
servers, register OAuth clients, or create vault connections.

## Configure

### Guided configuration

From this directory:

```powershell
.\build.ps1 -Interactive
```

The builder asks only for non-secret package metadata. It generates a new app
ID by default and saves the answers in the gitignored `plugin.config.json`.
Specify how many Snowflake, Databricks, and MongoDB entries the customer needs.
Zero is valid for an unused provider.

### File-based configuration

```powershell
Copy-Item .\plugin.config.template.json .\plugin.config.json
```

Update `plugin.config.json`:

1. Replace the all-zero `app.id` with a tenant app GUID.
2. Set publisher URLs, app text, color, and PNG paths.
3. Add one array entry per required MCP connection and set its unique `id`,
   environment-specific display name, and remote MCP HTTPS URL. Connector IDs
   must be unique across every provider.
4. Set `enabled` to `false` only when retaining an entry that should not be
   emitted into the package.
5. For OAuth endpoints, set `authorization.type` to `OAuthPluginVault` and
   supply the administrator-provided `referenceId`.
6. Remove `authorization` from a connector only when its endpoint deliberately
   uses no manifest-level authorization.

Do not put client secrets, access tokens, passwords, personal access tokens, or
private keys in any configuration field.

## Build

```powershell
.\build.ps1
```

The script validates high-risk manifest constraints, copies the supplied
icons, includes the runtime skill, derives `validDomains`, and writes a package
under `dist/`. The ZIP contains:

```text
manifest.json
color.png
outline.png
skills/
  data-platform-analytics/
    SKILL.md
```

The package must contain these files at its root; do not zip the `dist`
directory itself.

## Install in a tenant

1. Inspect the ZIP and generated `manifest.json`.
2. Have a Microsoft 365 tenant administrator upload the ZIP through the
   integrated-app/custom-app workflow in the Microsoft 365 admin center.
3. Complete any requested admin consent, connector approval, and OAuth Plugin
   Vault connection assignment.
4. Assign the app to a pilot group before broad deployment.
5. In Cowork, confirm the **Data Platform Analytics** skill appears.
6. Run a read-only metadata request against each enabled connector.

Tenant upload and approval are intentionally not automated. They are privileged
deployment decisions and provide the administrator a final review point.

## Update

Keep `app.id` unchanged, increment `app.version`, rebuild, inspect the diff in
the generated manifest, and upload the replacement package. Changing the app ID
creates a separate app rather than updating the existing installation.

## Remove

Use the Microsoft 365 admin center to unassign or remove the custom app.
Separately revoke its OAuth Plugin Vault connections and MCP-server access when
they are no longer needed.

## Copilot-guided workflows

Repository Copilot users can invoke:

- `configure-cowork-data-platform-mcp` to gather inputs, build the package, and
  guide tenant installation. Customers can point Copilot at this repository and
  invoke that skill for a question-by-question setup workflow.
- `install-scout-data-platform-plugins` to install provider-maintained
  Snowflake or Databricks plugins in Microsoft Scout Desktop. Scout is a
  separate product surface under `../Scout`.

The setup is guided by a skill, but is not fully automated. The skill can
collect non-secret values, generate configuration, run validation, build the
ZIP, and guide verification. A customer or administrator must separately
provision and approve MCP endpoints, provider identities, OAuth Plugin Vault
connections, tenant consent, app upload, and pilot assignment.

## Additional documentation

- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Verified primary-source research](docs/research.md)
