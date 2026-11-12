# Snowflake MCP

## Business purpose

Snowflake MCP enables Microsoft Copilot Studio agents to discover and invoke
tools hosted by a Snowflake-managed MCP server. A publisher can expose governed
Cortex Agent, Cortex Analyst, Cortex Search, read-only SQL, or approved custom
function and procedure tools without moving the MCP runtime outside Snowflake.

## Supported tools

Tools are discovered dynamically with MCP `tools/list` and invoked with
`tools/call`. The exact tools depend on the configured Snowflake-managed MCP
server and the connected user's role. Snowflake supports Cortex Agent, Cortex
Analyst, Cortex Search, SQL, and approved generic function or procedure tools.

For certification, list every enabled production tool here, including its
purpose, inputs, expected outputs, permissions, and test steps.

## Prerequisites

- A production Snowflake account with a managed MCP server.
- A dedicated warehouse and least-privileged role.
- A confidential OAuth client configured for Microsoft's connector redirect
  URL.
- A non-null default warehouse on the connecting Snowflake user, with warehouse
  `USAGE` granted to the effective OAuth role.
- A Microsoft Partner Center seller account with verified-publisher status.
- Legal authorization to publish an integration for the Snowflake service.
- Microsoft test credentials that can exercise every submitted tool.

## Setup and authentication

1. Create and test the Snowflake-managed MCP server with a dedicated role.
2. Deploy **both** `connector/apiDefinition.swagger.json` and
   `connector/apiProperties.json`, including the routing and Accept policies.
   Importing only the OpenAPI definition omits the connection inputs and dynamic
   OAuth configuration. The source package includes
   `scripts/deploy_connector.py`; see [deployment instructions](README.md#deploy-or-update-the-connector).
3. Copy the deployed connector's generated callback and register that exact
   value in a confidential custom Snowflake OAuth integration. Enable refresh
   tokens, restrict the allowed roles, and disable secondary roles.
4. Grant `USAGE` on the required warehouse, database, schema, MCP server, and
   applicable agent, search service, or function/procedure. Grant `SELECT`, not
   `USAGE`, on semantic views and tables needed by the tools, plus the applicable
   Cortex database role. Grant the access role to the user and set the user's
   default warehouse. Review the default role for clients without a role scope.
5. Obtain the integration's OAuth client ID and secret with
   `SYSTEM$SHOW_OAUTH_CLIENT_SECRETS`.
6. Create a new connection with the Snowflake organization-account identifier,
   OAuth client ID, OAuth client secret, scope, database, schema, and managed MCP
   server name. A typical scope is `refresh_token session:role:MCP_ACCESS_ROLE`;
   use the exact case of the granted, allowed role.
7. Add the connector to a Copilot Studio agent and verify discovery, an approved
   tool call, streamed responses, and token refresh after expiration. Recreate
   old connections with missing or stale inputs after updating the connector.

Each connection's complete MCP URL is built as follows:

```text
https://<account-identifier>.snowflakecomputing.com/api/v2/databases/<database>/schemas/<schema>/mcp-servers/<mcpServer>
```

The account field accepts only the hostname prefix, such as `myorg-myaccount`;
use hyphens, not underscores. Object inputs are separate simple names in their
stored case, normally uppercase, without qualification, quotes, or slashes.
The Swagger's `/mcp` path is replaced by the deployed routing policy.

OAuth tokens are passed directly from the Power Platform connection to the
Snowflake-managed MCP endpoint. Each customer supplies their client secret as a
secure connection parameter; it must not be committed with the connector
source.

This configuration uses native Snowflake OAuth and `client_secret_post` token
authentication. It does not support a server bound to an External OAuth issuer
without changing the OAuth configuration, or an integration requiring PKCE.
Do not disable organizational controls to bypass those requirements. Check
network policies for Power Platform backend access as well as browser login.

## Limitations

- The endpoint is specific to a Snowflake account, database, schema, and MCP
  server and is selected when each connection is created.
- The account input accepts an organization-account identifier, not a complete
  URL. The connector routes only to the `snowflakecomputing.com` domain.
- The connector requires Streamable HTTP; legacy standalone HTTP+SSE transport
  is unsupported. Request-scoped SSE responses within Streamable HTTP are
  supported and expected for Snowflake tool calls.
- The form does not encode quoted identifiers or support non-public Snowflake
  domains. Those configurations require a separately configured endpoint.
- Native OAuth only; External OAuth, enforced PKCE, and private networking
  require their own compatible configuration and validation.
- Tool availability is controlled by the connected Snowflake user and role.
- Changes to production tools can require connector recertification.
- Cortex services and warehouse usage can incur Snowflake charges.
- Large Cortex Agent responses must be tested against current Copilot Studio
  and connector response limits.

## Privacy and compliance

Requests and responses are processed by Microsoft Power Platform and Snowflake
under their respective customer agreements. Publishers must provide their own
production privacy policy, legal terms, data-handling disclosures, responsible
AI evidence, and support process before submission.

## Support

This repository is a reference implementation. Report implementation issues at
https://github.com/Azure/microsoft-isv-integration-patterns/issues.

Production publishers must replace this section with a staffed support URL,
support email, service website, privacy policy, and legal terms.
