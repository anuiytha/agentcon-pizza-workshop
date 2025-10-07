import os
import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import MessageRole, FilePurpose, FunctionTool, FileSearchTool, ToolSet, McpTool
from tools import calculate_pizza_for_people
from dotenv import load_dotenv
load_dotenv(override=True)

# This client connects your script to the Azure AI Foundry service using the connection string.
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_ENDPOINT"].strip().replace('"',''),
    credential = DefaultAzureCredential()
)
print(f"Uploading files from ./documents ...")

# Upload files
file_ids = [
    project_client.agents.files.upload_and_poll(file_path = os.path.join("./documents", f), purpose = FilePurpose.AGENTS).id
    for f in os.listdir("./documents")
    if os.path.isfile(os.path.join("./documents", f))]
print(f"Uploaded {len(file_ids)} files.")

# Creating a vector store with the uploaded files
vector_store = project_client.agents.vector_stores.create_and_poll(
    data_sources = [],
    name = "contoso-pizza-store_information"
)
print(f"Created vector store, vector store ID: {vector_store.id}")

# Creating a file batch to process the uploaded files
batch = project_client.agents.vector_store_file_batches.create_and_poll(
    vector_store_id = vector_store.id,
    file_ids = file_ids
)

# Create function tool
functions = FunctionTool(functions = {calculate_pizza_for_people})

# Creating a file search tool that can query the vector store
file_search = FileSearchTool(vector_store_ids = [vector_store.id])

# Create MCP Tool for Contoso Pizza
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
    ],
)
mcp_tool.set_approval_mode("never")

# Add all tools to toolset
toolset = ToolSet()
toolset.add(file_search)
toolset.add(functions)
toolset.add(mcp_tool)
project_client.agents.enable_auto_function_calls(toolset)

# This creates a new agent using the GPT-4o model
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="PizzaOrderAgent",
    instructions = open("instructions.txt").read(),
    top_p = 0.7,
    temperature = 0.7,
    toolset=toolset
)
print(f"Created agent with system prompt, ID: {agent.id}")

# Agents interact with Threads
thread = project_client.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

# Chat loop
while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat.")
        break
    
    # Adds a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_input
    )

    # Create and process an agent run with MCP tool resources
    # IMPORTANT: Use .create() instead of .create_and_process() when using MCP tools
    run = project_client.agents.runs.create(
        thread_id=thread.id,
        agent_id=agent.id,
        tool_resources=mcp_tool.resources
    )

    # Wait for completion
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(0.1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
    
    # Check for errors
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
        continue
    
    # Fetch All Messages from the Thread
    messages = project_client.agents.messages.list(thread_id = thread.id)
    first_message = next(iter(messages), None)
    if first_message: 
        print("Agent:", next((item["text"]["value"] for item in first_message.content if item.get("type") == "text"),""))

# Delete agent after exiting the loop
project_client.agents.delete_agent(agent.id)
print(f"Deleted agent, ID: {agent.id}") 