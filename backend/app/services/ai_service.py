import os
import httpx
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.services.anatomy_service import anatomy_service

class AIService:
    SYSTEM_PROMPT = (
        "You are OctSem AI, the expert anatomical and medical education assistant for HumanNova.\n"
        "Your mission is to guide medical students, nursing learners, and health science scholars "
        "through the complex wonders of male and female human anatomy.\n\n"
        "Guidelines:\n"
        "1. Response Structure: Provide clear, structured educational explanations with headings:\n"
        "   - 🩺 **Overview & Classification**\n"
        "   - 📍 **Anatomical Position & Relations**\n"
        "   - ⚙️ **Physiological Function**\n"
        "   - 💡 **Clinical & Surgical Significance** (e.g. pathologies, reflexes, common injuries)\n"
        "2. Context-Aware: If a specific anatomical structure is provided in context, tailor your response directly to it.\n"
        "3. Learning Clarity: Explain complex Latin/Greek terminology, provide mnemonic aids where appropriate, and cite typical anatomical variations.\n"
        "4. Safety: HumanNova is strictly an educational tool. Never provide personal medical diagnoses or drug prescriptions."
    )

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL

    def generate_response_sync(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        api_key = os.getenv("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
        model = os.getenv("OPENROUTER_MODEL", settings.OPENROUTER_MODEL)

        structure_info = None
        if context and context.get("structure_id"):
            structure_info = anatomy_service.get_structure_by_id(context["structure_id"])

        context_str = ""
        if structure_info:
            context_str = (
                f"\n\nCURRENTLY SELECTED 3D STRUCTURE IN ATLAS:\n"
                f"- Name: {structure_info.get('name')}\n"
                f"- System: {structure_info.get('system')}\n"
                f"- Anatomical Layer: {structure_info.get('layer')}\n"
                f"- Standard Location: {structure_info.get('location')}\n"
                f"- Primary Function: {structure_info.get('function')}\n"
                f"- Clinical Notes: {structure_info.get('clinical_notes')}\n"
            )

        if api_key and api_key.strip() and not api_key.startswith("replace_"):
            try:
                import urllib.request
                import json
                headers = {
                    "Authorization": f"Bearer {api_key.strip()}",
                    "HTTP-Referer": "https://humannova.atlas.edu",
                    "X-Title": "HumanNova 3D Atlas",
                    "Content-Type": "application/json"
                }
                payload = json.dumps({
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT + context_str},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 800
                }).encode('utf-8')
                req = urllib.request.Request(f"{self.base_url}/chat/completions", data=payload, headers=headers)
                with urllib.request.urlopen(req, timeout=20.0) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode('utf-8'))
                        answer = data["choices"][0]["message"]["content"]
                        return {
                            "answer": answer,
                            "context_used": context,
                            "mode": "live_ai",
                            "status": "success"
                        }
            except Exception as e:
                print(f"[OctSem AI] OpenRouter API sync error: {e}")

        fallback_answer = self._generate_educational_fallback(message, structure_info)
        return {
            "answer": fallback_answer,
            "context_used": context,
            "mode": "educational_verified",
            "status": "success",
            "notice": "OctSem AI Knowledge Engine (Live OpenRouter key can be added to .env)"
        }

    async def generate_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Refresh API key from settings/env in case it was updated in .env
        api_key = os.getenv("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
        model = os.getenv("OPENROUTER_MODEL", settings.OPENROUTER_MODEL)

        structure_info = None
        if context and context.get("structure_id"):
            structure_info = anatomy_service.get_structure_by_id(context["structure_id"])

        # Format context prompt
        context_str = ""
        if structure_info:
            context_str = (
                f"\n\nCURRENTLY SELECTED 3D STRUCTURE IN ATLAS:\n"
                f"- Name: {structure_info.get('name')}\n"
                f"- System: {structure_info.get('system')}\n"
                f"- Anatomical Layer: {structure_info.get('layer')}\n"
                f"- Standard Location: {structure_info.get('location')}\n"
                f"- Primary Function: {structure_info.get('function')}\n"
                f"- Clinical Notes: {structure_info.get('clinical_notes')}\n"
            )

        # Check if live OpenRouter key is provided
        if api_key and api_key.strip() and not api_key.startswith("replace_"):
            try:
                headers = {
                    "Authorization": f"Bearer {api_key.strip()}",
                    "HTTP-Referer": "https://humannova.atlas.edu",
                    "X-Title": "HumanNova 3D Atlas",
                    "Content-Type": "application/json"
                }
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT + context_str},
                    {"role": "user", "content": message}
                ]
                
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json={
                            "model": model,
                            "messages": messages,
                            "temperature": 0.3,
                            "max_tokens": 800
                        }
                    )
                    
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["choices"][0]["message"]["content"]
                    return {
                        "answer": answer,
                        "context_used": context,
                        "mode": "live_ai",
                        "status": "success"
                    }
            except Exception as e:
                # Log and fallback gracefully
                print(f"[OctSem AI] OpenRouter API call error: {e}. Falling back to knowledge-base answer.")

        # Educational fallback response using verified knowledge base
        fallback_answer = self._generate_educational_fallback(message, structure_info)
        return {
            "answer": fallback_answer,
            "context_used": context,
            "mode": "educational_verified",
            "status": "success",
            "notice": "OctSem AI Knowledge Engine (Live OpenRouter key can be added to .env)"
        }

    def _generate_educational_fallback(self, question: str, structure_info: Optional[Dict[str, Any]]) -> str:
        if structure_info:
            name = structure_info.get('name', 'Anatomical Structure')
            system = structure_info.get('system', 'Human Body')
            loc = structure_info.get('location', 'Anatomical position')
            func = structure_info.get('function', 'Physiological action')
            clin = structure_info.get('clinical_notes', 'Clinical pathology')
            
            return (
                f"### 🩺 **{name}** — {system}\n\n"
                f"**Question Received:** *\"{question}\"*\n\n"
                f"#### 📍 **Anatomical Position & Relations**\n"
                f"{loc}\n\n"
                f"#### ⚙️ **Physiological Function**\n"
                f"{func}\n\n"
                f"#### 💡 **Clinical & Surgical Significance**\n"
                f"{clin}\n\n"
                f"> **Study Tip:** Observe how this structure interacts with adjacent layers on the 3D canvas. "
                f"You can toggle the surrounding **Muscles**, **Veins**, or **Bones** layers to inspect deeper anatomical relations."
            )
        else:
            return (
                f"### 🧠 **OctSem AI Anatomy Guide**\n\n"
                f"**Anatomy Inquiry:** *\"{question}\"*\n\n"
                f"To provide the most targeted anatomical guidance:\n"
                f"1. Click on any organ, muscle belly, bone, or blood vessel in the **HumanNova 3D Atlas** stage.\n"
                f"2. Your selection will instantly load into OctSem AI's active context window.\n"
                f"3. You can ask about its origin, insertion, innervation, blood supply, or clinical relevance!\n\n"
                f"*HumanNova features full 3D interactive models for both male and female human anatomy across 5 segmented layers.*"
            )

ai_service = AIService()
