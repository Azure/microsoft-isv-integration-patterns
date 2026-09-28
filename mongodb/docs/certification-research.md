# MongoDB Atlas MCP connector research

Research date: September 28, 2026.

## Fixed remote server metadata

Azure/MCP identifies the production MongoDB Atlas MCP endpoint as
`https://mcp.mongodb.com` with Streamable HTTP transport. The URL is the root
endpoint; the connector must not append `/mcp`
([Azure/MCP MongoDB server metadata](https://github.com/Azure/MCP/blob/main/partners/servers/mongodb-remote-mcp-server.json)).

The same first-party registry entry defines these fixed user-delegated OAuth
values:

| Setting | Value |
|---|---|
| Flow | OAuth 2.1 authorization code with PKCE |
| Authorization URL | `https://cloud.mongodb.com/oauth/authorize` |
| Token URL | `https://authorize.mongodb.com/tokens` |
| Refresh URL | `https://authorize.mongodb.com/tokens` |
| Declared scopes | None |

The registry does not publish a client ID, client secret, dynamic-registration
endpoint, audience, resource parameter, or client-authentication method. Those
values must not be inferred
([Azure/MCP MongoDB server metadata](https://github.com/Azure/MCP/blob/main/partners/servers/mongodb-remote-mcp-server.json)).

## User-delegated access

MongoDB documents that user-delegated access uses OAuth 2.1 Authorization Code
with PKCE and browser authentication. Requests act with the authorizing user's
Atlas permissions, Atlas manages token refresh, and the MCP client does not
receive the user's password or long-lived credentials
([MongoDB remote MCP security](https://www.mongodb.com/docs/mcp-server/remote-mcp/security/)).
Static API keys are not supported by the hosted remote HTTP endpoint
([Azure/MCP MongoDB server metadata](https://github.com/Azure/MCP/blob/main/partners/servers/mongodb-remote-mcp-server.json)).

MongoDB states that this access model is available to AI clients registered by
MongoDB. A production Copilot Studio connector therefore requires MongoDB
registration or approval before its client values and authentication method are
known
([MongoDB remote MCP access models](https://www.mongodb.com/docs/mcp-server/remote-mcp/access-models/#std-label-remote-mcp-access-models-user-delegated)).

The checked-in connector intentionally keeps `clientId` and `clientSecret`
empty. The authorized publisher must obtain the production registration values,
confirm whether MongoDB requires client-secret authentication in addition to
PKCE, and inject any secret only through the secure connector or Partner Center
workflow. PKCE by itself does not establish whether a client is public or
confidential.

Microsoft requires an OAuth MCP publisher to register a multitenant
identity-provider application and provide production OAuth configuration, test
credentials, and test instructions during certification
([Microsoft MCP server certification](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-server-certification#authentication-support)).
The publisher must also verify that the target Power Platform OAuth
implementation emits the PKCE parameters required by MongoDB.

## Do not mix programmatic credentials

MongoDB also provides a separate programmatic-access model. Credentials from an
Atlas MCP configuration are not the client values for the user-delegated
authorization-code flow. The programmatic wrapper uses client credentials,
HTTP Basic client authentication, `grant_type=client_credentials`, and the
different token endpoint `https://cloud.mongodb.com/api/oauth/token`
([MongoDB Atlas MCP remote wrapper](https://github.com/mongodb-js/mongodb-mcp-server/tree/main/packages/mongodb-atlas-mcp-remote),
[wrapper token configuration](https://github.com/mongodb-js/mongodb-mcp-server/blob/main/packages/mongodb-atlas-mcp-remote/src/config.ts),
[wrapper token manager](https://github.com/mongodb-js/mongodb-mcp-server/blob/main/packages/mongodb-atlas-mcp-remote/src/tokenManager.ts)).

## Connector implications

- Use fixed host `mcp.mongodb.com`, HTTPS, root path `/`, and
  `x-ms-agentic-protocol: mcp-streamable-1.0`.
- Use the registry authorization, token, and refresh URLs verbatim.
- Do not invent scopes, audience values, or resource parameters.
- Keep the checked-in client ID and secret empty.
- Register the connector redirect URL and securely add MongoDB-issued
  production client values before publishing.
- Validate PKCE and the exact client-authentication method with MongoDB and in
  the target Power Platform environment.
