import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.routes.anatomy import health_check, get_model_anatomy, get_structure_detail, search_structures
from backend.app.routes.chat import ask_octsem_ai, ChatRequest
from backend.app.routes.quiz import get_quiz_questions, evaluate_quiz, QuizEvaluationRequest

def test_routes():
    # 1. Health
    h = health_check()
    assert h["status"] == "healthy"
    print("Health check OK")

    # 2. Male Anatomy
    male_res = get_model_anatomy("male")
    assert male_res["model_type"] == "male"
    assert male_res["total_structures"] > 30
    print(f"Male Anatomy OK ({male_res['total_structures']} structures)")

    # 3. Female Anatomy
    female_res = get_model_anatomy("female")
    assert female_res["model_type"] == "female"
    assert female_res["total_structures"] > 30
    print(f"Female Anatomy OK ({female_res['total_structures']} structures)")

    # 4. Structure Detail
    detail = get_structure_detail("male", "heart")
    assert detail["available"] is True
    assert "Heart" in detail["structure"]["name"]
    print("Structure Detail OK")

    # 5. Search
    search_res = search_structures("biceps", "male")
    assert search_res["count"] > 0
    print(f"Search OK ({search_res['count']} matches)")

    # 6. Chat endpoint
    chat_req = ChatRequest(
        message="What are the functions of this organ?",
        context={"structure_id": "heart", "name": "Heart", "system": "Cardiovascular System"},
        session_id="test_sess"
    )
    chat_resp = ask_octsem_ai(chat_req)
    assert chat_resp.status == "success"
    assert "Heart" in chat_resp.answer
    print("Chat Endpoint OK")

    # 7. Quiz questions & evaluation
    q_data = get_quiz_questions()
    assert q_data["count"] > 0
    print(f"Quiz Questions OK ({q_data['count']} questions)")

    eval_req = QuizEvaluationRequest(answers={"q1": 3})
    eval_resp = evaluate_quiz(eval_req)
    assert eval_resp["score"] == 1
    assert eval_resp["percentage"] == 100.0
    print("Quiz Evaluation OK")

    print("\nALL FASTAPI ROUTE TESTS PASSED!")

if __name__ == "__main__":
    test_routes()
