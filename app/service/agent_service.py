from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from app.config import MCP_CONFIG

mcp_client = None
agent = None

async def init_agent():
    global mcp_client, agent
    mcp_client = MultiServerMCPClient(MCP_CONFIG)
    await mcp_client.__aenter__()

    model = ChatOpenAI(model="gpt-4o")
    agent = create_react_agent(model, mcp_client.get_tools())

async def close_agent():
    if mcp_client:
        await mcp_client.__aexit__(None, None, None)

async def process_message(message: str) -> str:
    global agent
    if not agent:
        return "Agent is not initialized."

    try:
        result = await agent.ainvoke({"messages": message})
        if isinstance(result, dict) and "messages" in result:
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    return msg.content
            return "Couldn't generate a proper response."
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
