"""Settings management for the application.

This module provides a clean interface for accessing application settings
from environment variables with validation and proper defaults.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Environment enum for the application."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class BaseAppSettings(BaseSettings):
    """Base settings class with common configuration.

    This class provides the foundation for all environment-specific
    settings classes, with shared configuration options.

    Attributes:
        DEBUG: Flag indicating whether debug mode is enabled.
        HOST: The host address for the API server.
        PORT: The port number for the API server.
        API_PREFIX: The prefix for API routes.
        CORS_ALLOW_ALL_ORIGINS: Flag indicating whether to allow all origins for CORS.
        PROJECT_NAME: The name of the project.
        PROJECT_VERSION: The version (calendar) of the project.
        ENVIRONMENT: The environment the application is running in.
    """

    DEBUG: bool = False
    HOST: str = Field(default="127.0.0.1", alias="API_HOST")
    PORT: int = Field(default=8000, alias="API_PORT")
    API_PREFIX: str = Field(default="/api", alias="API_PREFIX")
    CORS_ALLOW_ALL_ORIGINS: bool = Field(default=False, alias="CORS_ALLOW_ALL_ORIGINS")
    PROJECT_NAME: str = Field(default="HamkeeFastAPI", alias="PROJECT_NAME")
    PROJECT_VERSION: str = Field(default="2025.01", alias="PROJECT_VERSION")
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT, alias="ENVIRONMENT"
    )

    class Config:
        """Configuration for settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        """Check if environment is development.

        Returns:
            True if environment is development, False otherwise.
        """
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Check if environment is testing.

        Returns:
            True if environment is testing, False otherwise.
        """
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def is_staging(self) -> bool:
        """Check if environment is staging.

        Returns:
            True if environment is staging, False otherwise.
        """
        return self.ENVIRONMENT == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if environment is production.

        Returns:
            True if environment is production, False otherwise.
        """
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def api_url(self) -> str:
        """Get the full API URL.

        Returns:
            The full API URL including host, port and prefix.
        """
        return f"http://{self.HOST}:{self.PORT}{self.API_PREFIX}"

    def as_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary.

        Returns:
            Dictionary representation of settings.
        """
        return self.dict()


class DevelopmentSettings(BaseAppSettings):
    """Settings for development environment.

    Attributes:
        DEBUG: Debug mode is enabled by default.
    """

    DEBUG: bool = True
    CORS_ALLOW_ALL_ORIGINS: bool = True


class TestingSettings(BaseAppSettings):
    """Settings for testing environment.

    Attributes:
        DEBUG: Debug mode is enabled by default.
        TESTING: Flag indicating this is a testing environment.
    """

    DEBUG: bool = True
    TESTING: bool = True
    # Add any test-specific settings here


class StagingSettings(BaseAppSettings):
    """Settings for staging environment.

    This environment is similar to production but with some development features.
    """

    pass  # Add any staging-specific settings here


class ProductionSettings(BaseAppSettings):
    """Settings for production environment.

    Production settings are more restrictive for security.
    """

    DEBUG: bool = False
    CORS_ALLOW_ALL_ORIGINS: bool = False


class SettingsFactory:
    """Factory for creating settings instances.

    This class helps create the appropriate settings object based on the
    current environment, with proper caching for performance.
    """

    _env_settings_map: Dict[Environment, Type[BaseAppSettings]] = {
        Environment.DEVELOPMENT: DevelopmentSettings,
        Environment.TESTING: TestingSettings,
        Environment.STAGING: StagingSettings,
        Environment.PRODUCTION: ProductionSettings,
    }

    @classmethod
    @lru_cache
    def create(
        cls,
        env_file: Optional[Union[str, Path]] = None,
        environment: Optional[str] = None,
    ) -> BaseAppSettings:
        """Create a settings instance for the specified environment.

        Args:
            env_file: Path to the environment file. If None, defaults to ".env".
            environment: Environment name. If None, will be read from the ENVIRONMENT
                variable in the env file.

        Returns:
            Settings instance appropriate for the environment.
        """
        # First load base settings to determine the environment
        base_kwargs = {}
        if env_file:
            base_kwargs["_env_file"] = str(env_file)

        if environment:
            base_kwargs["ENVIRONMENT"] = environment

        base_settings = BaseAppSettings(**base_kwargs)
        environment_enum = base_settings.ENVIRONMENT

        # Now create the environment-specific settings
        settings_class = cls._env_settings_map.get(
            environment_enum, DevelopmentSettings
        )

        return settings_class(**base_kwargs)

    @classmethod
    def get_test_settings(cls, **override_values: Any) -> BaseAppSettings:
        """Create settings for testing with optional overrides.

        This is useful for creating test-specific settings with modified values.

        Args:
            **override_values: Values to override in the test settings.

        Returns:
            TestingSettings instance with overridden values.
        """
        # We don't use the cache for test settings to avoid test interference
        test_settings = TestingSettings(ENVIRONMENT=Environment.TESTING)

        # Override any values specified
        for key, value in override_values.items():
            setattr(test_settings, key, value)

        return test_settings


def get_settings(
    env_file: Optional[Union[str, Path]] = None,
    environment: Optional[str] = None,
) -> BaseAppSettings:
    """Get settings instance for the application.

    This is a convenience function that uses the SettingsFactory to create
    an appropriate settings instance.

    Args:
        env_file: Path to the environment file. If None, defaults to ".env".
        environment: Environment name. If None, will be read from the ENVIRONMENT
            variable in the env file.

    Returns:
        Settings instance appropriate for the environment.
    """
    return SettingsFactory.create(env_file=env_file, environment=environment)
