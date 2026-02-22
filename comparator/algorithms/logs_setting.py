import logging
import os
from pathlib import Path

# Get project root directory (parent of this file's parent)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
LOGS_DIR = BASE_DIR / 'logs'

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

RESET = "\x1b[0m"
COLOR_MAP = {
    logging.DEBUG: "\x1b[32m",
    logging.INFO: "\x1b[34m",
    logging.WARNING: "\x1b[33m",
    logging.ERROR: "\x1b[31m",
    logging.CRITICAL: "\x1b[41m",
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = COLOR_MAP.get(record.levelno, RESET)
        message = super().format(record)
        return f"{color}{message}{RESET}"


def get_logger(
    name: str,
    log_file: str = "app.log",
    level=logging.DEBUG
) -> logging.Logger:
    """
    Get a logger with console and file handlers.
    Log files are stored in the logs/ directory.
    
    Args:
        name: Logger name
        log_file: Log file name (will be stored in logs/ directory)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            ColoredFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        # Store log files in logs/ directory
        log_path = LOGS_DIR / log_file
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
