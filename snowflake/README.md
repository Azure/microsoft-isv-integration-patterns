# Snowflake MCP for Copilot Studio

This folder contains a certification starter package for exposing a
Snowflake-managed Model Context Protocol (MCP) server in Microsoft Copilot
Studio. It follows Microsoft's certified MCP connector shape: an OpenAPI 2.0
definition, OAuth connection metadata, an icon, and publisher documentation.

The connector uses Snowflake's Streamable HTTP endpoint directly. It does not
proxy, store, or transform Snowflake data.

## Package contents

- `connector/apiDefinition.swagger.json`: OpenAPI 2.0 MCP connector definition.
- `connector/apiProperties.json`: OAuth and publisher metadata.
- `connector/icon.png`: 128 x 128 connector icon.
- `intro.md`: certification and customer-facing setup documentation.
- `docs/certification-research.md`: sourced certification requirements and
  identified submission risks.
- `scripts/build_source_package.py`: deterministic source-package builder.
- `scripts/generate_icon.py`: dependency-free icon generator.
- `tests/test_connector.py`: structural and certification-readiness checks.
- `dist/snowflake-copilot-studio-connector-source.zip`: generated source
  package.

## Configure the connector

The Snowflake endpoint is configured by each user when they create a
connection. The connector asks for:

| Connection value | Example |
|---|---|
| Snowflake account identifier | `myorg-myaccount` |
| Database | `MY_DATABASE` |
| Schema | `MY_SCHEMA` |
| MCP server | `MY_MCP_SERVER` |

The account identifier is restricted to the Snowflake domain by composing
`https://<account-identifier>.snowflakecomputing.com`; users do not provide an
arbitrary URL. The connector uses Microsoft's `dynamichosturl` policy for the
account authority and `routerequesttoendpoint` for the database, schema, and MCP
server path. The same account identifier selects the Snowflake OAuth endpoints.

The checked-in files remain publisher templates. Replace these values before
import and certification:

| Token | Value |
|---|---|
| `REPLACE_WITH_REDIRECT_URL` | Redirect URL generated for the imported connector |
| `REPLACE_WITH_AUTHORIZED_PUBLISHER` | Publisher legally authorized to submit the integration |

Do not commit OAuth client secrets. Microsoft receives production client
credentials through Partner Center, not through these public connector files.

### Snowflake prerequisites

1. Create a Snowflake-managed MCP server.
2. Prefer one governed Cortex Agent tool. If SQL is exposed, use a separate
   MCP server, a dedicated least-privileged role, and `read_only: true`.
3. Grant the user's default OAuth role only the required `USAGE` privileges on the
   warehouse, database, schema, MCP server, and downstream objects.
4. Configure a confidential OAuth client with Microsoft's generated redirect
   URL. Restrict allowed roles and set `OAUTH_USE_SECONDARY_ROLES = NONE`.
5. Verify the endpoint uses this form:

   ```text
   https://<account_url>/api/v2/databases/<database>/schemas/<schema>/mcp-servers/<name>
   ```

## Validate and build

From the repository root:

```powershell
python -m unittest discover -s snowflake\tests -v
python snowflake\scripts\build_source_package.py
python -m unittest discover -s snowflake\tests -v
```

The build writes
`snowflake/dist/snowflake-copilot-studio-connector-source.zip`. The archive is
deterministic and contains only the public connector source artifacts.

For a live endpoint check after replacing the publisher tokens and obtaining
an access token:

```powershell
$headers = @{
  Authorization = "Bearer $env:SNOWFLAKE_MCP_ACCESS_TOKEN"
  Accept = "application/json, text/event-stream"
  "Content-Type" = "application/json"
}
$body = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"connector-validation","version":"1.0"}}}'
Invoke-WebRequest -Method Post -Uri "https://<account_url>/api/v2/databases/<database>/schemas/<schema>/mcp-servers/<name>" -Headers $headers -Body $body
```

## Certification boundary

This repository can validate the public source artifacts, but it cannot produce
the final Partner Center submission without publisher-owned resources. The
authorized publisher must still:

1. Confirm it owns or is authorized by Snowflake to publish the integration.
2. Supply a production HTTPS endpoint and multitenant OAuth configuration.
3. Import the connector into a Power Platform solution and run Solution Checker.
4. Export separate connector and test-flow solutions.
5. Build the Package Deployer archive and outer ZIP containing `intro.md`.
6. Run Microsoft's `ConnectorPackageValidator.ps1`.
7. Provide Microsoft with test users and instructions that exercise every tool.

See [intro.md](intro.md) and
[certification research](docs/certification-research.md) before submission.

## Security

- Never grant the MCP role to `PUBLIC`.
- Never put passwords, OAuth secrets, access tokens, or test credentials in
  these files or in the final public connector repository.
- Test allowed and denied users, roles, objects, and operations.
- Do not log authorization headers or confidential Snowflake results.
- Review the repository [security guidance](../SECURITY.md).

## References

- [Microsoft MCP server certification](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification)
- [Connect an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
- [Prepare connector files for certification](https://learn.microsoft.com/en-us/connectors/custom-connectors/certification-submission)
- [Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp)
