---
name: install-scout-data-platform-plugins
description: Install or update the official Snowflake, Databricks, and MongoDB Copilot plugins in Microsoft Scout Desktop. Use when a user asks to add these provider skills to Scout.
---

# Install Scout Data Platform Plugins

Present exactly these four options without requesting free-form input:

1. Snowflake
2. Databricks
3. MongoDB
4. All

After the user selects one option, proceed without asking for more installation
input. Verify Microsoft Scout Desktop is installed and review the selected
provider prerequisites in its README.

Run the installer from the repository root with the selected option:

```powershell
.\Scout\install.ps1 -Platform <Snowflake|Databricks|MongoDB|All>
```

The scripts use Scout's bundled Copilot CLI, register or update this
repository's marketplace, install or update the provider-maintained plugin, and
create skill junctions under `~/.scout/m-skills`.

Do not request or write provider credentials. Authentication belongs to the
provider CLI or connection tooling documented by Snowflake, Databricks, or
MongoDB.
Surface installer errors directly. On success, ask the user to restart Scout
and verify the installed plugin and skills before reporting completion.
