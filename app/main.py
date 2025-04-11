from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.api.webhook import router as webhook_router
from app.service.agent_service import init_agent, close_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_agent()
    print("Agent initialized.")
    yield
    await close_agent()
    print("Agent closed.")

app = FastAPI(title="WhatsApp MCP Bot", lifespan=lifespan)

app.include_router(webhook_router)

@app.get("/")
def root():
    return RedirectResponse(url="/docs")
