---
name: install-scout-data-platform-plugins
description: Install or update the official Snowflake and Databricks Copilot plugins in Microsoft Scout Desktop. Use when a user asks to add Snowflake or Databricks skills to Scout.
---

# Install Scout Data Platform Plugins

Ask which provider to install: Snowflake, Databricks, or both. Then verify
Microsoft Scout Desktop is installed and review the provider prerequisites in
its README.

Run the matching installer from the repository root:

```powershell
.\Scout\snowflake\install.ps1
.\Scout\databricks\install.ps1
```

The scripts use Scout's bundled Copilot CLI, register or update this
repository's marketplace, install or update the provider-maintained plugin, and
create skill junctions under `~/.scout/m-skills`.

Do not request or write provider credentials. Authentication belongs to the
provider CLI or connection tooling documented by Snowflake or Databricks.
Surface installer errors directly. On success, ask the user to restart Scout
and verify the installed plugin and skills before reporting completion.
