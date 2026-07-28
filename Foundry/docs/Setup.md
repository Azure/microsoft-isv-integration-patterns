# Setup

This project provides an AI Foundry Agent integrated with Snowflake services through Model Context Protocol (MCP). The setup process is streamlined using [uv][uv-docs] for dependency management and Python environment handling.

The project includes:
- **AI Foundry Agent**: Azure AI agent with MCP integration
- **MCP Server**: Snowflake connectivity server
- **MCP Client**: CLI and web interfaces for testing

## Prerequisites

### System Requirements

- **Python**: Version 3.12 (managed automatically by uv)
- **uv**: Python package manager and environment tool

### Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See [uv installation guide][uv-install] for additional options.

## Project Setup

### 1. Install Dependencies

```bash
uv sync
```

This automatically:
- Creates Python 3.12 virtual environment
- Installs all project dependencies
- Sets up development environment

### 2. Verify Installation

```bash
uv run --help
```

## Next Steps

After setup completion:

1. **Configure MCP Server**: See [MCP Server Setup][mcp-server-docs]
2. **Configure AI Foundry Agent**: See [AI Foundry Setup][ai-foundry-docs] 
3. **Test with MCP Client**: See [MCP Client Usage][mcp-client-docs]

<!-- Reference Links -->
[uv-docs]: https://docs.astral.sh/uv/
[uv-install]: https://docs.astral.sh/uv/getting-started/installation/
[mcp-server-docs]: ./MCPServer.md
[ai-foundry-docs]: ./AIFoundry.md
[mcp-client-docs]: ./MCPClient.md