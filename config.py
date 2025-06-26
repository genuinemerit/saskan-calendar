"""
{project}/config.py

Configuration settings for the Flask application.
Base class for all environments and specific classes for development, testing, and production.
This type of approach is referred to as an application factory pattern for Flask in that it
uses objects (e.g., classes) to define the configuration settings for the application and
not just a single file.
"""

from datetime import timedelta
import os


class Config:
    """Base configuration class for the Flask application.
    This class handles settings and configurations across all environments.
    It pulls from whichever .env file is loaded in the enviornment in cases where
      the environment variable needs to be evaluated.
    Several config values are set in code only since they're the same in all environments.
    In some cases, values are set here for one environment but not another.
    For example if we don't want to expose the full database URL in the .env file
      in the case of development environments.

    The os.getenv() function is used to retrieve environment variables. If it finds
    the specified variable, it returns its value. If not, it returns a default value.
    """

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SASKAN_KEY", "invalid_key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SASKAN_DATABASE_URL",
        f"sqlite:///{os.path.abspath('./saskan.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Config
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_NAME = "saskan_session"
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "saskan_"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Babel
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


class DevelopmentConfig(Config):
    DEBUG = True
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    SECRET_KEY = os.getenv("SASKAN_KEY", "change_this")
    SQLALCHEMY_DATABASE_URI = os.getenv("SASKAN_DATABASE_URL")


# 🔑 Map the SASKAN_ENV name to a config class
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
