import logging
import sys

from loguru import logger as _logger
from settings import Settings

settings = Settings()

_LOGGING_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(level=_LOGGING_LEVEL)
logger = _logger
logger.configure(handlers=[{"sink": sys.stderr, "level": _LOGGING_LEVEL}])


__all__ = ["logger", "settings"]
