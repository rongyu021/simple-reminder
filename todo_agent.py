import os
# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv
#from langchain import hub  # To pull react prompt
from langchain_openai import AzureChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio

load_dotenv()

# Initialize Azure-backed LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    openai_api_version=os.getenv("OPENAI_API_VERSION", "2023-05-15"),
    temperature=0,
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# Define the main function to run the agent
async def main():
    # Define the server parameters for the math server
    python_path = os.getenv("PYTHON_PATH", "python")  # Use the Python path from .env or default to "python"
    server_path=os.getenv("TODO_MCPSERVER_PATH", "mcp_todo_server.py")  # Path to the MCP server script
    
    server_params = StdioServerParameters(
        command=python_path,
        args=[server_path]
    )
    
    #create a MCP client session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()     
            print("Connected to the todo server! 📝")       

            # Get tools
            tools = await load_mcp_tools(session)

            print(f"Loaded tools: {[tool.name for tool in tools]}")

            # Get the ReAct prompt
            #prompt = hub.pull("hwchase17/react")    # Pull the ReAct prompt from LangChain Hub (https://smith.langchain.com/hub/hwchase17/react)

            # Create the ReAct agent
            agent = create_react_agent(llm, tools)

            # Initialize conversation history outside the loop
            conversation_history = []

            while True:
                #create a simple REPL for user input
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Agent: Goodbye! 👋")
                    break
                
                if user_input:
                    # Add user message to history
                    conversation_history.append(("user", user_input))
                    response = await agent.ainvoke({"messages": conversation_history})
                    
                    # Add agent response to history
                    agent_message = response["messages"][-1].content
                    conversation_history.append(("assistant", agent_message))
                    print(f"Agent: {agent_message}")
                        

if __name__ == "__main__":
    asyncio.run(main())