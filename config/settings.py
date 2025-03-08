import os
import yaml
from dotenv import load_dotenv
import logging

load_dotenv(override=True)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Token not found")

WEBHOOK_MODE = os.getenv("WEBHOOK", "false").strip().lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
PORT = int(os.getenv("PORT", 8000))

BOT_LANGUAGE = os.getenv("BOT_LANGUAGE", "en").strip().lower()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
LANGUAGES_FILE = os.path.join(BASE_DIR, "languages", "languages.yaml")

with open(LANGUAGES_FILE, "r", encoding="utf-8") as file:
    LANGUAGES = yaml.safe_load(file)

def get_translation(key: str, language: str = BOT_LANGUAGE) -> str:
    return LANGUAGES.get(language, LANGUAGES["uz"]).get(key, key)

LOGS_DIR = os.path.join(BASE_DIR, "requests") 
LOG_FILE = os.path.join(LOGS_DIR, "request.log")  

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)
