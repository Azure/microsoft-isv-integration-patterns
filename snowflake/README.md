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
- `assets/snowflake.svg`: authoritative Snowflake icon from Azure/MCP.
- `connector/icon.png`: 128 x 128 rasterized connector icon.
- `THIRD-PARTY-NOTICES.md`: source and license notice for the icon.
- `intro.md`: certification and customer-facing setup documentation.
- `docs/certification-research.md`: sourced certification requirements and
  identified submission risks.
- `scripts/build_source_package.py`: deterministic source-package builder.
- `scripts/deploy_connector.py`: creates or updates the connector with both JSON
  artifacts, including connection parameters and policies.
- `scripts/validate_connection.py`: direct endpoint lifecycle, discovery,
  optional tool execution, and optional OAuth refresh check.
- `tests/`: offline connector contract and validation-script regression checks.
- `dist/snowflake-copilot-studio-connector-source.zip`: generated source
  package.

## Configure the connector

The Snowflake endpoint is configured by each user when they create a
connection. The connector asks for:

| Connection value | Example |
|---|---|
| Snowflake account identifier | `myorg-myaccount` |
| OAuth client ID | Value returned by `SYSTEM$SHOW_OAUTH_CLIENT_SECRETS` |
| OAuth client secret | Secret returned by `SYSTEM$SHOW_OAUTH_CLIENT_SECRETS` |
| OAuth scope | `refresh_token session:role:MCP_ACCESS_ROLE` |
| Database | `MY_DATABASE` |
| Schema | `MY_SCHEMA` |
| MCP server | `MY_MCP_SERVER` |

The connector builds the **complete MCP URL from each connection's inputs**:

```text
https://<account-identifier>.snowflakecomputing.com/api/v2/databases/<database>/schemas/<schema>/mcp-servers/<mcpServer>
```

With the example values above, requests go to:

```text
https://myorg-myaccount.snowflakecomputing.com/api/v2/databases/MY_DATABASE/schemas/MY_SCHEMA/mcp-servers/MY_MCP_SERVER
```

Do not enter a full URL in the account field. Use the public organization-account
hostname prefix with hyphens, not underscores. Enter database, schema, and server
names separately, without qualification, quotes, or slashes. Use their actual
stored case, normally uppercase for unquoted Snowflake identifiers. These inputs
are passed through, not uppercased or URL-encoded by the policies. The connector
form supports simple unquoted object names; quoted names requiring URL encoding
need a separately configured endpoint.

The `dynamichosturl` policy sets the account authority and
`routerequesttoendpoint` sets the full Snowflake MCP path. `/mcp` and
`account-identifier.snowflakecomputing.com` in the Swagger are logical
placeholders, not the backend URL. Both policies must be deployed. A third
policy sets `Accept: application/json, text/event-stream` for Streamable HTTP
responses, including Snowflake's streamed `tools/call` results.

The same account input selects `/oauth/authorize` and `/oauth/token-request`.
Customer-specific client credentials and scope are substituted by the OAuth
templates. `PLACEHOLDER_CLIENTID` is intentional for this bring-your-own-client
pattern; customers enter the real ID and secret in their connection, not in source.

## Deploy or update the connector

**Importing only `apiDefinition.swagger.json` is not sufficient.** Power Apps'
OpenAPI import does not automatically load the sibling `apiProperties.json`.
Without it, the dynamic endpoint, seven input fields, OAuth templates, and
request policies are missing.

From the repository root, install the Microsoft connector CLI if not already
installed, sign in, and deploy both artifacts using the helper:

```powershell
python -m pip install paconn
paconn login
python snowflake\scripts\deploy_connector.py --environment "<environment-id>" --publisher "<authorized publisher name>"
```

For an existing connector, use its ID to **update rather than create a duplicate**:

```powershell
python snowflake\scripts\deploy_connector.py --environment "<environment-id>" --publisher "<authorized publisher name>" --connector-id "<existing-connector-id>"
```

The helper deploys the Swagger, properties, and icon together. It supplies the
publisher name in a temporary properties file and omits `stackOwner` there to
work around the documented paconn update limitation. It does not change the
certification source, request secrets, create a Snowflake integration, or create
a Power Platform connection. The temporary file is removed after deployment.
See [Microsoft's CLI guidance](https://learn.microsoft.com/en-us/connectors/custom-connectors/paconn-cli).

After deployment:

1. Open the custom connector's **Security** page and copy its generated redirect
   URL. `GlobalPerConnector` means the callback is connector-specific.
2. Register that callback in Snowflake as described below, then create a new
   connection and enter all seven values. An updated connector can still have
   old connections with missing or stale inputs; recreate those connections.
3. Verify the three policies are scoped to `InvokeMCP` and that the connection
   form has account, client ID, client secret, scope, database, schema, and server.
4. Add or refresh the MCP tool in Copilot Studio using the new connection.
   Verify discovery and one approved tool call there, not only in a REST test.

The checked-in publisher value remains `REPLACE_WITH_AUTHORIZED_PUBLISHER`.
Replace it with the legally authorized publisher before certification. Never
commit OAuth client secrets.

## Snowflake prerequisites

Create and test a Snowflake-managed MCP server. Prefer one governed Cortex Agent
tool. If SQL is exposed, use a separate server, a dedicated least-privileged
role, and `read_only: true`.

### Role, warehouse, and tool privileges

Run the following as an appropriately privileged Snowflake administrator,
substituting existing objects and the intended user. This example is for a
Cortex Agent-based server:

```sql
CREATE ROLE MCP_ACCESS_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_AGENT_USER TO ROLE MCP_ACCESS_ROLE;
GRANT USAGE ON WAREHOUSE MY_WAREHOUSE TO ROLE MCP_ACCESS_ROLE;
GRANT USAGE ON DATABASE MY_DATABASE TO ROLE MCP_ACCESS_ROLE;
GRANT USAGE ON SCHEMA MY_DATABASE.MY_SCHEMA TO ROLE MCP_ACCESS_ROLE;
GRANT USAGE ON MCP SERVER MY_DATABASE.MY_SCHEMA.MY_MCP_SERVER TO ROLE MCP_ACCESS_ROLE;
GRANT USAGE ON AGENT MY_DATABASE.MY_SCHEMA.MY_AGENT TO ROLE MCP_ACCESS_ROLE;
GRANT ROLE MCP_ACCESS_ROLE TO USER <username>;
ALTER USER <username> SET DEFAULT_ROLE = MCP_ACCESS_ROLE DEFAULT_WAREHOUSE = MY_WAREHOUSE;
```

Review changes to defaults for users shared with other applications. A warehouse
grant alone does **not** set `DEFAULT_WAREHOUSE`; a null default can prevent MCP
initialization. The explicit `session:role:MCP_ACCESS_ROLE` scope selects the
primary role; when no specific role scope is supplied, the user's default role
is used.

Grant only the additional privileges needed by the configured tools:

| Underlying object | Required access |
|---|---|
| Cortex Agent | `USAGE` on the agent and applicable Cortex database role |
| Cortex Search service | `USAGE` |
| Semantic view for Cortex Analyst | `SELECT` |
| Tables queried by the agent or SQL tool | `SELECT` |
| UDF or stored procedure | `USAGE` on the exact function/procedure signature |

`USAGE` on an MCP server permits discovery; it does not grant access to all
underlying tools or data. Agent tools can be omitted from discovery when the
active role lacks agent access. See
[Snowflake MCP access control](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp#access-control).

### Native Snowflake OAuth

This connector implements **Snowflake-native OAuth authorization code flow with
a confidential custom client**, not External OAuth or dynamic client registration.
After deploying the connector and obtaining its actual callback:

```sql
CREATE SECURITY INTEGRATION COPILOT_STUDIO_MCP_OAUTH
  TYPE = OAUTH
  OAUTH_CLIENT = CUSTOM
  ENABLED = TRUE
  OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
  OAUTH_REDIRECT_URI = '<exact callback from the deployed connector>'
  OAUTH_ISSUE_REFRESH_TOKENS = TRUE
  OAUTH_USE_SECONDARY_ROLES = NONE
  ALLOWED_ROLES_LIST = ('MCP_ACCESS_ROLE');

SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('COPILOT_STUDIO_MCP_OAUTH');
```

Handle the returned ID and secret securely. Use
`refresh_token session:role:MCP_ACCESS_ROLE` as the space-delimited connection
scope. The role must exist with that case, be granted to the user, and be allowed
by the integration. The user must consent to refresh access. Token and refresh
requests use `application/x-www-form-urlencoded` and Snowflake-supported
`client_secret_post`; the bearer access token authenticates MCP requests.

Compatibility checks:

- The callback must match the deployed connector's generated URL, not a generic
  URL copied from another connector.
- These templates do not implement PKCE. An integration enforcing PKCE needs a
  PKCE-capable client/configuration; do not disable organizational controls to
  make this template work.
- Check inherited `OAUTH_AUTHORIZATION_SERVER` at schema, database, and account
  level. If it binds this server to Entra/Okta External OAuth, configure a separate
  connector with that provider's endpoints, scopes, audience, and client
  registration. These native Snowflake endpoints are not interchangeable.
- Allow the actual Power Platform region's outbound infrastructure through
  Snowflake network policies for token exchange, refresh, and MCP access.
  Browser sign-in succeeding does not prove that backend requests are allowed.
- This template builds public `snowflakecomputing.com` URLs. PrivateLink and
  other cloud domain configurations need separate connectivity validation; a
  SaaS client cannot automatically reach a private endpoint.

## Validate and build

From the repository root:

```powershell
python snowflake\scripts\build_source_package.py
python -B -m unittest discover -s snowflake\tests -v
```

The build writes
`snowflake/dist/snowflake-copilot-studio-connector-source.zip`. The archive is
deterministic and contains only public connector source artifacts and the
deployment/validation helpers. Package tests compare archived bytes to source.
Offline tests exercise template wiring and simulated HTTP responses; they do
**not** establish that a deployed Power Platform connection works.

### Live endpoint check

Supply a test access token securely through the process environment variable
`SNOWFLAKE_MCP_ACCESS_TOKEN`. The validator accepts either the same four endpoint
components as the connector or a complete public Snowflake MCP URL:

```powershell
python snowflake\scripts\validate_connection.py --account myorg-myaccount --database MY_DATABASE --schema MY_SCHEMA --mcp-server MY_MCP_SERVER
python snowflake\scripts\validate_connection.py --url "https://myorg-myaccount.snowflakecomputing.com/api/v2/databases/MY_DATABASE/schemas/MY_SCHEMA/mcp-servers/MY_MCP_SERVER"
```

The check performs `initialize`, `notifications/initialized`, and paginated
`tools/list`, preserving the negotiated protocol version and session header.
It accepts JSON and SSE responses and fails on HTTP, JSON-RPC, empty-tool, and
malformed-response errors. Redirects are refused to avoid forwarding credentials.
It prints status/counts, not tokens or tool results. It invokes no tools by default.

Explicitly opt into one approved test tool with its real input schema, for
example a read-only Cortex Agent test:

```powershell
python snowflake\scripts\validate_connection.py --account myorg-myaccount --database MY_DATABASE --schema MY_SCHEMA --mcp-server MY_MCP_SERVER --tool business_data_agent --arguments '{"text":"Summarize the approved test dataset."}'
```

To check refresh, securely supply `SNOWFLAKE_MCP_REFRESH_TOKEN`,
`SNOWFLAKE_OAUTH_CLIENT_ID`, and `SNOWFLAKE_OAUTH_CLIENT_SECRET` in the process
environment and append `--check-refresh`. The resulting access token is used for
the MCP checks. **Use a dedicated test OAuth session:** refresh can rotate or
consume the token; the validator does not save tokens or update an existing
Power Platform connection. Reconnect that test session if necessary.

The direct probe does not test the interactive authorization-code exchange,
Power Platform callback, deployed policies, or Copilot Studio's streaming client.
Final acceptance requires a new connection and discovery, an approved tool call,
and refresh after access-token expiry **inside Copilot Studio**.

### Troubleshooting

| Symptom | Check |
|---|---|
| Placeholder hostname or `/mcp` reached | Both artifacts and all three policies were deployed; inspect exported connector properties |
| OAuth consent fails | Exact callback, confidential client, allowed/granted role, scope case, PKCE requirement |
| `invalid_client` on token exchange | Client ID/secret, form encoding, and network policy; it is not proof of a bad secret |
| MCP returns `401` | Token expiry/account and inherited External OAuth issuer binding |
| Initialization fails | User's default warehouse and effective role's warehouse access |
| No tools or missing agent tool | MCP server and agent `USAGE`, plus applicable Cortex database-role access |
| Tool visible but invocation fails | Tool arguments and underlying object privileges, including `SELECT` where required |
| Discovery works but tool result fails | Streamable HTTP `Accept`, SSE response handling, timeout/size limits |

## Certification boundary

This repository can validate the public source artifacts, but it cannot produce
the final Partner Center submission without publisher-owned resources. The
authorized publisher must still:

1. Confirm it owns or is authorized by Snowflake to publish the integration.
2. Confirm the bring-your-own OAuth client pattern and provide certification
   test credentials in Partner Center.
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

## Icon attribution

The connector uses the Snowflake icon published in the
[Azure/MCP community registry](https://github.com/Azure/MCP/blob/main/community/registry/icons/snowflake.svg).
See [third-party notices](THIRD-PARTY-NOTICES.md) for its MIT license notice.

## References

- [Microsoft MCP server certification](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification)
- [Connect an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
- [Prepare connector files for certification](https://learn.microsoft.com/en-us/connectors/custom-connectors/certification-submission)
- [Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp)
- [Snowflake custom-client OAuth](https://docs.snowflake.com/en/user-guide/oauth-custom)
- [Snowflake streaming tool responses](https://docs.snowflake.com/en/release-notes/bcr-bundles/un-bundled/bcr-2405)
