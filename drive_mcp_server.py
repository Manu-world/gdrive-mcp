from mcp.server.fastmcp import FastMCP
from agent import create_drive_agent
from typing import Dict, Any

# Create MCP server
mcp = FastMCP("GoogleDriveAgent")

@mcp.tool()
async def interact_with_drive(query: str) -> str:
    """
    Interact with Google Drive using natural language.
    
    Args:
        query: The user's query about Google Drive operations
        
    Returns:
        str: The agent's response to the query
    """
    try:
        # Create the agent
        agent = create_drive_agent()
        
        # Invoke the agent with the query
        response = agent.invoke({"input": query})
        
        return response['output']
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_available_tools() -> Dict[str, Any]:
    """
    Get information about available tools in the Google Drive agent.
    
    Returns:
        Dict[str, Any]: Information about available tools
    """
    tools = [
        {
            "name": "list_all_files",
            "description": "Lists all files in Google Drive"
        },
        {
            "name": "list_folder_files",
            "description": "Lists files in a specific folder"
        },
        {
            "name": "search_files",
            "description": "Searches for files by name, type(pdf, document, docs, sheet, folder etc..), or content"
        },
        {
            "name": "get_file_metadata",
            "description": "Gets detailed metadata for a specific file"
        },
        {
            "name": "read_file",
            "description": "Reads the content of text-based files"
        },
        {
            "name": "parse_document",
            "description": "Parses a document into sections, paragraphs, or sentences"
        },
        {
            "name": "extract_information",
            "description": "Extracts key information like dates, names, emails, etc."
        },
        {
            "name": "summarize_document",
            "description": "Creates a concise summary of a document"
        },
        {
            "name": "search_in_document",
            "description": "Searches for keywords or phrases within a document"
        },
        {
            "name": "answer_question",
            "description": "Answers specific questions about file contents"
        }
    ]
    
    return {
        "tools": tools,
        "description": "Google Drive Agent with document analysis capabilities"
    }

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio") 