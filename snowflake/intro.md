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
- A Microsoft Partner Center seller account with verified-publisher status.
- Legal authorization to publish an integration for the Snowflake service.
- Microsoft test credentials that can exercise every submitted tool.

## Setup and authentication

1. Create and test the Snowflake-managed MCP server.
2. Configure OAuth for a confidential client.
3. Restrict the OAuth integration to the connector role and disable secondary
   roles.
4. Grant `USAGE` only on the required warehouse, database, schema, MCP server,
   and downstream Snowflake objects.
5. Import the connector definition and create an OAuth connection.
6. Enter the Snowflake organization-account identifier, database, schema, and
   managed MCP server name when creating the connection.
7. Add the connector to a Copilot Studio agent and verify tool discovery.

OAuth tokens are passed directly from the Power Platform connection to the
Snowflake-managed MCP endpoint. Secrets must be supplied through Partner Center
and must not be committed with the connector source.

## Limitations

- The endpoint is specific to a Snowflake account, database, schema, and MCP
  server and is selected when each connection is created.
- The account input accepts an organization-account identifier, not a complete
  URL. The connector routes only to the `snowflakecomputing.com` domain.
- The connector requires Streamable HTTP; legacy standalone HTTP+SSE transport
  is unsupported.
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
