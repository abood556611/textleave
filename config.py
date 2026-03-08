import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for TextLeaf application"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    
    # Video settings
    DEFAULT_FPS = 30
    PAGE_DURATION = 0.5  # seconds per page
    AVAILABLE_DURATIONS = [5, 10, 15]  # seconds
    AVAILABLE_FPS = [30, 60]
    
    # Resolution settings
    RESOLUTIONS = {
        '9:16': (1080, 1920),  # Vertical (Instagram/TikTok)
        '16:9': (1920, 1080),  # Horizontal
        '1:1': (1080, 1080)    # Square
    }
    
    # Text settings
    MAIN_TEXT_FONT_SIZE = 80
    FILLER_TEXT_FONT_SIZE = 30
    TEXT_COLOR = (0, 0, 0)  # Black
    HIGHLIGHTER_COLOR = (255, 255, 153, 200)  # Yellow with transparency
    
    # Randomization settings
    POSITION_VARIANCE = 5  # pixels
    SIZE_VARIANCE = 0.02   # 2%
    
    # Payment settings
    OXAPAY_API_KEY = os.getenv('OXAPAY_API_KEY', '')
    MONTHLY_PRICE = 5  # USD
    YEARLY_PRICE = 50  # USD
    
    # Support
    WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '+963958917677')
    
    # Watermark settings
    WATERMARK_TEXT = "TextLeaf.com"
    WATERMARK_FONT_SIZE = 40
    WATERMARK_OPACITY = 128  # 0-255
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create necessary directories
        try:
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
            
            # Ensure directories are writable
            os.chmod(Config.UPLOAD_FOLDER, 0o777)
            os.chmod(Config.OUTPUT_FOLDER, 0o777)
        except Exception as e:
            print(f"Warning: Could not set directory permissions: {e}")
