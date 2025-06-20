import os

class Config:
    """Application configuration settings"""
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5002))
    
    # Upload folder settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_uploads')
    
    # Page size for pagination
    DEFAULT_PAGE_SIZE = 1000