# Microsoft Scout plugins

This directory contains Scout marketplace manifests for third-party agent
plugins. Each manifest references the provider's public GitHub repository, so
Scout installs and updates the provider's source directly. No provider plugin
content is vendored in this repository.

The repository-level catalog is `.github/plugin/marketplace.json`, the
conventional path Scout discovers when this GitHub repository is registered as
a marketplace. The provider directories contain focused manifests and
installation documentation for each integration.

| Plugin | Marketplace | Upstream source |
| --- | --- | --- |
| Snowflake Cortex Code | [Snowflake](snowflake/README.md) | [Snowflake-Labs/snowflake-ai-kit](https://github.com/Snowflake-Labs/snowflake-ai-kit) |
| Databricks Agent Skills | [Databricks](databricks/README.md) | [databricks/databricks-agent-skills](https://github.com/databricks/databricks-agent-skills) |
| MongoDB Atlas Agent Skills | [MongoDB](mongodb/README.md) | [mongodb/agent-skills](https://github.com/mongodb/agent-skills) |

Microsoft Scout Desktop does not currently expose plugin marketplace management
in its UI. Each provider directory includes a PowerShell installer that uses
Scout's bundled Copilot CLI and private runtime directory. Running the installer
again refreshes the marketplace and updates the plugin from its upstream source.

See the [plugin marketplace documentation](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
for the marketplace commands used by Scout's bundled runtime.
