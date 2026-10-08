import os
from pathlib import Path
from typing import List

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "shophelper.db"
ENV_PATH = BASE_DIR / ".env"

def load_env_file(file_path: Path):
    """Simple, zero-dependency .env file parser."""
    if not file_path.exists():
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"Error loading .env file: {e}")

load_env_file(ENV_PATH)

# Available models in priority fallback order
DEFAULT_MODEL_FALLBACK_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]

class Config:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Comma-separated keys or single key
    _raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or ""
    GEMINI_API_KEYS: List[str] = [k.strip() for k in _raw_keys.split(",") if k.strip()]
    
    # Active model and fallback chain
    MODEL_FALLBACK_CHAIN: List[str] = DEFAULT_MODEL_FALLBACK_CHAIN
    DEFAULT_MODEL: str = DEFAULT_MODEL_FALLBACK_CHAIN[0]
    
    # Deal Refresh intervals and constants
    MAX_DEALS_PER_SEARCH: int = 16
    
    @classmethod
    def get_api_keys(cls) -> List[str]:
        return cls.GEMINI_API_KEYS

    @classmethod
    def set_api_keys(cls, keys: List[str]):
        cls.GEMINI_API_KEYS = [k.strip() for k in keys if k.strip()]
        # Persist to .env
        try:
            cls._update_env_key("GEMINI_API_KEYS", ",".join(cls.GEMINI_API_KEYS))
        except Exception as e:
            print(f"Failed to persist keys to .env: {e}")

    @classmethod
    def _update_env_key(cls, key: str, value: str):
        lines = []
        found = False
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{key}="):
                        lines.append(f"{key}={value}\n")
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append(f"{key}={value}\n")
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)

config = Config()
