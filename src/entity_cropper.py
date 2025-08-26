from PIL import Image
import os
import re
from collections import defaultdict
from .config import Config

class EntityCropper:
    def __init__(self, entities_dir=Config.DEFAULT_ENTITIES_DIR):
        self.entities_dir = entities_dir
        self.page_entities = defaultdict(lambda: defaultdict(list))
        os.makedirs(entities_dir, exist_ok=True)
    
    def _get_page_number(self, filename):
        """Extract page number from filename"""
        match = re.search(r'page(\d+)_', filename)
        return int(match.group(1)) if match else 0
    
    def crop_entities_from_results(self, image_path, results, page_no):
        """
        Crop detected entities from an image based on detection results
        
        Args:
            image_path (str): Path to the original image
            results: Detection results from YOLO
            page_no (int): Page number for naming
            
        Returns:
            dict: Dictionary of cropped entities by category for the current page
        """
        img = Image.open(image_path)
        cropped_entities = defaultdict(list)
        
        for r in results:
            if not hasattr(r, 'boxes') or r.boxes is None:
                continue
                
            boxes = r.boxes.xyxy.cpu().numpy()   # [x1, y1, x2, y2]
            classes = r.boxes.cls.cpu().numpy()  # class IDs
            scores = r.boxes.conf.cpu().numpy()  # confidence scores

            for idx, (box, cls, score) in enumerate(zip(boxes, classes, scores), start=1):
                cls_name = r.names[int(cls)]  # e.g., 'table', 'text', 'formula'
                x1, y1, x2, y2 = map(int, box)

                # Skip if the bounding box is invalid
                if x1 >= x2 or y1 >= y2:
                    continue

                try:
                    # Crop region
                    cropped = img.crop((x1, y1, x2, y2))

                    # Make folder for class
                    class_dir = os.path.join(self.entities_dir, cls_name)
                    os.makedirs(class_dir, exist_ok=True)

                    # Save cropped entity
                    out_file = os.path.join(class_dir, f"page{page_no:03d}_{cls_name}_{idx:03d}.jpg")
                    cropped.save(out_file)
                    
                    # Add to results dictionaries
                    cropped_entities[cls_name].append(out_file)
                    self.page_entities[page_no][cls_name].append(out_file)
                    
                    print(f"[PAGE {page_no}] Saved {cls_name} → {out_file}")
                    
                except Exception as e:
                    print(f"Error cropping {cls_name} on page {page_no}: {e}")
        
        return dict(cropped_entities)
    
    def get_entities_by_page(self, page_no):
        """
        Get all entities for a specific page
        
        Args:
            page_no (int): Page number to get entities for
            
        Returns:
            dict: Dictionary of entity types and their file paths for the specified page
        """
        return dict(self.page_entities.get(page_no, {}))
    
    def get_all_entities(self):
        """
        Get all cropped entities organized by type across all pages
        
        Returns:
            dict: Dictionary of entity types and their file paths
        """
        all_entities = defaultdict(list)
        
        # First check our in-memory tracking
        for page_ents in self.page_entities.values():
            for entity_type, files in page_ents.items():
                all_entities[entity_type].extend(files)
        
        # Fallback to filesystem if needed
        if not all_entities and os.path.exists(self.entities_dir):
            for entity_type in os.listdir(self.entities_dir):
                entity_dir = os.path.join(self.entities_dir, entity_type)
                if os.path.isdir(entity_dir):
                    files = [
                        os.path.join(entity_dir, f) 
                        for f in os.listdir(entity_dir) 
                        if f.endswith(('.jpg', '.jpeg', '.png'))
                    ]
                    if files:
                        all_entities[entity_type] = files
        
        return dict(all_entities)