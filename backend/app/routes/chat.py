from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from backend.app.services.ai_service import ai_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500, description="Student's anatomical question")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Active 3D structure context")
    session_id: Optional[str] = Field(default="session_default", description="Browser session token")

class ChatResponse(BaseModel):
    answer: str
    context_used: Optional[Dict[str, Any]] = None
    status: str = "success"
    mode: Optional[str] = "live_ai"
    notice: Optional[str] = None

@router.post("", response_model=ChatResponse)
def ask_octsem_ai(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Question message cannot be blank.")
        
    result = ai_service.generate_response_sync(
        message=req.message.strip(),
        context=req.context,
        session_id=req.session_id
    )
    return ChatResponse(**result)
