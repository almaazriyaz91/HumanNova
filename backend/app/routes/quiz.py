from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.app.services.anatomy_service import anatomy_service

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

class QuizEvaluationRequest(BaseModel):
    answers: Dict[str, int] # question_id -> chosen option index

@router.get("/questions")
def get_quiz_questions(system: Optional[str] = Query(None, description="Filter by anatomical system")):
    sys_str = system if isinstance(system, str) else None
    questions = anatomy_service.get_quizzes(sys_str)
    # Hide correct answers from client in question payload
    client_questions = []
    for q in questions:
        client_questions.append({
            "id": q["id"],
            "system": q["system"],
            "question": q["question"],
            "options": q["options"]
        })
    return {
        "count": len(client_questions),
        "questions": client_questions
    }

@router.post("/evaluate")
def evaluate_quiz(req: QuizEvaluationRequest):
    all_quizzes = {q["id"]: q for q in anatomy_service.get_quizzes()}
    score = 0
    total = len(req.answers)
    details = []
    
    for q_id, chosen_idx in req.answers.items():
        if q_id in all_quizzes:
            q = all_quizzes[q_id]
            is_correct = (chosen_idx == q["correct_answer"])
            if is_correct:
                score += 1
            details.append({
                "id": q_id,
                "question": q["question"],
                "chosen_index": chosen_idx,
                "correct_index": q["correct_answer"],
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })
            
    pct = round((score / max(total, 1)) * 100, 1)
    return {
        "score": score,
        "total": total,
        "percentage": pct,
        "passed": pct >= 70.0,
        "results": details
    }
