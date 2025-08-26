from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from .config import Config

class LayoutDetector:
    def __init__(self):
        self.model = None
    
    def load_model(self):
        """Load the YOLO model for document layout detection"""
        if self.model is None:
            weight_path = hf_hub_download(
                repo_id=Config.MODEL_REPO_ID,
                filename=Config.MODEL_FILENAME
            )
            self.model = YOLO(weight_path)
        return self.model
    
    def detect_layout(self, image_path, save=True, conf=Config.CONFIDENCE_THRESHOLD):
        """
        Detect layout elements in an image
        
        Args:
            image_path (str): Path to the image
            save (bool): Whether to save detection results
            conf (float): Confidence threshold
            
        Returns:
            list: Detection results
        """
        model = self.load_model()
        results = model.predict(image_path, save=save, conf=conf, 
                               project=Config.DEFAULT_DETECTIONS_DIR)
        return results