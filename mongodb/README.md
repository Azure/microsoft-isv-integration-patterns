# MongoDB Atlas MCP for Copilot Studio

This folder contains a certification starter package for exposing MongoDB's
Atlas-hosted remote Model Context Protocol (MCP) server in Microsoft Copilot
Studio. It follows Microsoft's certified MCP connector shape: an OpenAPI 2.0
definition, OAuth connection metadata, an icon, and publisher documentation.

The connector sends Streamable HTTP requests directly to
`https://mcp.mongodb.com`. It does not proxy, store, or transform MongoDB data.

## Package contents

- `connector/apiDefinition.swagger.json`: OpenAPI 2.0 MCP connector definition.
- `connector/apiProperties.json`: fixed MongoDB OAuth and publisher metadata.
- `assets/mongodb.svg`: authoritative MongoDB icon from Azure/MCP.
- `connector/icon.png`: 128 x 128 rasterized connector icon.
- `THIRD-PARTY-NOTICES.md`: source and license notice for the icon.
- `intro.md`: certification and customer-facing setup documentation.
- `docs/certification-research.md`: sourced implementation findings.
- `scripts/build_source_package.py`: deterministic source-package builder.
- `tests/test_connector.py`: structural and certification-readiness checks.
- `dist/mongodb-copilot-studio-connector-source.zip`: generated source package.

## Configure the connector

Unlike the Snowflake integration, the remote endpoint and OAuth authorities are
fixed:

| Setting | Value |
|---|---|
| MCP server | `https://mcp.mongodb.com` |
| Authorization URL | `https://cloud.mongodb.com/oauth/authorize` |
| Token URL | `https://authorize.mongodb.com/tokens` |
| Refresh URL | `https://authorize.mongodb.com/tokens` |
| OAuth flow | Authorization code with PKCE |
| Scopes | None declared |

The checked-in files intentionally leave the confidential OAuth client ID and
client secret empty. Before import and certification, the authorized publisher
must create or obtain the production MongoDB OAuth client and populate the
following values:

| Field or token | Required value |
|---|---|
| `clientId` | MongoDB-issued production OAuth client ID |
| `clientSecret` | MongoDB-issued production OAuth client secret |
| `REPLACE_WITH_REDIRECT_URL` | Redirect URL registered for the connector |
| `REPLACE_WITH_AUTHORIZED_PUBLISHER` | Publisher legally authorized to submit the integration |

Never commit the populated client secret. Add production credentials only in
the secure connector or Partner Center submission workflow.

These authorization-code client fields are not the credentials from an Atlas
MCP configuration. MongoDB's separate programmatic-access model uses a
client-credentials flow and a different token endpoint.

### MongoDB prerequisites

1. Obtain authorization from MongoDB to publish the integration and register a
   production OAuth client for the Atlas-hosted MCP server.
2. Register the connector redirect URL on that OAuth client.
3. Ensure OAuth authorization-code flow with PKCE is supported by the target
   connector environment.
4. Prepare least-privileged MongoDB Atlas test users that can exercise every
   submitted tool.
5. Review the tools exposed to each user before connecting them to an agent.

## Validate and build

From the repository root:

```powershell
python -m unittest discover -s mongodb\tests -v
python mongodb\scripts\build_source_package.py
python -m unittest discover -s mongodb\tests -v
```

The build writes
`mongodb/dist/mongodb-copilot-studio-connector-source.zip`. The archive is
deterministic and contains only the public connector source artifacts. It
retains empty OAuth client fields and must not contain production secrets.

For a live endpoint check after configuring OAuth and obtaining an access token:

```powershell
$headers = @{
  Authorization = "Bearer ******"
  Accept = "application/json, text/event-stream"
  "Content-Type" = "application/json"
}
$body = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"connector-validation","version":"1.0"}}}'
Invoke-WebRequest -Method Post -Uri "https://mcp.mongodb.com" -Headers $headers -Body $body
```

## Certification boundary

This repository validates public source artifacts, but the authorized publisher
must still:

1. Supply and securely configure the production client ID and secret.
2. Confirm the generated redirect URL is registered with MongoDB.
3. Validate PKCE authorization in the target Power Platform environment.
4. Import the connector into a Power Platform solution and run Solution Checker.
5. Export separate connector and test-flow solutions.
6. Build the Package Deployer archive and outer ZIP containing `intro.md`.
7. Run Microsoft's `ConnectorPackageValidator.ps1`.
8. Provide Microsoft with test users and instructions for every exposed tool.

See [intro.md](intro.md) and
[certification research](docs/certification-research.md) before submission.

## Security

- Use least-privileged Atlas users and roles.
- Do not commit client secrets, access tokens, test credentials, or MongoDB data.
- Treat write, delete, index-management, and Atlas administration tools as
  privileged operations.
- Test allowed and denied users, projects, clusters, databases, and operations.
- Do not log authorization headers or confidential MongoDB results.
- Review the repository [security guidance](../SECURITY.md).

## Icon attribution

The connector uses the MongoDB icon published in the
[Azure/MCP community registry](https://github.com/Azure/MCP/blob/main/community/registry/icons/mongodb.svg).
See [third-party notices](THIRD-PARTY-NOTICES.md) for its MIT license notice.

## References

- [Azure/MCP MongoDB remote server metadata](https://github.com/Azure/MCP/blob/main/partners/servers/mongodb-remote-mcp-server.json)
- [MongoDB MCP Server documentation](https://www.mongodb.com/docs/mcp-server/get-started/)
- [Microsoft MCP server certification](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification)
- [Connect an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
- [Prepare connector files for certification](https://learn.microsoft.com/en-us/connectors/custom-connectors/certification-submission)
