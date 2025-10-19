import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this config file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")  # Legacy, keeping for reference
FMP_API_KEY = os.getenv("FMP_API_KEY")  # Financial Modeling Prep
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")

# LLM Settings
LLM_MODEL = "gemini-2.5-flash"  # Fast model for analysts and debaters
SUPERVISOR_MODEL = "gemini-2.5-pro"  # Deep thinking model for supervisor
LLM_TEMPERATURE = 0  # Deterministic outputs for analysts
SUPERVISOR_TEMPERATURE = 0.7  # More creative for supervisor synthesis

# Financial Modeling Prep (FMP) Settings
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
FMP_TIMEOUT = 30  # seconds

# Legacy Alpha Vantage Settings (deprecated)
AV_BASE_URL = "https://www.alphavantage.co/query"
AV_TIMEOUT = 30  # seconds

# Output Settings
VERBOSE = True