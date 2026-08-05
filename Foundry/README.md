# AI Foundry ISV MCP Agent

This project provides an integrated solution for connecting Azure AI Foundry agents with ISV Partner services through the Model Context Protocol (MCP). It enables AI agents to interact with the specific ISV tools through a standardized protocol interface.

## Azure AI Foundry

[Azure AI Foundry][ai-foundry] is Microsoft's comprehensive platform for building, deploying, and managing AI applications. It provides enterprise-grade tools for AI development, including agent frameworks, model deployments, and integrated development environments. This project leverages AI Foundry's agent capabilities to create intelligent interfaces for third party ISV Services.

## Documentation

- **[Setup][setup-docs]** - Project installation and environment setup
- **[MCP Server][mcp-server-docs]** - MCP server deployment and configuration
- **[AI Foundry Agent][ai-foundry-docs]** - Agent configuration and usage
- **[MCP Client][mcp-client-docs]** - CLI and web interface usage

## References

- **[Azure AI Foundry Agents Samples][ai-foundry-agents-samples]** - Microsoft repository for AI Foundry agent samples and tools
- **[Azure AI Projects SDK][ai-projects-sdk-github]** - Python SDK for Azure AI Foundry projects and agents
- **[AI Foundry Training][ai-foundry-training]** - Microsoft Training for AI Foundry
- **[Model Context Protocol][mcp-spec]** - Official MCP specification and documentation


<!-- Reference Links -->
[ai-foundry]: https://learn.microsoft.com/en-us/azure/ai-foundry/
[setup-docs]: docs/Setup.md
[mcp-server-docs]: docs/mcp_server/MCPServer.md
[ai-foundry-docs]: docs/AIFoundryAgent.md
[mcp-client-docs]: docs/MCPClient.md
[ai-foundry-agents-samples]: https://github.com/Azure-Samples/ai-foundry-agents-samples
[ai-projects-sdk-github]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects
[mcp-spec]: https://modelcontextprotocol.io/
[ai-foundry-training]: https://learn.microsoft.com/en-us/training/azure/ai-foundry
