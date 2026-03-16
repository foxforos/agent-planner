import logging
from pathlib import Path

import logger_config


def test_setup_logging_creates_logs_folder_and_is_idempotent(tmp_path, monkeypatch):
    fake_logger_file = tmp_path / "logger_config.py"

    monkeypatch.setattr(logger_config, "__file__", str(fake_logger_file))

    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass

    try:
        first_log_path = logger_config.setup_logging()

        expected_logs_dir = tmp_path / logger_config.LOGS_FOLDER
        expected_log_path = expected_logs_dir / logger_config.LOG_FILE

        assert expected_logs_dir.exists()
        assert expected_logs_dir.is_dir()
        assert Path(first_log_path) == expected_log_path
        assert len(root_logger.handlers) == 1

        second_log_path = logger_config.setup_logging()

        assert Path(second_log_path) == expected_log_path
        assert len(root_logger.handlers) == 1

    finally:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

        for handler in original_handlers:
            root_logger.addHandler(handler)

        root_logger.setLevel(original_level)