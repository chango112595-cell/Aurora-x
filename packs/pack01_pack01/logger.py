#!/usr/bin/env python3
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(str(path))
    if logger.handlers:
        return logger
    handler = RotatingFileHandler(str(path), maxBytes=5 * 1024 * 1024, backupCount=3)
    fmt = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
