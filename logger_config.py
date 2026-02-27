import os
import logging

from config import LOGS_FOLDER, LOG_FILE, LOG_LEVEL


def setup_logging() -> str:
    """
    Setup logging su file (solo file, no console).
    Ritorna il path del file di log.
    Idempotente: se già configurato, non aggiunge handler duplicati.
    """
    # Root del progetto = cartella dove sta questo file
    project_root = os.path.dirname(os.path.abspath(__file__))

    logs_dir = os.path.join(project_root, LOGS_FOLDER)
    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(logs_dir, LOG_FILE)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Già configurato (evita doppioni)
        return log_path

    # Livello (string -> int)
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)

    return log_path