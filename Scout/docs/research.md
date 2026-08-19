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

Keep the Snowflake and Databricks `sha` fields. They enforce the reviewed-commit
policy documented in the provider READMEs and prevent unreviewed upstream
changes from entering an installation automatically.

MongoDB currently uses `"ref": "main"` instead, so its installs follow the
latest commit on that branch. Consider pinning MongoDB to a reviewed SHA if the
same reproducibility policy should apply to every provider.
