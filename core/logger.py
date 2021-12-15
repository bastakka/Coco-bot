"""Logging module

This module provides access to logging to all modules."""
import logging
import sys
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter

from core.config import get_config

config = get_config()


def get_logger(name):
    """Returns logger formated for both console and file"""
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    file_formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
    )
    console_formatter = ColoredFormatter(
        "%(log_color)s[%(levelname)s] %(name)s: %(message)s%(reset)s"
    )

    file_handler = RotatingFileHandler(
        "logs/logfile.log", maxBytes=(1048576 * 5), backupCount=7, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG if config.debug else logging.WARNING)
    return logger
