"""Logging service using loguru.

This module provides a pre-configured logger instance using the Loguru library,
with a clean API for logging at different levels.
"""

import sys

from typing import Any, Optional, Union
from pathlib import Path
from loguru import logger


LogLevel = Union[str, int]
HandlerId = int


class LoggerConfig:
    """Configuration class for Logger.

    Attributes:
        level: The minimum log level to record.
        format: The format string for log messages.
        sink: Where logs are written to.
        rotation: When to rotate the log file.
        retention: How long to keep log files.
        compression: How to compress rotated files.
    """

    def __init__(
        self,
        level: LogLevel = "INFO",
        format: str = "{time} | {level} | {message}",
        sink: Any = sys.stderr,
        rotation: Optional[str] = None,
        retention: Optional[str] = None,
        compression: Optional[str] = None,
    ):
        """Initialize LoggerConfig.

        Args:
            level: The minimum log level to record. Defaults to "INFO".
            format: The format string for log messages. Defaults to "{time} | {level} | {message}".
            sink: Where logs are written to. Can be sys.stderr, sys.stdout, or a file path.
                  Defaults to sys.stderr.
            rotation: When to rotate the log file (e.g. "500 MB", "12:00", "1 week").
                      Defaults to None.
            retention: How long to keep log files (e.g. "10 days"). Defaults to None.
            compression: How to compress rotated files (e.g. "zip", "gz"). Defaults to None.
        """
        self.level = level
        self.format = format
        self.sink = sink
        self.rotation = rotation
        self.retention = retention
        self.compression = compression


class Logger:
    """A logger wrapper around loguru.

    This class provides a clean API for logging at different levels,
    with pre-configured settings.
    """

    def __init__(self, config: Optional[LoggerConfig] = None):
        """Initialize Logger.

        Args:
            config: Configuration for the logger. If None, default config is used.
        """
        self._logger = logger
        # Remove default handlers
        self._logger.remove()

        # Use provided config or create default
        self.config = config or LoggerConfig()

        # Prepare kwargs for add method
        kwargs = {}
        # Only pass rotation/retention/compression when the sink is a file path
        if isinstance(self.config.sink, (str, Path)):
            if self.config.rotation:
                kwargs["rotation"] = self.config.rotation
            if self.config.retention:
                kwargs["retention"] = self.config.retention
            if self.config.compression:
                kwargs["compression"] = self.config.compression

        # Add handler with configured settings
        self._handler_id = self._logger.add(
            sink=self.config.sink,
            level=self.config.level,
            format=self.config.format,
            **kwargs,
        )

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message.

        Args:
            message: The message to log.
            **kwargs: Additional context to include in the log.
        """
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message.

        Args:
            message: The message to log.
            **kwargs: Additional context to include in the log.
        """
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message.

        Args:
            message: The message to log.
            **kwargs: Additional context to include in the log.
        """
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message.

        Args:
            message: The message to log.
            **kwargs: Additional context to include in the log.
        """
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message.

        Args:
            message: The message to log.
            **kwargs: Additional context to include in the log.
        """
        self._logger.critical(message, **kwargs)

    def add_handler(
        self,
        sink: Any,
        level: LogLevel = "DEBUG",
        format: Optional[str] = None,
        **kwargs: Any,
    ) -> HandlerId:
        """Add a new log handler.

        Args:
            sink: Where logs are written to. Can be sys.stderr, sys.stdout, or a file path.
            level: The minimum log level to record.
            format: The format string for log messages.
            **kwargs: Additional arguments to pass to loguru.

        Returns:
            The handler ID, which can be used to remove the handler later.
        """
        format_str = format or self.config.format
        return self._logger.add(sink=sink, level=level, format=format_str, **kwargs)

    def remove_handler(self, handler_id: HandlerId) -> None:
        """Remove a log handler.

        Args:
            handler_id: The ID of the handler to remove.
        """
        self._logger.remove(handler_id)

    def set_level(self, level: LogLevel) -> None:
        """Set the minimum log level.

        Args:
            level: The minimum log level to record.
        """
        # Remove existing handler and add a new one with the updated level
        self._logger.remove(self._handler_id)
        self.config.level = level
        self._handler_id = self._logger.add(
            sink=self.config.sink,
            level=self.config.level,
            format=self.config.format,
            rotation=self.config.rotation,
            retention=self.config.retention,
            compression=self.config.compression,
        )


class LoggerFactory:
    """Factory for creating loggers.

    This class provides methods for creating different types of loggers.
    """

    @staticmethod
    def create(
        name: str = "app",
        level: LogLevel = "INFO",
        sink: Any = sys.stderr,
        format: Optional[str] = None,
    ) -> Logger:
        """Create a pre-configured logger.

        Args:
            name: The name of the logger.
            level: The minimum log level to record.
            sink: Where logs are written to.
            format: The format string for log messages.

        Returns:
            A configured Logger instance.
        """
        if format is None:
            format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"

        config = LoggerConfig(
            level=level,
            format=format.replace("{name}", name),
            sink=sink,
        )

        return Logger(config)

    @staticmethod
    def create_file_logger(
        name: str = "app",
        level: LogLevel = "INFO",
        file_path: Union[str, Path] = "logs/app.log",
        format: Optional[str] = None,
        rotation: str = "10 MB",
        retention: str = "1 week",
        compression: str = "zip",
    ) -> Logger:
        """Create a logger that writes to a file.

        Args:
            name: The name of the logger.
            level: The minimum log level to record.
            file_path: The path to the log file.
            format: The format string for log messages.
            rotation: When to rotate the log file.
            retention: How long to keep log files.
            compression: How to compress rotated files.

        Returns:
            A configured Logger instance.
        """
        if format is None:
            format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"

        config = LoggerConfig(
            level=level,
            format=format.replace("{name}", name),
            sink=str(file_path),
            rotation=rotation,
            retention=retention,
            compression=compression,
        )

        return Logger(config)


# let create custom loggers
create_logger = LoggerFactory.create
create_file_logger = LoggerFactory.create_file_logger
