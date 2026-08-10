---
name: data-platform-analytics
description: Use approved Snowflake, Databricks, and MongoDB MCP tools for data discovery, analysis, lineage, governance, and data engineering work. Trigger when the user asks to inspect or analyze data in one of these platforms, compare results across them, or perform a governed data-platform action.
---

# Data Platform Analytics

Use the configured Snowflake, Databricks, and MongoDB MCP connectors without exposing
credentials or bypassing provider governance.

## Workflow

1. Determine which platform the user intends to use. If it is ambiguous, ask
   one focused question with the configured providers as choices.
2. When more than one connector exists for that provider, ask the user to
   choose the connector by its display name. Never infer production when the
   environment is ambiguous.
3. Confirm the account, workspace, cluster, project, catalog, database,
   collection, schema, or warehouse when the requested action could target
   more than one environment.
4. Prefer metadata and read-only tools before query or mutation tools.
5. Before any write, DDL, permission, job-run, or production action, summarize
   the exact target and request confirmation.
6. Call only tools exposed by the selected connector. Never invent a tool name
   or claim success without its returned result.
7. Present the platform, connector, target, query or action, and material limitations in
   the result. Keep sensitive row data to the minimum required by the request.

## Cross-platform requests

Run independent read-only discovery calls in parallel when possible. Normalize
units, time zones, null handling, and identifier casing before comparing
results. Do not move data between platforms unless the user explicitly requests
it and an approved connector tool supports the transfer.

## Failure handling

Surface authentication, authorization, policy, and endpoint errors directly.
Do not retry a denied action with broader scope. If a tool is unavailable,
identify the missing Snowflake, Databricks, or MongoDB connector and point the user to
the plugin administrator.
