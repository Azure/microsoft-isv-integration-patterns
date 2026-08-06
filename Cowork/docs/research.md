# Primary-source research

Research was performed on August 5, 2026 against public Microsoft, Databricks,
and Snowflake documentation. The supplied Cowork examples were also inspected
because Cowork and Microsoft Scout are preview experiences whose package
extensions are not currently described in public Microsoft Learn content.

## Compatibility finding

The supplied examples use these Microsoft 365 app manifest extensions:

- `agentSkills`
- `agentConnectors[].toolSource.remoteMcpServer`

Those fields are the pattern implemented by this repository. They do not appear
in the current public Microsoft 365 app-manifest documentation. A tenant must
therefore be enabled for the Cowork/Scout preview that accepts these fields.
The standard public Microsoft 365 Copilot extensibility model uses a
`copilotAgents.declarativeAgents` reference, a declarative agent manifest, and
plugin manifests with `RemoteMCPServer` runtimes instead.

Do not submit this preview package to general Microsoft 365 validation channels
without first confirming the target channel accepts the Cowork extensions.

## Confirmed public Microsoft model

The public package model uses a root ZIP containing `manifest.json`, a 192 x
192 color PNG, and a 32 x 32 outline PNG. Declarative agents additionally
reference a declarative agent manifest through `copilotAgents`, and MCP plugins
use plugin manifest schema v2.4 with:

```json
{
  "type": "RemoteMCPServer",
  "auth": {
    "type": "OAuthPluginVault",
    "reference_id": "<connection-reference>"
  },
  "run_for_functions": [
    "*"
  ],
  "spec": {
    "url": "https://mcp.example.com/mcp"
  }
}
```

Public MCP plugin authentication supports `None` and `OAuthPluginVault`; API
key vault authentication is not supported for MCP plugins. Dynamic discovery
uses an empty `functions` array and `run_for_functions: ["*"]`.

Microsoft documents Agents Toolkit (`atk`) for validation, packaging,
provisioning, installation, and publishing of the public declarative-agent
model. Public documentation for a product named Microsoft Scout or its private
Copilot plugin marketplace was not found; the Scout scripts in this repository
follow the installed Scout runtime pattern verified by the existing project
implementation.

## Provider findings

### Databricks

Databricks documents managed MCP servers, while the `databrickslabs/mcp`
repository provides a Databricks Labs implementation for Unity Catalog
functions, Vector Search, and Genie spaces. The Labs project is beta/community
software and is not covered by Databricks SLAs. Its remote Databricks Apps
transport uses streamable HTTP and documents URLs of the form:

```text
https://<app-name>.databricksapps.com/api/mcp/
```

Confirm the specific managed or self-hosted server's OAuth flow before creating
the Microsoft 365 OAuth vault connection.

### Snowflake

The Snowflake Labs MCP server supports Cortex Search, Cortex Analyst, Cortex
Agent, object management, SQL execution, and semantic-view tools. Its
streamable HTTP transport is suitable for a remote deployment, but the
published project is self-hosted rather than a confirmed Snowflake-managed
public HTTPS endpoint. Snowflake role-based access controls remain effective
through the server's configured Snowflake identity.

## Primary sources

- [Microsoft 365 app model for agents](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-are-apps)
- [Microsoft 365 app manifest `copilotAgents`](https://learn.microsoft.com/en-us/microsoft-365/extensibility/schema/root-copilot-agents)
- [Declarative agent manifest v1.8](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.8)
- [Plugin manifest v2.4](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-manifest-2.4)
- [Build an MCP plugin](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/build-mcp-plugins)
- [Plugin authentication](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-authentication)
- [OAuth authentication for plugins](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-authentication-oauth)
- [Dynamic MCP tool discovery](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-dynamic-tool-discovery)
- [Microsoft 365 Agents Toolkit CLI](https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/microsoft-365-agents-toolkit-cli)
- [Databricks Labs MCP](https://github.com/databrickslabs/mcp)
- [Snowflake Labs MCP](https://github.com/Snowflake-Labs/mcp)
