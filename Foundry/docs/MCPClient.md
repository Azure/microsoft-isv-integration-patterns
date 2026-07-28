# MCP Client

The MCP Client provides interface options to interact with AI Foundry agents through the [AI Foundry Agent)][foundry-agent]. It offers both command-line and web-based interfaces for testing and using AI Foundry agents with Snowflake MCP integration.

The client supports:
- **Continuous Conversations**: Thread persistence across multiple messages
- **Agent Configuration**: Dynamic agent selection and configuration
- **Real-time Interaction**: Immediate responses from AI Foundry agents
- **Session Management**: Thread ID tracking and conversation history

## Setup

### Prerequisites

- [AI Foundry Agent configured][ai-foundry-agent-setup] and accessible
- [MCP Server deployed][mcp-server-setup] and running

### Client Options

#### CLI Interface
Interactive command-line chat interface with:
- Continuous conversation support
- Thread persistence
- Agent metadata display
- Command history

#### Streamlit Interface  
Web-based chat interface featuring:
- User-friendly web UI
- Real-time conversation display
- Agent configuration input
- Session state management
- Conversation history visualization

## Running

### CLI Version

Execute the command-line interface:

```bash
uv run ai-foundry-chat-cli --agent_name <agent_name>
```

**Options:**
- `--agent_name`: Specify the agent configuration name from `agent_config.yaml`

**Example:**
```bash
uv run ai-foundry-chat-cli --agent_name snowflake-cortex-mcp
```

### Streamlit Version

Launch the web interface:

```bash
uv run python -m streamlit run "mcp_client\streamlit\app.py"
```

The web interface will be available at `http://localhost:8501` with:
- Agent name configuration
- Interactive chat interface
- Real-time metadata display
- Conversation management

<!-- Reference Links -->
[foundry-agent]: ../ai_foundry_agent/
[ai-foundry-agent-setup]: ./AIFoundry.md
[mcp-server-setup]: ./MCPServer.md