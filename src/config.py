# import os

# class Config:
#     # Paths
#     POPPLER_PATH = r"D:\\AIDS\\dependent\\Release-25.07.0-0\\poppler-25.07.0\\Library\\bin"
#     MODEL_REPO_ID = "DILHTWD/documentlayoutsegmentation_YOLOv8_ondoclaynet"
#     MODEL_FILENAME = "yolov8x-doclaynet-epoch64-imgsz640-initiallr1e-4-finallr1e-5.pt"
    
#     # Default directories
#     DEFAULT_OUTPUT_DIR = "output_pages"
#     DEFAULT_ENTITIES_DIR = "cropped_entities"
#     DEFAULT_DETECTIONS_DIR = "detections"
    
#     # Model settings
#     CONFIDENCE_THRESHOLD = 0.25
#     IMAGE_SIZE = 640
    
#     @classmethod
#     def setup_directories(cls):
#         """Create necessary directories if they don't exist"""
#         os.makedirs(cls.DEFAULT_OUTPUT_DIR, exist_ok=True)
#         os.makedirs(cls.DEFAULT_ENTITIES_DIR, exist_ok=True)
#         os.makedirs(cls.DEFAULT_DETECTIONS_DIR, exist_ok=True)

import os
import platform

class Config:
    # Model settings
    MODEL_REPO_ID = "DILHTWD/documentlayoutsegmentation_YOLOv8_ondoclaynet"
    MODEL_FILENAME = "yolov8x-doclaynet-epoch64-imgsz640-initiallr1e-4-finallr1e-5.pt"
    
    # Default directories
    DEFAULT_OUTPUT_DIR = "output_pages"
    DEFAULT_ENTITIES_DIR = "cropped_entities"
    DEFAULT_DETECTIONS_DIR = "detections"
    
    # Model settings
    CONFIDENCE_THRESHOLD = 0.25
    IMAGE_SIZE = 640
    
    # Poppler path - handle different environments
    @classmethod
    def get_poppler_path(cls):
        """Get the appropriate poppler path based on the environment"""
        # For Streamlit Cloud/Linux environment
        if os.path.exists('/usr/bin/pdftoppm'):
            return '/usr/bin'
        
        # For Windows development environment
        windows_path = r"D:\\AIDS\\dependent\\Release-25.07.0-0\\poppler-25.07.0\\Library\\bin"
        if os.path.exists(windows_path):
            return windows_path
        
        # For other environments, try to find poppler in PATH
        try:
            import subprocess
            result = subprocess.run(['which', 'pdftoppm'], capture_output=True, text=True)
            if result.returncode == 0:
                return os.path.dirname(result.stdout.strip())
        except:
            pass
            
        # Fallback - return None and let pdf2image handle it
        return None
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.DEFAULT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.DEFAULT_ENTITIES_DIR, exist_ok=True)
        os.makedirs(cls.DEFAULT_DETECTIONS_DIR, exist_ok=True)