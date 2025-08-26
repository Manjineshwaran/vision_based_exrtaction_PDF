import argparse
import os
import time
from src.pdf_processor import PDFProcessor
from src.layout_detector import LayoutDetector
from src.entity_cropper import EntityCropper
from src.utils import get_image_files, clear_directory, setup_environment

def process_pdf(pdf_path, clear_existing=True, progress_callback=None):
    """
    Process a PDF file to extract layout entities page by page
    
    Args:
        pdf_path (str): Path to the PDF file
        clear_existing (bool): Whether to clear existing output directories
        progress_callback (callable): Optional callback function for progress updates
        
    Returns:
        dict: All extracted entities by type with page numbers
    """
    # Setup environment
    setup_environment()
    
    # Clear existing files if requested
    if clear_existing:
        from src.config import Config
        clear_directory(Config.DEFAULT_OUTPUT_DIR)
        clear_directory(Config.DEFAULT_ENTITIES_DIR)
        clear_directory(Config.DEFAULT_DETECTIONS_DIR)
    
    # Initialize components
    pdf_processor = PDFProcessor()
    layout_detector = LayoutDetector()
    entity_cropper = EntityCropper()
    
    # Convert PDF to images one page at a time
    print(f"Processing PDF: {os.path.basename(pdf_path)}")
    
    # Get total number of pages first
    total_pages = pdf_processor.get_page_count(pdf_path)
    print(f"Total pages to process: {total_pages}")
    
    all_entities = {}
    
    # Process each page one by one
    for page_num in range(1, total_pages + 1):
        start_time = time.time()
        print(f"\n=== Processing Page {page_num}/{total_pages} ===")
        
        try:
            # Convert current page to image
            print(f"Converting page {page_num} to image...")
            img_path = pdf_processor.convert_pdf_page_to_image(pdf_path, page_num)
            
            if not img_path or not os.path.exists(img_path):
                print(f"Warning: Failed to convert page {page_num} to image")
                continue
                
            # Detect layout using YOLO
            print("Detecting layout...")
            results = layout_detector.detect_layout(img_path, save=True)
            
            # Crop entities from the current page
            print("Cropping entities...")
            entity_cropper.crop_entities_from_results(img_path, results, page_num)
            
            # Get entities for current page
            page_entities = entity_cropper.get_entities_by_page(page_num)
            
            # Update all entities
            for entity_type, files in page_entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                all_entities[entity_type].extend(files)
            
            # Calculate and print stats for current page
            page_processing_time = time.time() - start_time
            items_count = sum(len(files) for files in page_entities.values())
            print(f"Page {page_num} completed in {page_processing_time:.2f} seconds")
            print(f"Extracted {items_count} items from page {page_num}")
            
            # Call progress callback if provided (for Streamlit)
            if progress_callback:
                progress_callback({
                    'current_page': page_num,
                    'total_pages': total_pages,
                    'items_extracted': items_count,
                    'page_entities': page_entities,
                    'all_entities': all_entities
                })
                
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")
    
    # Print final summary
    print("\n=== FINAL EXTRACTION SUMMARY ===")
    total_items = 0
    for entity_type, files in all_entities.items():
        count = len(files)
        total_items += count
        print(f"{entity_type}: {count} items")
    
    print(f"\nTotal items extracted: {total_items}")
    return all_entities

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document Layout Analysis Pipeline")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--keep-existing", action="store_true", 
                       help="Keep existing output files instead of clearing them")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found.")
        exit(1)
    
    process_pdf(args.pdf_path, clear_existing=not args.keep_existing)