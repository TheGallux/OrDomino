"""
Logger module
"""

import logging
import os
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter that adds colored, structured console output.

    The formatter enriches log records with:
    - Timestamp (HH:MM:SS)
    - Source directory
    - Source filename
    - Function name
    - Log level
    - Message content
    """

    COLORS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[41m",  # red background
        "RESET": "\033[0m",
    }

    def format(self, record):
        """
        Format a log record into a colored string for console output.
        """

        filepath = record.pathname

        directory = os.path.basename(os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        func = record.funcName
        time = datetime.now().strftime("%H:%M:%S")

        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]

        return (
            f"{color}"
            f"[{time}][{directory}][{filename}][{func}] - {record.levelname}"
            f" - {record.getMessage()}"
            f"{reset}"
        )


def get_logger(name: str):
    """
    Create or retrieve a configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    logger.addHandler(handler)

    return logger
