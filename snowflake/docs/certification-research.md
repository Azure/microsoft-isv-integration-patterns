# Snowflake MCP certification research

Research date: September 25, 2026.

## Certification path

Microsoft currently certifies public MCP integrations through the verified
publisher Power Platform connector process. The publisher creates a Partner
Center **Connectors and Agents for Microsoft Copilot Studio** offer. The
publisher needs a verified seller account, production support, ownership or
control of the endpoint, complete authentication configuration, and test
credentials and instructions for every tool
([Microsoft MCP server certification](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification),
[verified-publisher certification](https://learn.microsoft.com/en-us/connectors/custom-connectors/submit-for-certification)).

An independent publisher that does not own the underlying service is not
eligible to submit directly. The submitting organization therefore needs
authorization from Snowflake or must establish that it controls the production
service
([Microsoft MCP server certification](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification#publisher-eligibility)).

## Connector and transport

The public connector source uses OpenAPI 2.0. Its MCP POST operation must include
`x-ms-agentic-protocol: mcp-streamable-1.0`. Copilot Studio supports Streamable
HTTP; standalone HTTP+SSE has not been supported since August 2025. The endpoint
must accept JSON-RPC POST requests and the client accept header
`application/json, text/event-stream`
([connect an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)).

The endpoint must use HTTPS with TLS 1.2 or later. The MCP transport also
requires origin validation and JSON or request-scoped SSE responses
([Marketplace certification policies](https://learn.microsoft.com/en-us/legal/marketplace/certification-policies#5000-connectors--agents-in-microsoft-copilot-studio),
[MCP Streamable HTTP transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)).

## Per-connection Snowflake endpoint

Power Platform supports per-connection backend routing. Values declared under
`properties.connectionParameters` can be read by policies with
`@connectionParameters('name')`
([Microsoft policy expressions](https://learn.microsoft.com/en-us/connectors/custom-connectors/policy-templates/expressions/expressions)).

This connector uses two Microsoft policy templates:

- `dynamichosturl` builds the authority from the user's Snowflake
  organization-account identifier. The template appends
  `.snowflakecomputing.com`, so the connection cannot supply an arbitrary host.
- `routerequesttoendpoint` builds the documented managed MCP path from the
  connection's database, schema, and MCP server values.

Both templates support connection-parameter expressions
([Set Host URL](https://learn.microsoft.com/en-us/connectors/custom-connectors/policy-templates/dynamichosturl/dynamichosturl),
[Route Request](https://learn.microsoft.com/en-us/connectors/custom-connectors/policy-templates/routerequesttoendpoint/routerequesttoendpoint)).
Microsoft's certified Cognitive Services Text Analytics connector combines
these same two policy types, and certified connectors such as Tribal SITS use
connection-derived host and path values
([Cognitive Services source](https://github.com/microsoft/PowerPlatformConnectors/blob/dev/certified-connectors/CognitiveServicesTextAnalytics/apiProperties.json),
[Tribal SITS source](https://github.com/microsoft/PowerPlatformConnectors/blob/dev/certified-connectors/Tribal%20-%20SITS/apiProperties.json)).

OAuth URL templates use `{placeholder}` substitution rather than policy
expressions. A `token:accountIdentifier` connection parameter backs
`{accountIdentifier}` in the authorization, token, and refresh URL templates.
This pattern is demonstrated by the certified Tribal SITS and Cognite Data
Fusion connectors
([Cognite source](https://github.com/microsoft/PowerPlatformConnectors/blob/dev/certified-connectors/Cognite%20Data%20Fusion/apiProperties.json)).
Snowflake documents the account-specific paths as `/oauth/authorize` and
`/oauth/token-request`
([Snowflake OAuth endpoints](https://docs.snowflake.com/en/user-guide/oauth-custom#invoke-snowflake-oauth-endpoints)).

### Customer-specific OAuth client

The connector collects each customer's OAuth registration when a connection is
created. `token:ClientId` is a string, `token:ClientSecret` is a secure string,
and `token:Scope` is a string. OAuth templates consume these values as
`{ClientId}`, `{ClientSecret}`, and `{Scope}`. Microsoft's certified Cognite
Data Fusion connector demonstrates this bring-your-own-client pattern
([Cognite source](https://github.com/microsoft/PowerPlatformConnectors/blob/dev/certified-connectors/Cognite%20Data%20Fusion/apiProperties.json)).

The authorization template includes `{RedirectUrl}`, `{State}`, and the
customer's scope. Separate token and refresh bodies use `{Code}` and
`{RefreshToken}` respectively. Microsoft's certified Talkdesk connector
demonstrates these platform placeholders and body templates
([Talkdesk source](https://github.com/microsoft/PowerPlatformConnectors/blob/dev/certified-connectors/Talkdesk/apiProperties.json)).

Snowflake supports `client_secret_post`, so the connector sends the customer
client ID and secret in the form-encoded token and refresh bodies. Snowflake
also supports HTTP Basic authentication, but it is not required
([Snowflake client authentication](https://docs.snowflake.com/en/user-guide/oauth-custom#client-authentication)).
A typical scope is
`refresh_token session:role:MCP_ACCESS_ROLE`
([Snowflake OAuth scope](https://docs.snowflake.com/en/user-guide/oauth-custom#scope)).

The callback is not entered by each customer. `GlobalPerConnector` gives the
imported or published connector one Power Platform-generated callback, injected
as `{RedirectUrl}`. Every customer registers that callback in their own
Snowflake OAuth security integration. The publisher must document the actual
callback after connector import or publication.

The constituent connector policies and dynamic OAuth syntax are verified.
Microsoft's public sources do not explicitly confirm certification of an MCP
connector that combines `x-ms-agentic-protocol` with these policies. The
publisher should confirm this composition during pre-submission review.

## Authentication

Microsoft allows OAuth 2.0, API key, or Basic authentication and prefers OAuth.
OAuth certification requires a multitenant identity-provider application,
production OAuth settings, a client ID and secret supplied securely through
Partner Center, the Microsoft redirect URI, and credentials and instructions
that exercise every tool
([Microsoft authentication requirements](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification#authentication-support)).
Microsoft's certified connector repository also demonstrates customer-entered
OAuth client registrations, which this connector follows. The public
certification guidance does not explain how Partner Center's publisher-level
credential fields apply to this bring-your-own-client model. The publisher
should expect to supply certification test credentials while confirming that
production customers use their own `token:ClientId` and
`token:ClientSecret`.

Snowflake-managed MCP supports confidential custom-client OAuth and External
OAuth. Snowflake documents a Microsoft callback URL, restricted allowed roles,
and `OAUTH_USE_SECONDARY_ROLES = NONE` for its custom-client configuration
([Snowflake-managed MCP authentication](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp#set-up-oauth-authentication)).
Snowflake custom-client OAuth is account-scoped, so the publisher must confirm
with Microsoft whether it satisfies the multitenant requirement. External OAuth
backed by a multitenant Microsoft Entra application is a possible alternative,
but the cited documentation does not explicitly confirm certification
acceptance.

## Snowflake architecture and authorization

The managed endpoint has this shape:

```text
https://<account_url>/api/v2/databases/{database}/schemas/{schema}/mcp-servers/{name}
```

Snowflake supports `CORTEX_AGENT_RUN`, `CORTEX_ANALYST_MESSAGE`,
`CORTEX_SEARCH_SERVICE_QUERY`, `SYSTEM_EXECUTE_SQL`, and `GENERIC` function or
procedure tools. Snowflake recommends exposing one governed Cortex Agent when
possible. Direct SQL should use a separate MCP server and dedicated role, and
`SYSTEM_EXECUTE_SQL` should remain `read_only: true`
([Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp)).

The caller role needs `USAGE` on the warehouse, database, schema, and MCP server,
plus only the downstream object privileges needed by enabled tools. The role
must not be granted to `PUBLIC`.

## Metadata and public artifacts

The server must advertise MCP tools and implement `tools/list` and `tools/call`.
Each tool needs a unique machine name, precise description, and JSON Schema
`inputSchema`; `outputSchema` is recommended when useful. Names and descriptions
directly affect Copilot Studio tool selection
([MCP tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)).

Connector metadata requires a unique English title of at most 30 characters
that excludes "API", "Connector", and Power Platform product names; a 30-500
character English description; operation and parameter summaries of at most 80
characters; and publisher, service-owner, website, privacy, legal, and support
details
([connector submission requirements](https://learn.microsoft.com/en-us/connectors/custom-connectors/certification-submission)).

Public certified connector directories normally contain:

- `apiDefinition.swagger.json`
- `apiProperties.json`
- `icon.png`
- `README.md` or `readme.md`
- optionally `settings.json`

Microsoft's
[AffinityMCP connector](https://github.com/microsoft/PowerPlatformConnectors/tree/dev/certified-connectors/AffinityMCP)
is a first-party example of this MCP connector shape.

## Final Partner Center package

The final submission is not the public source archive built by this repository.
The publisher must create the connector in a Power Platform solution, run
Solution Checker, export that solution, export a separate test-flow solution,
create a Package Deployer package containing both solutions, add `intro.md`,
build the outer ZIP, run Microsoft's package validator, and provide the archive
through a SAS URL valid for at least 15 days
([prepare connector files](https://learn.microsoft.com/en-us/connectors/custom-connectors/certification-submission),
[ConnectorPackageValidator.ps1](https://github.com/microsoft/PowerPlatformConnectors/blob/dev/scripts/ConnectorPackageValidator.ps1)).

## Required testing

Before submission, test:

- `tools/list`, every intended `tools/call`, and JSON and streamed responses.
- Connection creation, consent, refresh, expiration, invalid scope, and invalid
  audience behavior.
- Allowed and denied Snowflake users, roles, objects, and operations.
- Rejection of write, DDL, and DCL operations by read-only SQL tools.
- Missing, malformed, oversized, boundary, and adversarial inputs.
- Empty, error, large, citation-bearing, and confidential outputs.
- Warehouse outages, throttling, timeouts, retries, and safe audit logging.

Microsoft performs automated schema and package checks and manually invokes
every submitted tool. Evaluation evidence is optional but can expedite review
([Microsoft certification process](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification#certification-process)).

## Open certification questions

1. Whether Snowflake account-scoped OAuth satisfies Microsoft's multitenant
   identity-provider requirement.
2. Whether Microsoft will certify the verified dynamic connector policies when
   combined with `x-ms-agentic-protocol` for customer-owned Snowflake accounts.
3. Whether the submitting organization has the required rights from Snowflake.
4. Which production MCP protocol revisions Microsoft and Snowflake jointly
   support at submission time.
5. Which dynamic tool changes require recertification.
6. Current Copilot Studio limits for Snowflake Cortex responses over 200 KB.
