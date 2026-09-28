# MongoDB Atlas MCP

## Business purpose

MongoDB Atlas MCP enables Microsoft Copilot Studio agents to discover and invoke
tools hosted by MongoDB's Atlas-managed remote MCP server. Agents can work with
MongoDB data, search capabilities, and Atlas resources within the permissions
of the user who completes OAuth authorization.

## Supported tools

Tools are discovered dynamically with MCP `tools/list` and invoked with
`tools/call`. The exact tools available can vary as MongoDB evolves the hosted
service and according to the authorizing user's Atlas permissions. MongoDB
documents database operations, Atlas administration, search and vector search,
and Atlas Stream Processing capabilities.

For certification, list every enabled production tool here, including its
purpose, inputs, expected outputs, write or delete effects, permissions, and
test steps.

## Prerequisites

- Access to the MongoDB Atlas-hosted MCP server.
- A least-privileged MongoDB Atlas user for each intended permission profile.
- A MongoDB OAuth client configured for the connector redirect URL.
- A Microsoft Partner Center seller account with verified-publisher status.
- Legal authorization to publish an integration for the MongoDB service.
- Microsoft test credentials that can exercise every submitted tool.

## Setup and authentication

1. Import the connector definition and obtain its redirect URL.
2. Register that redirect URL on the production MongoDB OAuth client.
3. Populate the connector's empty `clientId` and `clientSecret` fields through
   the secure publishing workflow.
4. Verify authorization-code flow with PKCE against the fixed MongoDB
   authorization and token endpoints.
5. Create the OAuth connection with a least-privileged Atlas user.
6. Add the connector to a Copilot Studio agent and verify tool discovery.
7. Test both allowed and denied operations before publishing.

OAuth tokens are sent directly from the Power Platform connection to
`https://mcp.mongodb.com`. The hosted endpoint acts with the authorizing user's
Atlas permissions. Static API keys are not supported by this remote endpoint.
Never commit the populated OAuth client secret. Do not substitute credentials
from MongoDB's separate programmatic-access model, which uses a different OAuth
flow and token endpoint.

## Limitations

- The connector targets only MongoDB's fixed `https://mcp.mongodb.com` endpoint.
- The remote service requires OAuth 2.1 authorization code flow with PKCE.
- Tool availability and results depend on the connected user's Atlas permissions.
- Static API keys are unsupported on the hosted remote HTTP endpoint.
- Database writes, deletes, index changes, and Atlas administration can be
  destructive and must be governed with least privilege.
- Changes to production tools can require connector recertification.
- Atlas services and running stream processors can incur MongoDB charges.
- Large results must be tested against current Copilot Studio and connector
  response limits.

## Privacy and compliance

Requests and responses are processed by Microsoft Power Platform and MongoDB
under their respective customer agreements. Publishers must provide production
privacy terms, data-handling disclosures, responsible AI evidence, legal terms,
and support processes before submission.

## Support

This repository is a reference implementation. Report implementation issues at
https://github.com/Azure/microsoft-isv-integration-patterns/issues.

For MongoDB product support, use https://www.mongodb.com/company/contact.
Production publishers must provide staffed support, service, privacy, and legal
URLs in the final submission.
