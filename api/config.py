import os

class Config:
    """Base configuration."""
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/data/videos")
    ALLOWED_EXTENSIONS = {'mp4'}
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://172.19.245.152:30001").split(',')
    DEBUG = False


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
