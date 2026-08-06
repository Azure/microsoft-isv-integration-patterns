# Troubleshooting

## Build failures

### Configuration not found

Copy `plugin.config.template.json` to the gitignored `plugin.config.json`, or
run `.\build.ps1 -Interactive`.

### App ID is invalid

Use a non-empty GUID. The all-zero value in the template is deliberately
rejected.

### URL must be HTTPS

Use an absolute `https://` publisher or MCP URL. The builder rejects HTTP,
relative URLs, and malformed URLs.

### Icon not found or not a PNG

Icon paths are resolved relative to the configuration file. Supply both PNG
files and confirm their Microsoft 365-required dimensions and transparency.
The builder verifies file existence and extension; the tenant upload performs
additional image validation.

### Enable at least one connector

Set `connectors.snowflake.enabled` or `connectors.databricks.enabled` to `true`.

### OAuth reference validation failed

When `authorization` is present, its type must be `OAuthPluginVault` and
`referenceId` must be non-empty. Remove the entire authorization object only
for an endpoint intentionally configured without manifest-level OAuth.

## Tenant upload failures

- Confirm `manifest.json`, both icons, and `skills/` are at the ZIP root.
- Validate the generated manifest against the schema URL declared in it.
- Confirm the app ID and version meet tenant lifecycle expectations.
- Check whether custom app upload and the manifest features are allowed by
  tenant policy.
- Confirm the administrator has permission to manage integrated apps and
  connector connections.

## Connector is missing in Cowork

- Confirm the installed package version contains the expected connector.
- Confirm the app is assigned to the current user and deployment has
  propagated.
- Check tenant policy, admin approval, and the OAuth vault connection.
- Verify the remote MCP hostname appears in generated `validDomains`.

## MCP tool discovery or calls fail

- Open the MCP URL from an approved network path and verify its certificate.
- Check server health and protocol compatibility.
- Verify the OAuth connection is active and mapped to the correct endpoint.
- Confirm provider identity permissions and environment targeting.
- Review Microsoft 365, MCP server, Snowflake, or Databricks audit logs using a
  shared timestamp or correlation ID.

Do not work around an authorization denial by broadening provider roles without
review.

## Scout installer fails

- Install or update Microsoft Scout Desktop and confirm its bundled
  `copilot.exe` exists.
- If the marketplace name is already registered from a different GitHub
  repository or local directory, remove or explicitly migrate that marketplace
  before rerunning the installer. The installer refuses to trust a
  same-named source.
- Confirm GitHub access is available.
- For Snowflake, verify the required Snowflake tooling and connection.
- For Databricks, run `databricks version` and verify CLI authentication.
- Rerun the provider `install.ps1`; it updates an existing marketplace and
  plugin.
- Restart Scout after successful installation so its Skills UI refreshes.
