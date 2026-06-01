"""
logger.py — Rotating file logger + console output.
"""

import logging
import logging.handlers
import os


def setup_logger():
    os.makedirs("logs", exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)-14s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file: 5 MB per file, keep last 7
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/newsbot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
