# Security guidance

## Before deployment

- Approve each MCP endpoint owner, hostname, transport security configuration,
  data residency, logging policy, and tool inventory.
- Require HTTPS and use publicly trusted certificates.
- Configure provider identities with the minimum Snowflake roles, Databricks
  permissions, catalogs, schemas, warehouses, and workspaces needed.
- Prefer separate development, test, and production endpoints and identities.
- Review tools that execute SQL, mutate objects, manage permissions, start
  jobs, export data, or invoke models.
- Restrict the initial Microsoft 365 assignment to a pilot group.

## Secrets

Never place these values in the JSON configuration, manifest, skill, ZIP, git
history, issue, or chat:

- passwords;
- OAuth client secrets;
- access or refresh tokens;
- personal access tokens;
- private keys;
- Snowflake key-pair material;
- Databricks service-principal secrets.

An `OAuthPluginVault` `referenceId` identifies a tenant-managed connection. It
is not a substitute for the underlying secret store and should still be
treated as tenant configuration.

## Runtime controls

- Keep read-only discovery separate from mutating tools.
- Require user confirmation before writes, DDL, permission changes, job runs,
  or production actions.
- Enforce row, column, masking, catalog, and schema policies at the provider.
- Limit response size and avoid returning sensitive rows when aggregate or
  metadata results satisfy the request.
- Correlate Microsoft 365, MCP gateway, Snowflake, and Databricks audit logs.
- Alert on denied actions, unusual query volume, bulk export, and repeated
  cross-environment access attempts.

## Lifecycle

- Review the generated manifest before every tenant upload.
- Keep the app ID stable and increment the version for controlled updates.
- Revoke provider access and OAuth connections when removing the app.
- Revalidate endpoint tools and permissions after MCP server upgrades.
- Update Scout plugin commit SHAs explicitly and review upstream changes before
  rollout. Marketplace sources are pinned to immutable commits.

## Incident response

If compromise is suspected, unassign the app, disable the affected connector
or MCP endpoint, revoke its vault connection and provider identity, preserve
audit logs, rotate underlying credentials, and reapprove the integration before
restoring access.
