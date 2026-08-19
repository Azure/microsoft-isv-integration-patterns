# Scout marketplace research

Research was performed on 2026-08-19 against the official GitHub Copilot CLI
plugin reference.

## `sha` in `marketplace.json`

For a `github` plugin source, `sha` is an optional full 40-character Git commit
SHA. It pins installation to an exact upstream commit, making installs
reproducible and unaffected by branch, tag, or default-branch movement.

The field is not required. If both `sha` and `ref` are omitted, the Copilot CLI
uses the repository's default branch. If only `ref` is present, it resolves that
branch or tag when the plugin is installed or updated.

Primary sources:

- [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference#marketplacejson)
- [GitHub's first-party Copilot plugin marketplace](https://github.com/github/copilot-plugins/blob/main/.github/plugin/marketplace.json)

## Repository decision

The repository intentionally uses `"ref": "main"` for Snowflake, Databricks,
and MongoDB. This makes Scout installs and updates follow the latest commit
published by each partner. The accepted tradeoff is that installs are not
reproducible and upstream changes can take effect without a marketplace
manifest change.
