from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from app.config import MCP_CONFIG
from langgraph.checkpoint.memory import MemorySaver
import uuid

mcp_client = None
agent = None

async def init_agent():
    global mcp_client, agent
    mcp_client = MultiServerMCPClient(MCP_CONFIG)
    await mcp_client.__aenter__()
    
    model = ChatOpenAI(model="gpt-4o")
    memory = MemorySaver()
    agent = create_react_agent(model, mcp_client.get_tools(), checkpointer=memory)

async def close_agent():
    if mcp_client:
        await mcp_client.__aexit__(None, None, None)



async def process_message(message: str, thread_id: str = None) -> str:
    global agent
    if not agent:
        return "Agent is not initialized."

    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await agent.ainvoke({"messages": message}, config=config)
        if isinstance(result, dict) and "messages" in result:
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    return msg.content
            return "Couldn't generate a proper response."
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# if __name__ == "__main__":
#     import asyncio
#     print("Welcome to DriveAssistant! How can I help you with your Google Drive today?")
#     asyncio.run(init_agent())
    
#     while True:
#         user_input = input("\nYou: ")
#         if user_input.lower() in ['exit', 'quit', 'bye']:
#             print("DriveAssistant: Goodbye!")
#             break
#         try:
#             response = asyncio.run(process_message(user_input, thread_id="1234"))
#             print(f"\nDriveAssistant: {response}")
#         except Exception as e:
#             print(f"\nDriveAssistant: I encountered an error: {str(e)}")