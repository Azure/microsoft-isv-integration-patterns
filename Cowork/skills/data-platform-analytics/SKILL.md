---
name: data-platform-analytics
description: Use approved Snowflake and Databricks MCP tools for data discovery, SQL analysis, lineage, governance, and data engineering work. Trigger when the user asks to inspect or analyze data in Snowflake or Databricks, compare results across the platforms, or perform a governed data-platform action.
---

# Data Platform Analytics

Use the configured Snowflake and Databricks MCP connectors without exposing
credentials or bypassing provider governance.

## Workflow

1. Determine which platform the user intends to use. If it is ambiguous, ask
   one focused question with Snowflake and Databricks as choices.
2. Confirm the workspace, catalog, database, schema, or warehouse when the
   requested action could target more than one environment.
3. Prefer metadata and read-only tools before query or mutation tools.
4. Before any write, DDL, permission, job-run, or production action, summarize
   the exact target and request confirmation.
5. Call only tools exposed by the selected connector. Never invent a tool name
   or claim success without its returned result.
6. Present the platform, target, query or action, and material limitations in
   the result. Keep sensitive row data to the minimum required by the request.

## Cross-platform requests

Run independent read-only discovery calls in parallel when possible. Normalize
units, time zones, null handling, and identifier casing before comparing
results. Do not move data between platforms unless the user explicitly requests
it and an approved connector tool supports the transfer.

## Failure handling

Surface authentication, authorization, policy, and endpoint errors directly.
Do not retry a denied action with broader scope. If a tool is unavailable,
identify the missing Snowflake or Databricks connector and point the user to
the plugin administrator.
