# MCP Server Documentation

This directory contains comprehensive documentation for various Partner Model Context Protocol (MCP) Server implementations that enable AI agents to securely interact with different data services and platforms.

## Overview

Model Context Protocol (MCP) is an open-source standard that allows AI agents to securely connect with business applications and external data systems. This documentation covers different MCP server implementations available in this project.

## Available MCP Server Implementations

### Snowflake MCP Servers

A Model Context Protocol server for interacting with Snowflake Cortex released by Snowflake.

#### 1. Snowflake Managed MCP Server (Recommended)

The Snowflake-managed MCP server is a cloud-native solution that eliminates the need for separate infrastructure deployment. This is the **recommended approach**.

**[Snowflake Managed MCP Server Documentation](./SnowflakeManagedMCPServer.md)**

---

#### 2. Self-Hosted Snowflake MCP Server

A containerized MCP server implementation for custom deployments and advanced use cases. Use this when you need more control over the deployment or have specific customization requirements.

**[Self-Hosted Snowflake MCP Server Documentation](./SnowflakeMCPServer.md)**

---

### MongoDB MCP Server

 A Model Context Protocol server for interacting with MongoDB Databases and MongoDB Atlas released by MongoDB.

**[Self-Hosted MongoDB MCP Server Documentation](./MongoDBMCPServer.md)**

---
