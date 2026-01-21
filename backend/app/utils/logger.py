"""
Logging Configuration for VaccineColdChain
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_level=logging.DEBUG, log_file=None):
    """
    Setup logging configuration

    Args:
        log_level: Logging level
        log_file: Log file path (optional)
    """
    # Create logs directory if not exists
    logs_dir = os.path.join(os.path.dirname(__file__), "../../logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file is None:
        log_file = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5  # 10MB per file
    )
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)

    logging.info("Logging initialized")


def get_logger(name):
    """
    Get logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
