from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Project(BaseModel):
    name: str                    # nome del progetto
    objective: str               # descrizione/obiettivo
    created_at: datetime         # timestamp creazione
    filename: str                # percorso file salvato
    tags: List[str] = []         # opzionale: lista tag
    format: str = "md"           # "md" o "txt"
