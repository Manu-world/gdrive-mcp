import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# OpenAI
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Twilio Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Google Drive MCP Config
# MCP_CONFIG = {
#     "gdrive": {
#         "command": "npx",
#         "args": ["-y", "@isaacphi/mcp-gdrive"],
#         "env": {
#             "CLIENT_ID": os.getenv("GDRIVE_CLIENT_ID"),
#             "CLIENT_SECRET": os.getenv("GDRIVE_CLIENT_SECRET"),
#             "GDRIVE_CREDS_DIR": os.getenv("GDRIVE_CREDS_DIR", "/path/to/config/directory"),
#         },
#     }
# }

MCP_CONFIG = {
    "gdrive": {
        "command": "python",
       "args":["drive_mcp_server.py"],
       "transport": "stdio"   
    }
}
