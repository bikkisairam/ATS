import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    # Core
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    @staticmethod
    def validate():
        missing = []
        if not Config.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")

        if missing:
            raise EnvironmentError(
                f"❌ Missing required environment variables: {', '.join(missing)}"
            )
