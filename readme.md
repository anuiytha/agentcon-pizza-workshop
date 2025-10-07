# Contoso Pizza Ordering Agent 🍕🤖

https://github.com/user-attachments/assets/f74f6757-e725-47da-b353-dcc784e0abd8


An intelligent AI agent built with Azure AI Foundry that enables natural language pizza ordering with a custom web interface.

## Overview

This project was developed during the AgentCon Washington DC 2025 workshop "Agents of Tomorrow: Building the Next Generation of Intelligence" by Henk Boelman. The agent demonstrates advanced AI capabilities including natural language understanding, tool calling, and external system integration.

## Features

- **Natural Language Processing**: Order pizzas through conversational interactions
- **RAG Implementation**: Retrieval Augmented Generation for grounded responses
- **MCP Integration**: Model Context Protocol for interoperable agent-tool connections
- **Custom Frontend**: User-friendly React-based web interface for seamless ordering experience.
- **Real-time Menu**: Live pizza and topping information via MCP server
- **Order Management**: Place, view, and manage orders through the agent

## Technologies Used

- **Azure AI Foundry**: Core AI agent framework
- **Python**: Backend agent implementation
- **MCP (Model Context Protocol)**: External tool and API integration
- **RAG**: Knowledge grounding and context retrieval
- **Azure AI Agents SDK**: Agent orchestration and management

## Architecture

The agent leverages several key components:
- **System Messages**: Defines agent behavior and personality
- **Tool Calling**: Custom functions for pizza calculations and operations
- **File Search**: Document-based knowledge retrieval
- **MCP Server**: External API integration for menu and order data

## Getting Started

1. Clone the repository
2. Set up your Azure AI Foundry environment
3. Configure your `.env` file with API credentials
4. Install dependencies: `pip install -r requirements.txt`
5. Run the agent: `python agent.py`

## Event

Built at **AgentCon Washington DC 2025** - October 1, 2025  
Microsoft Office, Reston, VA

## Acknowledgments

Workshop led by Henk Boelman as part of the Global AI Agents World Tour.
