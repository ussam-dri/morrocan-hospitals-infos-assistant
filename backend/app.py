from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .chat_service import GeminiChatService
from .config import get_settings

app = FastAPI(title="Chatbot FR/AR propulsé par Gemini")

settings = get_settings()
chat_service = GeminiChatService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    language: str = Field(default=settings.default_language, pattern="^(fr|ar)$")


class ChatResponse(BaseModel):
    answer: str
    suggested_questions: list[str]
    context_used: list[str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": settings.gemini_model}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        result = chat_service.ask(payload.question, payload.language)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(**result)

