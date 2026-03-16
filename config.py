import os

# ✅ API Key: deve stare nell'ambiente, NON nel codice
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def require_openai_api_key() -> str:
    """
    Ritorna la OPENAI_API_KEY se presente.
    Solleva RuntimeError solo quando una parte del programma prova davvero a usare OpenAI.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY non impostata." "Imposta la variabile d'ambiente OPENAI_API_KEY (o usa un file .env caricato dal tuo launcher).")
    return OPENAI_API_KEY

# Modello (override via env)
MODEL = os.getenv("AGENT_PLANNER_MODEL", "gpt-4.1-mini")

# Cartella documenti (override via env)
DOCS_FOLDER = os.getenv("AGENT_PLANNER_DOCS_FOLDER", "docs")


# ------------------------------
# Logging (built-in)
# ------------------------------

# Cartella log (override via env)
LOGS_FOLDER = os.getenv("AGENT_PLANNER_LOGS_FOLDER", "logs")

# File di log (override via env)
LOG_FILE = os.getenv("AGENT_PLANNER_LOG_FILE", "agent_planner.log")

# Livello di log (override via env) - es: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = os.getenv("AGENT_PLANNER_LOG_LEVEL", "INFO").upper()
