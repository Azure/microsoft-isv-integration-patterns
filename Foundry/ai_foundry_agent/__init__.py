"""
AI Foundry Agent Package

This package provides a simple interface to interact with Azure AI Foundry agents
through the Model Context Protocol (MCP).
"""

from .agent import invoke_agent

__all__ = ['invoke_agent']