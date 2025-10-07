import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    MessageRole,
    FilePurpose,
    FunctionTool,
    FileSearchTool,
    ToolSet,
    McpTool
)
from tools import calculate_pizza_for_people

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

# Initialize Azure AI client
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_ENDPOINT"].strip().replace('"', ''),
    credential=DefaultAzureCredential()
)

# Upload files from ./documents
file_ids = [
    project_client.agents.files.upload_and_poll(
        file_path=os.path.join("./documents", f),
        purpose=FilePurpose.AGENTS
    ).id
    for f in os.listdir("./documents")
    if os.path.isfile(os.path.join("./documents", f))
]

# Create vector store
vector_store = project_client.agents.vector_stores.create_and_poll(
    data_sources=[],
    name="contoso-pizza-store_information"
)

# Create file batch
project_client.agents.vector_store_file_batches.create_and_poll(
    vector_store_id=vector_store.id,
    file_ids=file_ids
)

# Create tools
functions = FunctionTool(functions={calculate_pizza_for_people})
file_search = FileSearchTool(vector_store_ids=[vector_store.id])
mcp_tool = McpTool(
    server_label="contoso_pizza",
    server_url="https://ca-pizza-mcp-sc6u2typoxngc.graypond-9d6dd29c.eastus2.azurecontainerapps.io/sse",
    allowed_tools=[
        "get_pizzas",
        "get_pizza_by_id",
        "get_toppings",
        "get_topping_by_id",
        "get_topping_categories",
        "get_orders",
        "get_order_by_id",
        "place_order",
        "delete_order_by_id"
    ]
)
mcp_tool.set_approval_mode("never")

# Assemble toolset
toolset = ToolSet()
toolset.add(file_search)
toolset.add(functions)
toolset.add(mcp_tool)
project_client.agents.enable_auto_function_calls(toolset)

# Create agent
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="PizzaOrderAgent",
    instructions=open("instructions.txt").read(),
    top_p=0.7,
    temperature=0.7,
    toolset=toolset
)

# Create thread
thread = project_client.agents.threads.create()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid or missing JSON payload'}), 400

    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Add user message to thread
    project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_message
    )

    # Create agent run with MCP tool resources
    run = project_client.agents.runs.create(
        thread_id=thread.id,
        agent_id=agent.id,
        tool_resources=mcp_tool.resources
    )

    # Wait for completion
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(0.1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)

    if run.status == "failed":
        return jsonify({'error': f'Run failed: {run.last_error}'}), 500

    # Get agent response
    messages = project_client.agents.messages.list(thread_id=thread.id)
    first_message = next(iter(messages), None)
    if first_message:
        agent_response = next(
            (item["text"]["value"] for item in first_message.content if item.get("type") == "text"),
            "I couldn't generate a response."
        )
        return jsonify({'response': agent_response, 'status': 'success'})
    else:
        return jsonify({'error': 'No response from agent'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'agent_id': agent.id, 'thread_id': thread.id})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
