from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .chat_engine import ChatEngine
import os

# Initialize the FastAPI app
app = FastAPI(title="SynKro Assist API")

# Lazy-initialize ChatEngine to avoid heavy startup and env deps during import (e.g., CI)
chat_engine = None
if os.getenv("BACKEND_EAGER_INIT", "1") == "1":
    chat_engine = ChatEngine()

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow Next.js dev server
    # Add your production frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request and response validation
class ChatRequest(BaseModel):
    query: str
    user_id: str


class ChatResponse(BaseModel):
    answer: str
    source: str


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the SynKro Assist API!"}


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Receives a user query and returns a response from the chatbot.
    """
    global chat_engine
    if chat_engine is None:
        chat_engine = ChatEngine()
    response_data = chat_engine.generate_response(request.query, request.user_id)
    return ChatResponse(**response_data)
