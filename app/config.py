from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DRAFTS_PATH = DATA_DIR / "drafts.jsonl"
EXAMPLES_PATH = DATA_DIR / "examples.jsonl"