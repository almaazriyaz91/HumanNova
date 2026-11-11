import json
from typing import Dict, Any, List, Optional
from backend.app.config import settings

class AnatomyService:
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._quiz_data: Dict[str, Any] = {}
        self.reload_data()

    def reload_data(self):
        if settings.ANATOMY_DATA_FILE.exists():
            with open(settings.ANATOMY_DATA_FILE, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {"structures": {}}

        if settings.QUIZ_DATA_FILE.exists():
            with open(settings.QUIZ_DATA_FILE, "r", encoding="utf-8") as f:
                self._quiz_data = json.load(f)
        else:
            self._quiz_data = {"quizzes": []}

    def get_all_structures(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        structures = list(self._data.get("structures", {}).values())
        if not model_type or model_type == "all":
            return structures
            
        filtered = []
        for s in structures:
            gender = s.get("gender", "both")
            if gender == "both" or gender == model_type:
                filtered.append(s)
        return filtered

    def get_structure_by_id(self, structure_id: str) -> Optional[Dict[str, Any]]:
        return self._data.get("structures", {}).get(structure_id)

    def search_structures(self, query: str, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if not query:
            return self.get_all_structures(model_type)
            
        q = query.lower().strip()
        candidates = self.get_all_structures(model_type)
        results = []
        for s in candidates:
            name = s.get("name", "").lower()
            system = s.get("system", "").lower()
            desc = s.get("description", "").lower()
            struct_id = s.get("id", "").lower()
            
            score = 0
            if q in name or q == struct_id:
                score += 10
            elif q in system:
                score += 5
            elif q in desc:
                score += 2
                
            if score > 0:
                results.append((score, s))
                
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results]

    def get_quizzes(self, system: Optional[str] = None) -> List[Dict[str, Any]]:
        quizzes = self._quiz_data.get("quizzes", [])
        if not system or system == "all":
            return quizzes
        return [q for q in quizzes if q.get("system", "").lower() == system.lower()]

anatomy_service = AnatomyService()
