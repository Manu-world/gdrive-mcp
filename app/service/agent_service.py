# from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from langchain.agents import AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from app.config import MCP_CONFIG
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.tools import load_mcp_tools

from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
import operator
# mcp_client = None
# agent = None

# async def init_agent():
#     global mcp_client, agent
#     mcp_client = MultiServerMCPClient(MCP_CONFIG)
#     await mcp_client.__aenter__()

#     model = ChatOpenAI(model="gpt-4o")
#     agent = create_react_agent(model, mcp_client.get_tools())

# async def close_agent():
#     if mcp_client:
#         await mcp_client.__aexit__(None, None, None)

# async def process_message(message: str) -> str:
#     global agent
#     if not agent:
#         return "Agent is not initialized."

#     try:
#         result = await agent.ainvoke({"messages": message})
#         if isinstance(result, dict) and "messages" in result:
#             for msg in reversed(result["messages"]):
#                 if isinstance(msg, AIMessage):
#                     return msg.content
#             return "Couldn't generate a proper response."
#         return str(result)
#     except Exception as e:
#         return f"Error: {str(e)}"

from langchain_core.tracers import ConsoleCallbackHandler
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate



async def new_process_message(message):
   try:

    model = ChatOpenAI(model="gpt-4o",api_key=os.getenv("OPENAI_API_KEY"))

    server_params = StdioServerParameters(**MCP_CONFIG["gdrive"])
    

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()


            # Get tools
            tools = await load_mcp_tools(session)
            # print("tools:", tools)

            # input_message = input("You:") 
        

            # Create and run the agent
            agent = create_react_agent(model,tools)

            # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

          
            try:
                agent_response = await agent.ainvoke({"messages":message},{"callbacks": [ConsoleCallbackHandler()]} )
                
            except* Exception as eg:
                print("Grouped exception caught:")
                for sub in eg.exceptions:
                    print(f"Sub-exception: {sub}")
                print("A task failed during agent execution.")

        
            if isinstance(agent_response, dict) and "messages" in agent_response:
                for msg in reversed(agent_response["messages"]):
                    if isinstance(msg, AIMessage):
                        return msg.content
                return "Couldn't generate a proper response."
            
            # Access the intermediate steps
            

        print(str(agent_response))    
        return str(agent_response)


   except Exception as e:
        return f"Error in new process message: {str(e)}"        
   



async def new_agent_process_message(message):
     try:

        model = ChatOpenAI(model="gpt-4o",api_key=os.getenv("OPENAI_API_KEY"))

        server_params = StdioServerParameters(**MCP_CONFIG["gdrive"])
        

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()


                # Get tools
                tools = await load_mcp_tools(session)
                # print("tools:", tools)

                # input_message = input("You:") 
            

                # Create and run the agent
                prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "You are a helpful google drive assistant."),
                    ("human", "{input}"),
                    # Placeholders fill up a **list** of messages
                    ("placeholder", "{agent_scratchpad}"),
                ]
            )


                agent = create_tool_calling_agent(model, tools, prompt)
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

                agent_response = await agent_executor.ainvoke({"input": message})
                            

            print(str(agent_response))    
            return str(agent_response)


     except Exception as e:
        return f"Error in new process message: {str(e)}"        
   




async def main():
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("DriveAssistant: Goodbye!")
            break
        
        try:
            response = await new_agent_process_message(user_input)
            print(response)
            # print(f"\nDriveAssistant: {response['output']}")
        except Exception as e:
            print(f"\nDriveAssistant: I encountered an error: {str(e)}")

asyncio.run(main())   