# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Copy the MCP Tools Config
COPY ./mcp_server/snowflake/tools_config.yaml /app

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER nonroot

# Running the MCP Server
CMD ["uvx", "snowflake-labs-mcp", "--service-config-file", "./tools_config.yaml", "--transport", "streamable-http", "--endpoint", "/snowflake-mcp"]