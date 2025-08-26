import glob
import os
from .config import Config

def get_image_files(directory=Config.DEFAULT_OUTPUT_DIR):
    """Get all image files from a directory"""
    return sorted(glob.glob(os.path.join(directory, "*.jpg")))

def clear_directory(directory):
    """Clear all files in a directory"""
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def setup_environment():
    """Set up the environment by creating necessary directories"""
    Config.setup_directories()