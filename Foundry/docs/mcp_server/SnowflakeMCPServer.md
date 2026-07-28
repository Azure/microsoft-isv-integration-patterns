# Snowflake MCP Server

The MCP Server provides Snowflake connectivity through the Snowflake's [Model Context Protocol][mcp-repo] Server. It enables AI agents to interact with Snowflake services including Cortex Agent, Cortex Search, and Cortex Analyst and other available tools.

## Setup

### Configuration Files

Rename template files to remove `_template` suffix:

```
tools_config_template.yaml → tools_config.yaml
deploy_mcp_aci_template.yaml → deploy_mcp_aci.yaml
```

### Tools Configuration

Configure `tools_config.yaml` with your Snowflake services:

- **agent_services**: Cortex Agent services
- **search_services**: Cortex Search services  
- **analyst_services**: Cortex Analyst semantic models
- **other_services**: Enable object/query/semantic managers
- **sql_statement_permissions**: SQL operation permissions

Reference the [Snowflake MCP documentation][mcp-config] for detailed configuration options and latest configuration file.

## Deploy

### Azure Container Instances

The server deploys as a containerized service on [Azure Container Instances][aci-overview].

#### Prerequisites

- Azure Subscription. Signup for a free [Trial][azure-trial]
- Resource Group
- [Azure Container Registry][acr-quickstart]
- Docker image built and pushed to registry

#### Build and Push Docker Image

Ensure [Docker Desktop][docker-desktop] is installed and [Azure CLI][azure-cli] is configured.

**1. Login to Azure Container Registry**
```bash
az acr login --name <registry>
```

**2. Build Docker Image**
```bash
docker build -f .\mcp_server\snowflake\Dockerfile -t mcp-server-snowflake:v1 .
```

**3. Tag Image for Registry**
```bash
docker tag mcp-server-snowflake:v1 <registry>.azurecr.io/mcp-server-snowflake:v1
```

**4. Push to Registry**
```bash
docker push <registry>.azurecr.io/mcp-server-snowflake:v1
```

See [ACR push documentation][acr-push] for troubleshooting and advanced options.

#### Deployment Configuration

Update `deploy_mcp_aci.yaml` with:

- Container registry details
- Snowflake connection parameters
- Resource allocation (CPU/Memory)
- Network configuration

#### Deploy Command

```bash
az container create --file ./mcp_server/snowflake/deploy_mcp_aci.yaml --resource-group <resource-group>
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
http://<fqdn>:9000/snowflake-mcp
```

Where:
- `<fqdn>` is the fully qualified domain name from step 1
- Port `9000` is defined in the deployment configuration
- `/snowflake-mcp` is the endpoint path from `SNOWFLAKE_MCP_ENDPOINT` environment variable

**3. Verify Server Status**
```bash
curl http://<fqdn>:9000/snowflake-mcp/health
```

Use this URL as the `MCP_Server_URL` in your AI Foundry agent configuration.

## References

- **[Snowflake Cortex Agents][sf-cortex-agents]** - Snowflake Documentation for Cortex Agents
- **[Snowflake Cortex Analyst][sf-cortex-analyst]** - Snowflake Documentation for Cortex Analyst
- **[Snowflake Cortex Search][sf-cortex-search]** - Snowflake Documentation for Cortex Search

<!-- Reference Links -->
[mcp-repo]: https://github.com/Snowflake-Labs/mcp
[mcp-config]: https://github.com/Snowflake-Labs/mcp#configuration
[aci-overview]: https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview
[acr-quickstart]: https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal
[aci-deploy]: https://docs.microsoft.com/en-us/azure/container-instances/container-instances-deploy-yaml
[azure-trial]: https://azure.microsoft.com/en-us/free
[docker-desktop]: https://docs.docker.com/desktop/
[azure-cli]: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
[acr-push]: https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli
[sf-cortex-agents]:https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents
[sf-cortex-search]:https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview
[sf-cortex-analyst]:https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst