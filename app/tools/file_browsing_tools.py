"""
Google Drive AI Agent: File Browsing & Metadata
This agent provides tools to interact with Google Drive for browsing files and retrieving metadata.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import datetime

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


# Define the scopes required for Google Drive access
SCOPES = ["https://www.googleapis.com/auth/drive",
  "https://www.googleapis.com/auth/spreadsheets"]

def get_drive_service():
    """Authenticate and return the Google Drive service."""
    creds = None
    # Load credentials from token.pickle if it exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Build the Drive service
    service = build('drive', 'v3', credentials=creds)
    return service

# Define schemas for each tool
class ListFilesInput(BaseModel):
    page_size: int = Field(default=10, description="Maximum number of files to return")
    
class ListFolderFilesInput(BaseModel):
    folder_id: str = Field(..., description="The ID of the folder to list files from")
    page_size: int = Field(default=10, description="Maximum number of files to return")

class SearchFilesInput(BaseModel):
    query: str = Field(..., description="Search query. Can include file name, type, or content keywords")
    page_size: int = Field(default=10, description="Maximum number of files to return")

class GetFileMetadataInput(BaseModel):
    file_id: str = Field(..., description="The ID of the file to get metadata for")

# Define the tools
class ListAllFilesTool(BaseTool):
    name: str = "list_all_files"
    description: str = "Lists all files in Google Drive. Use when you need to get an overview of all files."
    args_schema: type[ListFilesInput] = ListFilesInput
    
    def _run(self, page_size: int = 10) -> str:
        """Lists all files in Google Drive."""
        try:
            service = get_drive_service()
            results = service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, owners, parents)"
            ).execute()
            items = results.get('files', [])
            
            if not items:
                return "No files found in Google Drive."
            
            files_info = []
            for item in items:
                file_type = item.get('mimeType', 'Unknown type')
                modified_time = item.get('modifiedTime', 'Unknown')
                if modified_time != 'Unknown':
                    # Convert to a more readable format
                    modified_time = datetime.datetime.fromisoformat(modified_time.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                
                owner = "Unknown"
                if 'owners' in item and item['owners']:
                    owner = item['owners'][0].get('displayName', 'Unknown')
                
                size = item.get('size', 'Unknown')
                if size != 'Unknown':
                    # Convert size to a readable format
                    size = f"{int(size) / 1024:.2f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.2f} MB"
                
                files_info.append({
                    'id': item['id'],
                    'name': item['name'],
                    'type': file_type,
                    'modified': modified_time,
                    'owner': owner,
                    'size': size
                })
            
            # Format the output
            output = "Files in Google Drive:\n\n"
            for idx, file in enumerate(files_info, 1):
                output += f"{idx}. {file['name']} ({file['type']})\n"
                output += f"   ID: {file['id']}\n"
                output += f"   Modified: {file['modified']}\n"
                output += f"   Owner: {file['owner']}\n"
                output += f"   Size: {file['size']}\n\n"
            
            return output
        
        except Exception as e:
            return f"Error listing files: {str(e)}"

class ListFolderFilesTool(BaseTool):
    name: str = "list_folder_files"
    description: str = "Lists files in a specific folder in Google Drive. Use when you need to explore the contents of a particular folder."
    args_schema: type[ListFolderFilesInput] = ListFolderFilesInput
    
    def _run(self, folder_id: str, page_size: int = 10) -> str:
        """Lists files in a specific folder in Google Drive."""
        try:
            service = get_drive_service()
            query = f"'{folder_id}' in parents"
            results = service.files().list(
                q=query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, owners)"
            ).execute()
            items = results.get('files', [])
            
            if not items:
                # First verify that the folder exists
                try:
                    folder = service.files().get(fileId=folder_id).execute()
                    return f"No files found in folder '{folder['name']}'."
                except:
                    return f"Folder with ID '{folder_id}' not found or inaccessible."
            
            files_info = []
            for item in items:
                file_type = item.get('mimeType', 'Unknown type')
                modified_time = item.get('modifiedTime', 'Unknown')
                if modified_time != 'Unknown':
                    modified_time = datetime.datetime.fromisoformat(modified_time.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                
                owner = "Unknown"
                if 'owners' in item and item['owners']:
                    owner = item['owners'][0].get('displayName', 'Unknown')
                
                size = item.get('size', 'Unknown')
                if size != 'Unknown':
                    size = f"{int(size) / 1024:.2f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.2f} MB"
                
                files_info.append({
                    'id': item['id'],
                    'name': item['name'],
                    'type': file_type,
                    'modified': modified_time,
                    'owner': owner,
                    'size': size
                })
            
            # Get folder name for better output
            try:
                folder = service.files().get(fileId=folder_id, fields="name").execute()
                folder_name = folder.get('name', 'Unknown folder')
            except:
                folder_name = "Folder"
            
            # Format the output
            output = f"Files in '{folder_name}' (ID: {folder_id}):\n\n"
            for idx, file in enumerate(files_info, 1):
                output += f"{idx}. {file['name']} ({file['type']})\n"
                output += f"   ID: {file['id']}\n"
                output += f"   Modified: {file['modified']}\n"
                output += f"   Owner: {file['owner']}\n"
                output += f"   Size: {file['size']}\n\n"
            
            return output
        
        except Exception as e:
            return f"Error listing folder files: {str(e)}"

class SearchFilesTool(BaseTool):
    name: str = "search_files"
    description: str = "Searches for specific files in Google Drive Searches for files by name, file type(pdf, document, docs, sheet, folder etc..), or content. Use when looking for specific files."
    args_schema: type[SearchFilesInput] = SearchFilesInput
    
    def _run(self, query: str, page_size: int = 10) -> str:
        """Searches for files in Google Drive by name, file type(or file extension), or content keywords."""
        try:
            service = get_drive_service()
            
            # Handle common file type searches more intuitively
            if query.lower() in ['document', 'doc', 'docs']:
                search_query = "mimeType = 'application/vnd.google-apps.document'"
            elif query.lower() in ['spreadsheet', 'sheet', 'sheets']:
                search_query = "mimeType = 'application/vnd.google-apps.spreadsheet'"
            elif query.lower() in ['presentation', 'slides']:
                search_query = "mimeType = 'application/vnd.google-apps.presentation'"
            elif query.lower() in ['pdf']:
                search_query = "mimeType = 'application/pdf'"
            elif query.lower() in ['folder', 'directory']:
                search_query = "mimeType = 'application/vnd.google-apps.folder'"
            else:
                
                words = query.split()
                name_terms = [f"name contains '{word}'" for word in words]
                content_terms = [f"fullText contains '{word}'" for word in words]
                
                name_query = " or ".join(name_terms)
                content_query = " or ".join(content_terms)
                search_query = f"({name_query}) and ({content_query})"
            
            results = service.files().list(
                q=search_query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, owners, parents)"
            ).execute()
            
            items = results.get('files', [])
            
            if not items:
                return f"No files found matching '{query}'."
            
            files_info = []
            for item in items:
                file_type = item.get('mimeType', 'Unknown type')
                # Convert Google Drive mime types to more readable formats
                if file_type == 'application/vnd.google-apps.document':
                    file_type = 'Google Doc'
                elif file_type == 'application/vnd.google-apps.spreadsheet':
                    file_type = 'Google Sheet'
                elif file_type == 'application/vnd.google-apps.presentation':
                    file_type = 'Google Slides'
                elif file_type == 'application/vnd.google-apps.folder':
                    file_type = 'Folder'
                    
                modified_time = item.get('modifiedTime', 'Unknown')
                if modified_time != 'Unknown':
                    modified_time = datetime.datetime.fromisoformat(modified_time.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                
                owner = "Unknown"
                if 'owners' in item and item['owners']:
                    owner = item['owners'][0].get('displayName', 'Unknown')
                
                size = item.get('size', 'Unknown')
                if size != 'Unknown':
                    size = f"{int(size) / 1024:.2f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.2f} MB"
                else:
                    if file_type == 'Folder':
                        size = 'N/A'
                
                files_info.append({
                    'id': item['id'],
                    'name': item['name'],
                    'type': file_type,
                    'modified': modified_time,
                    'owner': owner,
                    'size': size
                })
            
            # Format the output
            output = f"Search results for '{query}':\n\n"
            for idx, file in enumerate(files_info, 1):
                output += f"{idx}. {file['name']} ({file['type']})\n"
                output += f"   ID: {file['id']}\n"
                output += f"   Modified: {file['modified']}\n"
                output += f"   Owner: {file['owner']}\n"
                output += f"   Size: {file['size']}\n\n"
            
            return output
        
        except Exception as e:
            return f"Error searching files: {str(e)}"

class GetFileMetadataTool(BaseTool):
    name: str = "get_file_metadata"
    description: str = "Gets detailed metadata for a specific file in Google Drive. Use when you need comprehensive information about a particular file."
    args_schema: type[GetFileMetadataInput] = GetFileMetadataInput
    
    def _run(self, file_id: str) -> str:
        """Gets detailed metadata for a file."""
        try:
            service = get_drive_service()
            # metadata
            file = service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, description, createdTime, modifiedTime, modifiedByMeTime, viewedByMeTime, "
                       "size, version, webViewLink, iconLink, thumbnailLink, owners, sharingUser, shared, " 
                       "lastModifyingUser, capabilities, permissions, starred, trashed"
            ).execute()
            
            if not file:
                return f"No file found with ID '{file_id}'."
            
            # Process the file data for human-friendly output
            mime_type = file.get('mimeType', 'Unknown type')
            # Convert Google Drive mime types to more readable formats
            file_type = "Unknown type"
            if mime_type == 'application/vnd.google-apps.document':
                file_type = 'Google Doc'
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                file_type = 'Google Sheet'
            elif mime_type == 'application/vnd.google-apps.presentation':
                file_type = 'Google Slides'
            elif mime_type == 'application/vnd.google-apps.folder':
                file_type = 'Folder'
            elif mime_type == 'application/pdf':
                file_type = 'PDF'
            elif 'image/' in mime_type:
                file_type = 'Image'
            elif 'video/' in mime_type:
                file_type = 'Video'
            elif 'audio/' in mime_type:
                file_type = 'Audio'
            elif 'text/' in mime_type:
                file_type = 'Text'
            else:
                file_type = mime_type
            
            # Format timestamps
            created_time = "Unknown"
            if 'createdTime' in file:
                created_time = datetime.datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            
            modified_time = "Unknown"
            if 'modifiedTime' in file:
                modified_time = datetime.datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            
            # Format size
            size = file.get('size', 'Unknown')
            if size != 'Unknown':
                size_int = int(size)
                if size_int < 1024:
                    size = f"{size_int} B"
                elif size_int < 1024 * 1024:
                    size = f"{size_int / 1024:.2f} KB"
                else:
                    size = f"{size_int / (1024 * 1024):.2f} MB"
            
            # Get owner information
            owner = "Unknown"
            if 'owners' in file and file['owners']:
                owner = file['owners'][0].get('displayName', 'Unknown')
                owner_email = file['owners'][0].get('emailAddress', 'Unknown')
                owner = f"{owner} ({owner_email})"
            
            # Last modified by
            last_modifier = "Unknown"
            if 'lastModifyingUser' in file:
                last_modifier = file['lastModifyingUser'].get('displayName', 'Unknown')
                last_modifier_email = file['lastModifyingUser'].get('emailAddress', 'Unknown')
                last_modifier = f"{last_modifier} ({last_modifier_email})"
            
            # Format the output
            output = f"Metadata for '{file['name']}':\n\n"
            output += f"Basic Information:\n"
            output += f"- File ID: {file['id']}\n"
            output += f"- Name: {file['name']}\n"
            output += f"- Type: {file_type} ({mime_type})\n"
            output += f"- Size: {size}\n"
            output += f"- Version: {file.get('version', 'Unknown')}\n\n"
            
            output += f"Timestamps:\n"
            output += f"- Created: {created_time}\n"
            output += f"- Modified: {modified_time}\n"
            if 'viewedByMeTime' in file:
                viewed_time = datetime.datetime.fromisoformat(file['viewedByMeTime'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                output += f"- Last viewed: {viewed_time}\n\n"
            else:
                output += f"- Last viewed: Never or Unknown\n\n"
            
            output += f"Ownership & Sharing:\n"
            output += f"- Owner: {owner}\n"
            output += f"- Last modified by: {last_modifier}\n"
            output += f"- Shared: {'Yes' if file.get('shared', False) else 'No'}\n"
            
            if 'description' in file and file['description']:
                output += f"\nDescription:\n{file['description']}\n"
            
            if 'webViewLink' in file:
                output += f"\nWeb link: {file['webViewLink']}\n"
            
            # Additional flags
            flags = []
            if file.get('starred', False):
                flags.append("Starred")
            if file.get('trashed', False):
                flags.append("In trash")
            
            if flags:
                output += f"\nFlags: {', '.join(flags)}\n"
            
            return output
        
        except Exception as e:
            return f"Error retrieving file metadata: {str(e)}"
        




# functions for new tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_all_files(page_size: int = 10) -> str:
    """
    Lists all files in the user's Google Drive.

    Args:
        page_size (int): The maximum number of files to retrieve. Default is 10.

    Returns:
        str: A formatted string listing file details or an error message.
    """
    try:
        logger.info("Initializing Google Drive service...")
        service = get_drive_service()

        logger.info(f"Fetching up to {page_size} files from Google Drive...")
        results = service.files().list(
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, owners, parents)"
        ).execute()

        items = results.get('files', [])
        if not items:
            logger.info("No files found in Google Drive.")
            return "No files found in Google Drive."

        files_info = []
        for item in items:
            file_type = item.get('mimeType', 'Unknown type')
            modified_time = item.get('modifiedTime', 'Unknown')
            if modified_time != 'Unknown':
                modified_time = datetime.datetime.fromisoformat(
                    modified_time.replace('Z', '+00:00')
                ).strftime('%Y-%m-%d %H:%M:%S')

            owner = "Unknown"
            if 'owners' in item and item['owners']:
                owner = item['owners'][0].get('displayName', 'Unknown')

            size = item.get('size', 'Unknown')
            if size != 'Unknown':
                size = f"{int(size) / 1024:.2f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.2f} MB"

            files_info.append({
                'id': item['id'],
                'name': item['name'],
                'type': file_type,
                'modified': modified_time,
                'owner': owner,
                'size': size
            })

        logger.info(f"{len(files_info)} files retrieved from Google Drive.")
        output = "Files in Google Drive:\n\n"
        for idx, file in enumerate(files_info, 1):
            output += f"{idx}. {file['name']} ({file['type']})\n"
            output += f"   ID: {file['id']}\n"
            output += f"   Modified: {file['modified']}\n"
            output += f"   Owner: {file['owner']}\n"
            output += f"   Size: {file['size']}\n\n"

        return output

    except Exception as e:
        logger.error("Failed to list files from Google Drive.", exc_info=True)
        return f"Error listing files: {str(e)}"



def list_folder_files(folder_id: str, page_size: int = 10) -> str:
    """
    Lists files inside a specific folder in Google Drive.

    Args:
        folder_id (str): The ID of the Google Drive folder.
        page_size (int): The maximum number of files to retrieve. Default is 10.

    Returns:
        str: A formatted string listing the folder's file details or an error message.
    """
    try:
        logger.info(f"Connecting to Google Drive service to list files in folder: {folder_id}")
        service = get_drive_service()
        query = f"'{folder_id}' in parents"

        logger.info(f"Executing file list query for folder ID: {folder_id}")
        results = service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, owners)"
        ).execute()

        items = results.get('files', [])
        logger.info(f"{len(items)} files retrieved.")

        if not items:
            logger.warning("No files found. Verifying folder existence...")
            try:
                folder = service.files().get(fileId=folder_id, fields="name").execute()
                return f"No files found in folder '{folder['name']}'."
            except Exception:
                logger.error(f"Folder with ID {folder_id} not found or inaccessible.")
                return f"Folder with ID '{folder_id}' not found or inaccessible."

        files_info = []
        for item in items:
            file_type = item.get('mimeType', 'Unknown type')
            modified_time = item.get('modifiedTime', 'Unknown')
            if modified_time != 'Unknown':
                modified_time = datetime.datetime.fromisoformat(
                    modified_time.replace('Z', '+00:00')
                ).strftime('%Y-%m-%d %H:%M:%S')

            owner = "Unknown"
            if 'owners' in item and item['owners']:
                owner = item['owners'][0].get('displayName', 'Unknown')

            size = item.get('size', 'Unknown')
            if size != 'Unknown':
                size = f"{int(size) / 1024:.2f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.2f} MB"

            files_info.append({
                'id': item['id'],
                'name': item['name'],
                'type': file_type,
                'modified': modified_time,
                'owner': owner,
                'size': size
            })

        # Try to fetch folder name for a better header
        try:
            folder = service.files().get(fileId=folder_id, fields="name").execute()
            folder_name = folder.get('name', 'Unknown folder')
        except Exception:
            logger.warning("Could not retrieve folder name.")
            folder_name = "Folder"

        output = f"Files in '{folder_name}' (ID: {folder_id}):\n\n"
        for idx, file in enumerate(files_info, 1):
            output += f"{idx}. {file['name']} ({file['type']})\n"
            output += f"   ID: {file['id']}\n"
            output += f"   Modified: {file['modified']}\n"
            output += f"   Owner: {file['owner']}\n"
            output += f"   Size: {file['size']}\n\n"

        return output

    except Exception as e:
        logger.error("Failed to list files in the folder.", exc_info=True)
        return f"Error listing folder files: {str(e)}"
    


def search_files(query: str, page_size: int = 10) -> str:
    """
    Searches for files in Google Drive by name, file type (e.g., pdf, doc, folder), or content keywords.

    Args:
        query (str): The search query or file type.
        page_size (int): Maximum number of files to return. Default is 10.

    Returns:
        str: A formatted string listing the matching files, or an error message.
    """
    try:
        logger.info(f"Initializing Google Drive service for search query: {query}")
        service = get_drive_service()

        # Determine search query
        query_lower = query.lower()
        if query_lower in ['document', 'doc', 'docs']:
            search_query = "mimeType = 'application/vnd.google-apps.document'"
        elif query_lower in ['spreadsheet', 'sheet', 'sheets']:
            search_query = "mimeType = 'application/vnd.google-apps.spreadsheet'"
        elif query_lower in ['presentation', 'slides']:
            search_query = "mimeType = 'application/vnd.google-apps.presentation'"
        elif query_lower in ['pdf']:
            search_query = "mimeType = 'application/pdf'"
        elif query_lower in ['folder', 'directory']:
            search_query = "mimeType = 'application/vnd.google-apps.folder'"
        else:
            words = query.split()
            name_terms = [f"name contains '{word}'" for word in words]
            content_terms = [f"fullText contains '{word}'" for word in words]
            name_query = " or ".join(name_terms)
            content_query = " or ".join(content_terms)
            search_query = f"({name_query}) and ({content_query})"

        logger.info(f"Executing search with query: {search_query}")
        results = service.files().list(
            q=search_query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, owners, parents)"
        ).execute()

        items = results.get('files', [])
        logger.info(f"{len(items)} matching files found.")

        if not items:
            return f"No files found matching '{query}'."

        files_info = []
        for item in items:
            file_type = item.get('mimeType', 'Unknown type')

            # Friendly file type naming
            type_mapping = {
                'application/vnd.google-apps.document': 'Google Doc',
                'application/vnd.google-apps.spreadsheet': 'Google Sheet',
                'application/vnd.google-apps.presentation': 'Google Slides',
                'application/vnd.google-apps.folder': 'Folder'
            }
            file_type = type_mapping.get(file_type, file_type)

            modified_time = item.get('modifiedTime', 'Unknown')
            if modified_time != 'Unknown':
                modified_time = datetime.datetime.fromisoformat(
                    modified_time.replace('Z', '+00:00')
                ).strftime('%Y-%m-%d %H:%M:%S')

            owner = "Unknown"
            if 'owners' in item and item['owners']:
                owner = item['owners'][0].get('displayName', 'Unknown')

            size = item.get('size', 'Unknown')
            if size != 'Unknown':
                size = f"{int(size) / 1024:.2f} KB" if int(size) < 1024 * 1024 else f"{int(size) / (1024 * 1024):.2f} MB"
            elif file_type == 'Folder':
                size = 'N/A'

            files_info.append({
                'id': item['id'],
                'name': item['name'],
                'type': file_type,
                'modified': modified_time,
                'owner': owner,
                'size': size
            })

        # Format output
        output = f"Search results for '{query}':\n\n"
        for idx, file in enumerate(files_info, 1):
            output += f"{idx}. {file['name']} ({file['type']})\n"
            output += f"   ID: {file['id']}\n"
            output += f"   Modified: {file['modified']}\n"
            output += f"   Owner: {file['owner']}\n"
            output += f"   Size: {file['size']}\n\n"

        return output

    except Exception as e:
        logger.error("Error occurred during file search.", exc_info=True)
        return f"Error searching files: {str(e)}"


def get_file_metadata(file_id: str) -> str:
    """
    Retrieves detailed metadata for a specific file in Google Drive.

    Args:
        file_id (str): The ID of the file.

    Returns:
        str: A human-readable string containing file metadata or an error message.
    """
    try:
        logger.info(f"Fetching metadata for file ID: {file_id}")
        service = get_drive_service()
        
        file = service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, description, createdTime, modifiedTime, modifiedByMeTime, viewedByMeTime, "
                   "size, version, webViewLink, iconLink, thumbnailLink, owners, sharingUser, shared, "
                   "lastModifyingUser, capabilities, permissions, starred, trashed"
        ).execute()

        if not file:
            return f"No file found with ID '{file_id}'."

        # Mime type conversion
        mime_type = file.get('mimeType', 'Unknown type')
        type_map = {
            'application/vnd.google-apps.document': 'Google Doc',
            'application/vnd.google-apps.spreadsheet': 'Google Sheet',
            'application/vnd.google-apps.presentation': 'Google Slides',
            'application/vnd.google-apps.folder': 'Folder',
            'application/pdf': 'PDF',
        }
        file_type = type_map.get(mime_type, 
                     'Image' if 'image/' in mime_type else 
                     'Video' if 'video/' in mime_type else 
                     'Audio' if 'audio/' in mime_type else 
                     'Text' if 'text/' in mime_type else mime_type)

        def format_timestamp(timestamp):
            return datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')

        created_time = format_timestamp(file['createdTime']) if 'createdTime' in file else "Unknown"
        modified_time = format_timestamp(file['modifiedTime']) if 'modifiedTime' in file else "Unknown"
        viewed_time = format_timestamp(file['viewedByMeTime']) if 'viewedByMeTime' in file else "Never or Unknown"

        size = file.get('size', 'Unknown')
        if size != 'Unknown':
            size_int = int(size)
            if size_int < 1024:
                size = f"{size_int} B"
            elif size_int < 1024 * 1024:
                size = f"{size_int / 1024:.2f} KB"
            else:
                size = f"{size_int / (1024 * 1024):.2f} MB"

        # Owner
        owner = "Unknown"
        if file.get('owners'):
            owner_data = file['owners'][0]
            owner = f"{owner_data.get('displayName', 'Unknown')} ({owner_data.get('emailAddress', 'Unknown')})"

        # Last modifier
        last_modifier = "Unknown"
        if file.get('lastModifyingUser'):
            mod_user = file['lastModifyingUser']
            last_modifier = f"{mod_user.get('displayName', 'Unknown')} ({mod_user.get('emailAddress', 'Unknown')})"

        # Build output
        output = f"Metadata for '{file['name']}':\n\n"
        output += f"Basic Information:\n"
        output += f"- File ID: {file['id']}\n"
        output += f"- Name: {file['name']}\n"
        output += f"- Type: {file_type} ({mime_type})\n"
        output += f"- Size: {size}\n"
        output += f"- Version: {file.get('version', 'Unknown')}\n\n"

        output += f"Timestamps:\n"
        output += f"- Created: {created_time}\n"
        output += f"- Modified: {modified_time}\n"
        output += f"- Last viewed: {viewed_time}\n\n"

        output += f"Ownership & Sharing:\n"
        output += f"- Owner: {owner}\n"
        output += f"- Last modified by: {last_modifier}\n"
        output += f"- Shared: {'Yes' if file.get('shared', False) else 'No'}\n"

        if file.get('description'):
            output += f"\nDescription:\n{file['description']}\n"

        if file.get('webViewLink'):
            output += f"\nWeb link: {file['webViewLink']}\n"

        flags = []
        if file.get('starred'):
            flags.append("Starred")
        if file.get('trashed'):
            flags.append("In trash")
        if flags:
            output += f"\nFlags: {', '.join(flags)}\n"

        logger.info(f"Successfully retrieved metadata for file '{file['name']}'")

        return output

    except Exception as e:
        logger.error(f"Error retrieving metadata for file ID {file_id}", exc_info=True)
        return f"Error retrieving file metadata: {str(e)}"

