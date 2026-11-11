import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Load .env file from project root if present
load_dotenv(ROOT_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "HumanNova"
    API_V1_STR: str = "/api"
    
    # OpenRouter API Configuration (kept empty by default per instructions)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-super-vl:free")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # CORS Origin
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")
    
    # Data Paths
    DATA_DIR: Path = BASE_DIR / "app" / "data"
    ANATOMY_DATA_FILE: Path = DATA_DIR / "anatomy.json"
    QUIZ_DATA_FILE: Path = DATA_DIR / "quiz_data.json"
    
    # Static frontend directory
    FRONTEND_DIR: Path = ROOT_DIR / "frontend"

settings = Settings()
