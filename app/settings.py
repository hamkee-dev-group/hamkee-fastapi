from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Project settings.

    Attributes:
        DEBUG (bool): Flag indicating whether debug mode is enabled.
        HOST (str): The host address for the API server.
        PORT (int): The port number for the API server.
        API_PREFIX (str): The prefix for API routes.
        CORS_ALLOW_ALL_ORIGINS (bool): Flag indicating whether to allow all origins for CORS.
        PROJECT_NAME (str): The name of the project.
        PROJECT_VERSION (str): The version of the project.

    Config:
        env_file (str): The name of the environment file.
        env_file_encoding (str): The encoding of the environment file.
        extra (str): The behavior when encountering extra fields on the env_file.
        populate_by_name (bool): Flag indicating whether to populate settings by name.
    """

    DEBUG: bool = False
    HOST: str = Field(alias="API_HOST")
    PORT: int = Field(alias="API_PORT")
    API_PREFIX: str = Field(alias="API_PREFIX", default="/api")
    CORS_ALLOW_ALL_ORIGINS: bool = Field(alias="CORS_ALLOW_ALL_ORIGINS", default=False)
    PROJECT_NAME: str = Field(alias="PROJECT_NAME", default="ResultAPI")
    PROJECT_VERSION: str = Field(alias="PROJECT_VERSION", default="0.0.1")

    class Config:
        env_file = ".result"
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True
