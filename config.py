"""
Application configuration.
"""
import os


class Config:
    """
    Base configuration class.
    Follows Open/Closed Principle - can be extended for different environments.
    """

    # Flask settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Job runner settings
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # RapidAPI settings for LinkedIn scraper
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '79ed527d4dmsh4cb995852b24aaep1a7e21jsn6249410b641b')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'fresh-linkedin-profile-data.p.rapidapi.com')

    # Model service settings
    MODEL_API_URL = os.getenv('MODEL_API_URL', 'http://localhost:8000/score')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> Config:
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'default')
    return config_by_name.get(env, DevelopmentConfig)
