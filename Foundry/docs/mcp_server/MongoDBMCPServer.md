# MongoDB MCP Server

The MongoDB MCP Server provides MongoDB connectivity through the official [MongoDB Model Context Protocol Server][mcp-repo]. It enables AI agents to interact with MongoDB databases and MongoDB Atlas clusters in natural language, supporting various capabilities.

## Setup

### Configuration Files

Rename template files to remove `_template` suffix:

```
deploy_mcp_aci_template.yaml → deploy_mcp_aci.yaml
```

### Prerequisites

Before setting up the MongoDB MCP Server, ensure you have:

- **MongoDB Connection**: Either a MongoDB connection string OR Atlas API credentials
- **Atlas Service Account**: Required for Atlas tools (optional for database-only operations)


### Configuration Options

Reference the [official MongoDB MCP documentation][mcp-config] for detailed configuration options.

## Deploy

### Azure Container Instances

The server deploys as a containerized service on [Azure Container Instances][aci-overview].

#### Prerequisites

- Azure Subscription. Signup for a free [Trial][azure-trial]
- Resource Group
- [Azure Container Registry][acr-quickstart]
- Docker image built and pushed to registry
- MongoDB Atlas cluster or MongoDB instance
- MongoDB connection credentials

#### Deployment Configuration

Update `deploy_mcp_aci.yaml` with:

- Container registry details
- Environment Variables for Configuration.
- Resource allocation (CPU/Memory)
- Network configuration

#### Deploy Command

```bash
az container create --file ./mcp_server/mongodb/deploy_mcp_aci.yaml --resource-group <resource-group>
```

For detailed deployment options, see [ACI deployment documentation][aci-deploy].

#### Obtaining the MCP Server URL

After successful deployment, obtain the server URL:

**1. Get Container Instance Details**
```bash
az container show --resource-group <resource-group> --name <container-group-name> --query ipAddress.fqdn
```

**2. Construct MCP Server URL**
```
http://<fqdn>:9000/mcp
```

Where:
- `<fqdn>` is the fully qualified domain name from step 1
- Port `9000` is defined in the deployment configuration
- `/mcp` is the endpoint path for the MCP Server

## Available Tools

The MongoDB MCP Server provides comprehensive tools organized into categories. see [MCP Server Tools][mcp-server-tools]

## Configuration Options

### Environment Variables

Key configuration options (prefix with `MDB_MCP_`). see [MCP Server Options][mcp-server-options]

### Setup
See [Documentation][mcp-server-setup]

### Security Best Practices

- **Environment Variables**: Use environment variables for sensitive data instead of command-line arguments
- **Read-Only Mode**: Enable `--readOnly` flag for analysis-only access
- **Minimum Permissions**: Grant only the minimum required Atlas permissions
- **Index Checking**: Use `--indexCheck` to enforce query optimization
- **Connection Security**: Always use TLS/SSL for production connections
- **Networking**: Whitelist the Outbound IP of AI Foundry VNet into MongoDB Atlas

## References

- **[MongoDB MCP Server Documentation][mcp-docs]** - Official MongoDB MCP Server documentation
- **[MongoDB MCP Server GitHub][mcp-repo]** - Official MongoDB MCP Server repository
- **[Model Context Protocol][mcp-protocol]** - Official MCP specification

<!-- Reference Links -->
[mcp-docs]: https://www.mongodb.com/docs/mcp-server/
[mcp-repo]: https://github.com/mongodb-js/mongodb-mcp-server
[mcp-config]: https://github.com/mongodb-js/mongodb-mcp-server#configuration
[mcp-protocol]: https://modelcontextprotocol.io/
[mcp-server-options]:https://www.mongodb.com/docs/mcp-server/configuration/options/#std-label-mcp-server-configuration-options
[aci-overview]: https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview
[acr-quickstart]: https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal
[aci-deploy]: https://docs.microsoft.com/en-us/azure/container-instances/container-instances-deploy-yaml
[azure-trial]: https://azure.microsoft.com/en-us/free
[azure-cli]: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
[acr-push]: https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli
[mcp-server-tools]: https://www.mongodb.com/docs/mcp-server/tools/
[mcp-server-setup]: https://www.mongodb.com/docs/mcp-server/prerequisites/