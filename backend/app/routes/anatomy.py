from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from backend.app.services.anatomy_service import anatomy_service

router = APIRouter(prefix="/api/anatomy", tags=["anatomy"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HumanNova Anatomy Engine",
        "version": "1.0.0"
    }

@router.get("/search")
def search_structures(
    q: str = Query("", description="Search anatomical query"),
    model_type: Optional[str] = Query(None, description="male | female | all")
):
    query_str = q if isinstance(q, str) else ""
    m_type = model_type if isinstance(model_type, str) else None
    results = anatomy_service.search_structures(query_str, m_type)
    return {
        "query": query_str,
        "count": len(results),
        "results": results
    }

@router.get("/{model_type}")
def get_model_anatomy(model_type: str):
    if model_type not in ["male", "female", "all"]:
        raise HTTPException(status_code=400, detail="Invalid model_type. Must be 'male', 'female', or 'all'.")
    structures = anatomy_service.get_all_structures(model_type)
    return {
        "model_type": model_type,
        "total_structures": len(structures),
        "structures": structures
    }

@router.get("/{model_type}/structures/{structure_id}")
def get_structure_detail(model_type: str, structure_id: str):
    structure = anatomy_service.get_structure_by_id(structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail=f"Structure '{structure_id}' not found.")
    
    # Check gender match
    gender = structure.get("gender", "both")
    if model_type != "all" and gender != "both" and gender != model_type:
        return {
            "available": False,
            "message": f"Structure '{structure['name']}' is specific to {gender} anatomy and not present in the {model_type} atlas.",
            "structure": structure
        }
        
    return {
        "available": True,
        "structure": structure
    }

@router.get("/structures/individual")
def get_individual_models_catalog():
    return {
        "organs": [
            {"id": "heart", "name": "Heart (Cor)", "model": "organs/heart.glb", "desc": "Cardiac muscle, aortic arch, chambers"},
            {"id": "brain", "name": "Brain (Encephalon)", "model": "organs/brain.glb", "desc": "Cerebrum, cerebellum, brainstem"},
            {"id": "lungs", "name": "Lungs & Trachea", "model": "organs/lungs.glb", "desc": "Left & right pulmonary lobes, trachea"},
            {"id": "liver", "name": "Liver (Hepar)", "model": "organs/liver.glb", "desc": "Right & left lobes, metabolic center"},
            {"id": "stomach", "name": "Stomach (Gaster)", "model": "organs/stomach.glb", "desc": "Curved gastric reservoir"},
            {"id": "kidneys", "name": "Kidneys (Renes)", "model": "organs/kidneys.glb", "desc": "Renal filtration organs"},
            {"id": "uterus", "name": "Female Reproductive", "model": "organs/female_reproductive.glb", "desc": "Uterus, fallopian tubes, ovaries"}
        ],
        "muscles": [
            {"id": "pectoralis_major", "name": "Pectoralis Major", "model": "muscles/pectoralis_major.glb", "desc": "Chest pectoral muscle"},
            {"id": "biceps_brachii", "name": "Biceps Brachii", "model": "muscles/biceps_brachii.glb", "desc": "Anterior arm flexor with tendons"},
            {"id": "rectus_abdominis", "name": "Rectus Abdominis", "model": "muscles/rectus_abdominis.glb", "desc": "Segmented abdominal wall and linea alba"},
            {"id": "quadriceps_femoris", "name": "Quadriceps & Patella", "model": "muscles/quadriceps_femoris.glb", "desc": "Femoral extensors and patellar tendon"}
        ],
        "veins": [
            {"id": "cardiovascular_tree", "name": "Cardiovascular Tree", "model": "veins/cardiovascular_tree.glb", "desc": "Aorta, Vena Cava, Carotids, Femoral vessels"}
        ],
        "bones": [
            {"id": "cranium", "name": "Cranium & Mandible", "model": "bones/cranium.glb", "desc": "Skull dome and jawbone"},
            {"id": "ribcage_spine", "name": "Ribcage & Spine", "model": "bones/ribcage_spine.glb", "desc": "Thoracic cage, sternum, vertebral column"},
            {"id": "pelvis", "name": "Pelvic Girdle", "model": "bones/pelvis.glb", "desc": "Pelvis, ilium, sacrum"}
        ]
    }
