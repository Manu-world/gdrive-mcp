from fastapi import APIRouter, Request, Form
from fastapi.responses import Response
from app.service.agent_service import process_message
from app.service.twilio_service import send_whatsapp_message

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request, From: str = Form(...), Body: str = Form(...)):
    incoming_msg = Body
    sender = From
    response_msg = await process_message(incoming_msg)
    send_whatsapp_message(sender, response_msg)
    return Response(status_code=200)
