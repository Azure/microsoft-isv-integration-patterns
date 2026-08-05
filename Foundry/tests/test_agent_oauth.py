from importlib.util import find_spec
import sys
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch


try:
    from azure.ai.projects.models import MCPTool  # noqa: F401
except (ImportError, ModuleNotFoundError):
    azure = ModuleType("azure")
    azure.__path__ = []
    azure_ai = ModuleType("azure.ai")
    azure_ai.__path__ = []
    azure_projects = ModuleType("azure.ai.projects")
    azure_projects.__path__ = []
    azure_projects.AIProjectClient = MagicMock()
    azure_models = ModuleType("azure.ai.projects.models")
    azure_models.MCPTool = MagicMock()
    azure_models.PromptAgentDefinition = MagicMock()
    azure_identity = ModuleType("azure.identity")
    azure_identity.DefaultAzureCredential = MagicMock()
    sys.modules.update(
        {
            "azure": azure,
            "azure.ai": azure_ai,
            "azure.ai.projects": azure_projects,
            "azure.ai.projects.models": azure_models,
            "azure.identity": azure_identity,
        }
    )

if find_spec("dotenv") is None:
    dotenv = ModuleType("dotenv")
    dotenv.load_dotenv = MagicMock()
    sys.modules["dotenv"] = dotenv

if find_spec("yaml") is None:
    yaml = ModuleType("yaml")
    yaml.YAMLError = ValueError
    yaml.safe_load = MagicMock()
    sys.modules["yaml"] = yaml

from ai_foundry_agent import agent


class AgentOAuthTests(TestCase):
    def setUp(self):
        agent.allowed_tools = []
        agent.approval_mode = "never"
        agent.logging_enabled = False
        agent.mcp_server_label = "snowflake"
        agent.mcp_server_url = "https://example.test/mcp"
        agent.project_connection_id = "snowflake-oauth"
        agent.project_endpoint = "https://example.test/project"

    @patch.object(agent, "MCPTool")
    @patch.object(agent, "DefaultAzureCredential")
    @patch.object(agent, "AIProjectClient")
    def test_project_init_uses_oauth_project_connection(
        self, project_client_type, credential_type, mcp_tool_type
    ):
        project_client, mcp_tool = agent._project_init()

        project_client_type.assert_called_once_with(
            endpoint=agent.project_endpoint,
            credential=credential_type.return_value,
        )
        mcp_tool_type.assert_called_once_with(
            server_label=agent.mcp_server_label,
            server_url=agent.mcp_server_url,
            require_approval="never",
            project_connection_id=agent.project_connection_id,
        )
        self.assertIs(project_client, project_client_type.return_value)
        self.assertIs(mcp_tool, mcp_tool_type.return_value)

    def test_agent_run_returns_oauth_consent_request(self):
        openai_client = MagicMock()
        openai_client.conversations.create.return_value = SimpleNamespace(id="conversation-1")
        openai_client.conversations.items.list.return_value = []
        openai_client.responses.create.return_value = SimpleNamespace(
            id="response-1",
            status="incomplete",
            output=[
                SimpleNamespace(
                    type="oauth_consent_request",
                    id="consent-1",
                    consent_link="https://example.test/consent",
                )
            ],
        )
        foundry_agent = SimpleNamespace(name="snowflake-agent", id="agent-1")

        result = agent._agent_run(
            openai_client,
            foundry_agent,
            "List my data",
            foundry_agent.name,
        )

        self.assertEqual(
            result["oauth_consent_requests"],
            [
                {
                    "id": "consent-1",
                    "consent_link": "https://example.test/consent",
                }
            ],
        )
        openai_client.responses.create.assert_called_once_with(
            conversation="conversation-1",
            input="List my data",
            extra_body={
                "agent_reference": {
                    "name": foundry_agent.name,
                    "type": "agent_reference",
                }
            },
        )

    def test_agent_run_continues_from_oauth_consent_response(self):
        openai_client = MagicMock()
        openai_client.conversations.retrieve.return_value = SimpleNamespace(
            id="conversation-1"
        )
        openai_client.conversations.items.list.return_value = []
        openai_client.responses.create.return_value = SimpleNamespace(
            id="response-2",
            status="completed",
            output=[],
        )
        foundry_agent = SimpleNamespace(name="snowflake-agent", id="agent-1")

        result = agent._agent_run(
            openai_client,
            foundry_agent,
            "List my data",
            foundry_agent.name,
            thread_id="conversation-1",
            previous_response_id="response-1",
        )

        self.assertEqual(result["oauth_consent_requests"], [])
        openai_client.responses.create.assert_called_once_with(
            previous_response_id="response-1",
            input="List my data",
            extra_body={
                "agent_reference": {
                    "name": foundry_agent.name,
                    "type": "agent_reference",
                }
            },
        )
