from mcp.server.fastmcp import FastMCP
from agent import create_drive_agent
from typing import Dict, Any

from app.tools.file_browsing_tools import get_file_metadata, list_all_files, list_folder_files, search_files
from app.tools.file_content_tools import answer_question, extract_document_information, parse_document_content, read_file_content, search_in_document, summarize_document

# Create MCP server
mcp = FastMCP("GoogleDriveAgent")

# @mcp.tool()
# async def interact_with_drive(query: str) -> str:
#     """
#     Interact with Google Drive using natural language.
    
#     Args:
#         query: The user's query about Google Drive operations
        
#     Returns:
#         str: The agent's response to the query
#     """
#     try:
#         # Create the agent
#         agent = create_drive_agent()
        
#         # Invoke the agent with the query
#         response = agent.invoke({"input": query})
        
#         return response['output']
#     except Exception as e:
#         return f"Error: {str(e)}"

# @mcp.tool()
# async def get_available_tools() -> Dict[str, Any]:
#     """
#     Get information about available tools in the Google Drive agent.
    
#     Returns:
#         Dict[str, Any]: Information about available tools
#     """
#     tools = [
#         {
#             "name": "list_all_files",
#             "description": "Lists all files in Google Drive"
#         },
#         {
#             "name": "list_folder_files",
#             "description": "Lists files in a specific folder"
#         },
#         {
#             "name": "search_files",
#             "description": "Searches for files by name, type(pdf, document, docs, sheet, folder etc..), or content"
#         },
#         {
#             "name": "get_file_metadata",
#             "description": "Gets detailed metadata for a specific file"
#         },
#         {
#             "name": "read_file",
#             "description": "Reads the content of text-based files"
#         },
#         {
#             "name": "parse_document",
#             "description": "Parses a document into sections, paragraphs, or sentences"
#         },
#         {
#             "name": "extract_information",
#             "description": "Extracts key information like dates, names, emails, etc."
#         },
#         {
#             "name": "summarize_document",
#             "description": "Creates a concise summary of a document"
#         },
#         {
#             "name": "search_in_document",
#             "description": "Searches for keywords or phrases within a document"
#         },
#         {
#             "name": "answer_question",
#             "description": "Answers specific questions about file contents"
#         }
#     ]
    
#     return {
#         "tools": tools,
#         "description": "Google Drive Agent with document analysis capabilities"
#     }


@mcp.tool()
async def list_all_files_tool(page_size: int = 10) -> str:
    """
    Lists all files in the user's Google Drive.

    Args:
        page_size (int): The maximum number of files to retrieve. Default is 10.

    Returns:
        str: A formatted string listing file details or an error message.
    """
    return list_all_files(page_size=page_size)


@mcp.tool()
async def list_folder_files_tool(folder_id: str, page_size: int = 10) -> str:
    """
    Lists files inside a specific folder in Google Drive.

    Args:
        folder_id (str): The ID of the Google Drive folder.
        page_size (int): The maximum number of files to retrieve. Default is 10.

    Returns:
        str: A formatted string listing the folder's file details or an error message.
    """
    return list_folder_files(folder_id=folder_id,page_size=page_size)

@mcp.tool()
async def search_files_tool(query: str, page_size: int = 10) -> str:
    """
    Searches for files in Google Drive by name, file type (e.g., pdf, doc, folder), or content keywords.

    Args:
        query (str): The search query or file type.
        page_size (int): Maximum number of files to return. Default is 10.

    Returns:
        str: A formatted string listing the matching files, or an error message.
    """
    return search_files(query=query,page_size=page_size)

@mcp.tool()
async def get_file_metadata_tool(file_id: str) -> str:
    """
    Retrieves detailed metadata for a specific file in Google Drive.

    Args:
        file_id (str): The ID of the file.

    Returns:
        str: A human-readable string containing file metadata or an error message.
    """
    return get_file_metadata(file_id=file_id)


@mcp.tool()
async def read_file_content_tool(file_id: str, max_pages: int = 5) -> str:
    """
    Reads the content of a text-based file in Google Drive.

    Args:
        file_id (str): The ID of the file to read.
        max_pages (int, optional): Max number of pages to read for PDFs. Default is 5.

    Returns:
        str: A human-readable summary with content preview or an error message.
    """
    return read_file_content(file_id=file_id,max_pages=max_pages)


@mcp.tool()
async def parse_document_content_tool(file_id: str, parse_level: str = "sections") -> str:
    """
    Parses a document from Google Drive into sections, paragraphs, or sentences.

    Args:
        file_id (str): The ID of the file to parse.
        parse_level (str): One of "sections", "paragraphs", or "sentences".

    Returns:
        str: A summary of the parsed content or an error message.
    """
    return parse_document_content(file_id=file_id,parse_level=parse_level)


@mcp.tool()
async def extract_document_information_tool(file_id: str, info_types: str = "all") -> str:
    """
    Extracts key information (dates, names, emails, URLs, headers) from a document.

    Args:
        file_id (str): The ID of the document to extract from.
        info_types (str): A comma-separated list or "all".

    Returns:
        str: A formatted summary of the extracted information.
    """
    return extract_document_information(file_id=file_id,info_types=info_types)


@mcp.tool()
async def summarize_document_tool(file_id: str, summary_length: str = "medium") -> str:
    """
    Summarizes the document content based on the specified summary length.
    
    Args:
        file_id (str): ID of the document to summarize.
        summary_length (str): One of "short", "medium", or "long".

    Returns:
        str: A human-readable summary of the document.
    """
    return summarize_document(file_id=file_id,summary_length=summary_length)


@mcp.tool()
async def search_in_document_tool(file_id: str, query: str, case_sensitive: bool = False) -> str:
    """
    Searches for keywords or phrases within a document and returns relevant context with matches.

    Args:
        file_id (str): ID of the document to search.
        query (str): The keyword or phrase to search for.
        case_sensitive (bool): If True, the search will be case-sensitive.

    Returns:
        str: The results of the search, including matches with context and highlighted text.
    """
    return search_in_document(file_id=file_id,query=query,case_sensitive=case_sensitive)

@mcp.tool()
async def answer_question_tool(file_id: str, question: str) -> str:
    """
    Answers a specific question based on the content of the provided file.
    
    Args:
        file_id (str): ID of the document to process.
        question (str): The question to answer based on the document's content.
    
    Returns:
        str: The formatted answer to the question.
    """
    return answer_question(file_id=file_id,question=question)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio") 