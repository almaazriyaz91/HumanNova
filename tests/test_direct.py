import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.anatomy_service import anatomy_service
from backend.app.services.ai_service import ai_service

def test_service():
    print("Testing anatomy service...")
    all_s = anatomy_service.get_all_structures("all")
    print(f"Total structures: {len(all_s)}")
    assert len(all_s) > 30
    
    male_s = anatomy_service.get_all_structures("male")
    print(f"Male structures: {len(male_s)}")
    assert len(male_s) > 30
    
    female_s = anatomy_service.get_all_structures("female")
    print(f"Female structures: {len(female_s)}")
    assert len(female_s) > 30
    
    heart = anatomy_service.get_structure_by_id("heart")
    print(f"Heart: {heart['name']}")
    assert heart is not None
    
    search_res = anatomy_service.search_structures("pectoralis")
    print(f"Search 'pectoralis': found {len(search_res)}")
    assert len(search_res) > 0
    
    quizzes = anatomy_service.get_quizzes()
    print(f"Quizzes: found {len(quizzes)}")
    assert len(quizzes) > 0
    
    print("\nTesting AI service fallback...")
    res = ai_service.generate_response_sync(
        message="Explain the function of the heart",
        context={"structure_id": "heart", "name": "Heart"}
    )
    print("AI Response Status:", res["status"])
    print("AI Answer Preview:", res["answer"][:100], "...")
    assert res["status"] == "success"
    print("\nAll service tests passed successfully!")

if __name__ == "__main__":
    test_service()
