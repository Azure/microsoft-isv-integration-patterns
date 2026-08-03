"""
Wrapper module for AI Foundry Agent with MCP Integration.

This package exposes the necessary methods to interact with Azure AI Foundry agents
through the Model Context Protocol (MCP).
"""

import os
import time

import yaml
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential

# Global variables to store configuration
config = None
agent_name = None
agent_description = None
mcp_server_url = None
mcp_server_label = None
allowed_tools = None
agent_instructions = None
approval_mode = None
logging_enabled = None
log_path = None
delete_agent_after_run = None
ignore_existing_agent = None
model_deployment_name = None
project_endpoint = None
auth_token = None
logging_initialized = False

def _load_config(input_agent_name):
    """Load configuration from YAML file and environment variables"""
    global config, agent_name, agent_description, mcp_server_url, mcp_server_label, allowed_tools
    global agent_instructions, approval_mode, logging_enabled, log_path
    global delete_agent_after_run, ignore_existing_agent, model_deployment_name, project_endpoint
    global auth_token, logging_initialized
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load environment variables from ai_foundry.env file in the script directory
    load_dotenv(os.path.join(script_dir, 'ai_foundry.env'))

    # Get AI Foundry Configuration from environment variables
    model_deployment_name = os.getenv("FOUNDRY_MODEL_NAME") or os.getenv("MODEL_DEPLOYMENT_NAME")
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("PROJECT_ENDPOINT")

    # Load agent configuration from YAML file
    try:
        # Look for agent_config.yaml in the same directory as this script
        config_file_path = os.path.join(script_dir, 'agent_config.yaml')
        with open(config_file_path, 'r') as config_file:
            agent_config = yaml.safe_load(config_file)
    except FileNotFoundError:
        print(f"Error: agent_config.yaml file not found at {config_file_path}")
        print("Please ensure agent_config.yaml exists in the same directory as agent.py")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        exit(1)

    # Get the specified agent configuration
    agent_name = input_agent_name
    if agent_name not in agent_config:
        available_agents = list(agent_config.keys())
        print(f"Error: Agent '{agent_name}' not found in configuration.")
        print(f"Available agents: {available_agents}")
        exit(1)
    config = agent_config[agent_name]

    # Get Agent Configuration from agent_config.yaml
    mcp_server_url = config.get("MCP_Server_URL")
    mcp_server_label = config.get("MCP_Server_Label")
    allowed_tools = config.get("Allowed_Tools", [])
    agent_description = config.get("Agent_Description", "")
    agent_instructions = config.get("Agent_Instruction")
    approval_mode = config.get("Approval_Mode", "never")
    logging_enabled = config.get("Logging", True)
    log_path = config.get("Log_Path", "logs/agent_logs.txt")
    delete_agent_after_run = config.get("Delete_Agent_After_Run", False)
    ignore_existing_agent = config.get("Ignore_Existing_Agent", False)
    auth_token = config.get("Auth_Token", "")
    logging_initialized = False  # Reset logging flag for new config

def _log_message(message):
    """Setup logging function"""
    global logging_initialized
    if logging_enabled:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as log_file:
            # Only write the "Starting Logging" message once
            if not logging_initialized:
                log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Starting Logging for Agent {agent_name}\n")
                logging_initialized = True
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    else:
        print(message)

def _project_init():
    """Initialize AI Project Client and MCP Tool"""
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    approval_aliases = {"on_request": "always", "prompt": "always"}
    require_approval = approval_aliases.get(approval_mode, approval_mode)
    if require_approval not in {"always", "never"}:
        raise ValueError("Approval_Mode must be one of: always, never, prompt, on_request")

    mcp_tool_options = {
        "server_label": mcp_server_label,
        "server_url": mcp_server_url,
        "require_approval": require_approval,
    }
    if allowed_tools:
        mcp_tool_options["allowed_tools"] = allowed_tools
    if auth_token:
        mcp_tool_options["headers"] = {"Authorization": f"Bearer {auth_token}"}

    mcp_tool = MCPTool(
        **mcp_tool_options,
    )
    _log_message(f"Initialized MCP Tool {mcp_tool}")

    return project_client, mcp_tool

def _agent_init(project_client, mcp_tool):
    """Check for existing agent and create agent if needed"""
    existing_agent = None

    if not ignore_existing_agent:
        try:
            for agent_item in project_client.agents.list():
                if agent_item.name == agent_name:
                    existing_agent = agent_item
                    break
        except Exception as e:
            _log_message(f"Error listing agents: {e}")
            existing_agent = None
    else:
        _log_message("Ignoring existing agents - will create new agent")
    
    # Use existing agent if found and not ignoring existing agents
    if existing_agent and not ignore_existing_agent:
        agent = existing_agent
        _log_message(f"Using existing agent, Name: {agent_name} ID: {agent.id}")
    else:
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            description=agent_description,
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=agent_instructions,
                tools=[mcp_tool],
            ),
        )
        _log_message(
            f"Created new agent, Name: {agent_name} ID: {agent.id} Version: {agent.version}"
        )
    _log_message(f"MCP Server: {mcp_server_label} at {mcp_server_url}")

    return agent

def _agent_run(openai_client, agent, user_message, agent_name, thread_id=None):
    """Create a conversation, invoke the agent, and return conversation results."""
    if thread_id:
        conversation = openai_client.conversations.retrieve(thread_id)
        _log_message(f"Using existing conversation, ID: {conversation.id}")
    else:
        conversation = openai_client.conversations.create()
        _log_message(f"Created conversation, ID: {conversation.id}")

    agent_reference = {"name": agent.name, "type": "agent_reference"}
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=user_message,
        extra_body={"agent_reference": agent_reference},
    )

    while True:
        approval_requests = [
            item for item in response.output if item.type == "mcp_approval_request" and item.id
        ]
        if not approval_requests:
            break

        approvals = []
        for request in approval_requests:
            _log_message(
                f"Approving MCP tool call {request.id}: "
                f"{getattr(request, 'name', '<unknown>')} "
                f"{getattr(request, 'arguments', '')}"
            )
            approvals.append(
                {
                    "type": "mcp_approval_response",
                    "approval_request_id": request.id,
                    "approve": True,
                }
            )

        response = openai_client.responses.create(
            input=approvals,
            previous_response_id=response.id,
            extra_body={"agent_reference": agent_reference},
        )

    _log_message(f"Response completed with status: {response.status}")
    messages = openai_client.conversations.items.list(conversation.id, order="asc")
    _log_message("Conversation:")
    _log_message("-" * 50)

    conversation_results = []
    for msg in messages:
        if msg.type != "message":
            continue
        content = "".join(
            part.text for part in msg.content if part.type in {"input_text", "output_text"}
        )
        if content:
            conversation_results.append({"role": msg.role.upper(), "content": content})

    _log_message(f"response: {conversation_results}")

    return {
        "agent_name": agent_name,
        "agent_id": agent.id,
        "thread_id": conversation.id,
        "message_id": response.id,
        "response": conversation_results
    }

def _agent_delete(project_client, openai_client, agent, thread_id):
    """Delete the agent"""
    try:
        openai_client.conversations.delete(thread_id)
        _log_message(f"Deleted conversation ID: {thread_id}")
        project_client.agents.delete(agent.name, force=True)
        _log_message(f"Deleted agent ID: {agent.id}")
        return True
    except Exception as e:
        _log_message(f"Error deleting thread {thread_id} agent {agent.id}: {e}")
        return False

def _run_agent_with_message(agent_name, user_message, thread_id=None):
    """Main function to run the complete agent workflow with a custom message"""
    # Load configuration
    _load_config(agent_name)
    
    # Initialize project and MCP tool
    project_client, mcp_tool = _project_init()
    
    with project_client, project_client.get_openai_client() as openai_client:
        # Initialize or get existing agent
        agent = _agent_init(project_client, mcp_tool)

        # Run the agent with the user message
        conversation_results = _agent_run(
            openai_client, agent, user_message, agent_name, thread_id
        )

        # Delete the agent after run if set to True
        if delete_agent_after_run:
            _agent_delete(
                project_client,
                openai_client,
                agent,
                conversation_results.get("thread_id"),
            )

        return conversation_results

def invoke_agent(agent_name, user_message, thread_id=None) -> dict:
    """
    Public method to invoke the agent with the specified agent name and user message.
    
    Args:
        agent_name (str): The name of the agent configuration to use
        user_message (str): The message to send to the agent
        
    Returns:
        JSON Response
    """
    results = _run_agent_with_message(agent_name, user_message, thread_id)
    return results

def _main():
    """Private main function for standalone script execution"""
    # values for standalone execution
    agent_name = "snowflake-cortex-mcp"
    user_message = "Tell me about the call with Securebank?"
    
    results = invoke_agent(agent_name, user_message)
    print(results)

if __name__ == "__main__":
    _main()