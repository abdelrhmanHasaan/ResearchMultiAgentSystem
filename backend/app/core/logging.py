"""Application-wide logging configuration."""
from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # Quiet down noisy third-party loggers.
    for name in ("httpx", "httpcore", "urllib3", "chromadb"):
        logging.getLogger(name).setLevel(logging.WARNING)
