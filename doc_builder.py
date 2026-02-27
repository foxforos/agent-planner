# doc_builder.py
import os
from datetime import datetime
from config import DOCS_FOLDER
import logging

logger=logging.getLogger(__name__)

def ensure_docs_folder():
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        logger.info("DOC_BUILDER: docs folder created (path=%s)", DOCS_FOLDER)

def save_markdown(filename, content):
    ensure_docs_folder()
    filepath = os.path.join(DOCS_FOLDER, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("DOC_BUILDER: markdown saved (path=%s)", filepath)
        return filepath
    
    except Exception as e:
        logger.error("DOC_BUILDER: markdown save failed (path=%s err=%s)", filepath, e)
        raise

def save_text(filename, content):
    ensure_docs_folder()
    filepath = os.path.join(DOCS_FOLDER, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("DOC_BUILDER: text saved (path=%s)", filepath)
        return filepath
    
    except Exception as e:
        logger.error("DOC_BUILDER: text saved failed (path=%s err=%s)", filepath, e)
        raise