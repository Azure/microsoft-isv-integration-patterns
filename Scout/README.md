# Microsoft Scout data platform plugins

This directory contains the Microsoft Scout Desktop integration pattern.
The installers add provider-maintained Snowflake, Databricks, and MongoDB
plugins to Scout.

| Plugin | Marketplace | Upstream source |
| --- | --- | --- |
| Snowflake Cortex Code | [Snowflake](snowflake/README.md) | [Snowflake-Labs/snowflake-ai-kit](https://github.com/Snowflake-Labs/snowflake-ai-kit) |
| Databricks Agent Skills | [Databricks](databricks/README.md) | [databricks/databricks-agent-skills](https://github.com/databricks/databricks-agent-skills) |
| MongoDB Atlas Agent Skills | [MongoDB](mongodb/README.md) | [mongodb/agent-skills](https://github.com/mongodb/agent-skills) |

The [Cowork custom MCP app package](../Cowork/README.md) is a separate,
top-level product surface. It builds a tenant-specific Microsoft 365 app
package that connects Cowork to one or more remote Snowflake, Databricks, and
MongoDB MCP servers.

The repository-level Scout catalog is
`.github/plugin/marketplace.json`. It references provider-owned public GitHub
repositories; provider plugin source is not vendored here.

## Install

Choose Snowflake, Databricks, MongoDB, or All, then pass that selection to the
installer:

```powershell
.\Scout\install.ps1 -Platform Snowflake
.\Scout\install.ps1 -Platform Databricks
.\Scout\install.ps1 -Platform MongoDB
.\Scout\install.ps1 -Platform All
```

## Choose a pattern

| Need | Pattern |
| --- | --- |
| Expose remote Snowflake, Databricks, or MongoDB MCP tools in Cowork | Build the sibling [Cowork package](../Cowork/README.md) |
| Add provider-authored skills to Scout Desktop | Run the provider's `install.ps1` |
| Support both experiences | Install both; their configuration and lifecycle remain independent |

Review each provider's license, security guidance, and preview status before
production deployment.

The Cowork package uses preview manifest extensions from the supplied examples.
They are not part of the currently documented public Microsoft 365 app schema;
review the [compatibility research](../Cowork/docs/research.md) before
deployment.
